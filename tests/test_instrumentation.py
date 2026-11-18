import contextlib
from datetime import datetime
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import app
import config
import gate
import generate
import serve
import store


class InstrumentationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.log_path = root / "logs" / "runs.jsonl"
        self.enterContext(patch.object(app, "__file__", str(root / "app.py")))
        self.enterContext(patch.object(config, "CACHE_DIR", root / "cache"))
        self.enterContext(patch.object(config, "CACHE_ENABLED", True))
        self.enterContext(patch.object(generate, "_call_times", []))
        self.enterContext(patch.object(generate, "_session_calls", 0))
        self.enterContext(patch.object(generate, "_session_prompt_tokens", 0))
        self.enterContext(patch.object(generate, "_session_output_tokens", 0))
        self.enterContext(patch.object(generate, "_cache_hits", 0))

    def records(self):
        return [
            json.loads(line)
            for line in self.log_path.read_text(encoding="utf-8").splitlines()
        ]

    def test_answered_then_cached_query_append_one_record_each(self):
        result = SimpleNamespace(source="guide.md", text="Context", distance=0.2)
        response = SimpleNamespace(
            text="Grounded answer",
            usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=4),
        )
        client = SimpleNamespace(
            models=SimpleNamespace(generate_content=lambda **kwargs: response)
        )
        with patch.object(store, "search", return_value=[result]), patch.object(
            generate, "_get_client", return_value=client
        ), contextlib.redirect_stdout(io.StringIO()):
            answer = app._ask_one("Question?", "city_guides", "v2", None, 0.5)
            first = self.log_path.read_text(encoding="utf-8")
            answer_again = app._ask_one("Question?", "city_guides", "v2", None, 0.5)

        self.assertEqual(answer, "Grounded answer")
        self.assertEqual(answer_again, answer)
        self.assertTrue(self.log_path.read_text(encoding="utf-8").startswith(first))
        records = self.records()
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertEqual(record["status"], "answered")
            self.assertEqual(record["answer"], answer)
            self.assertEqual(record["corpus"], "city_guides")
            self.assertEqual(record["variant"], "v2")
            self.assertEqual(record["sources"], ["guide.md"])
            self.assertEqual(record["best_distance"], 0.2)
            self.assertEqual(record["threshold"], 0.5)
            self.assertIsNone(record["error_type"])
            self.assertGreaterEqual(record["duration_ms"], 0)
            self.assertIsNotNone(datetime.fromisoformat(record["timestamp_utc"]).utcoffset())
        self.assertEqual(
            [(r["cache_hit"], r["input_tokens"], r["output_tokens"]) for r in records],
            [(False, 12, 4), (True, 0, 0)],
        )

    def test_refusal_records_retrieved_sources_and_empty_retrieval(self):
        result = SimpleNamespace(source="far.md", text="Context", distance=0.9)
        with patch.object(store, "search", side_effect=[[result], []]):
            first, _ = app.instrumented_ask("Far?", threshold=0.5)
            second, _ = app.instrumented_ask("Nothing?", threshold=0.5)
        self.assertEqual(first["answer"], gate.REFUSAL)
        self.assertEqual(first["sources"], [])
        self.assertTrue(second["refused"])
        records = self.records()
        self.assertEqual(len(records), 2)
        self.assertEqual([r["status"] for r in records], ["refused", "refused"])
        self.assertEqual(records[0]["sources"], ["far.md"])
        self.assertEqual(records[0]["best_distance"], 0.9)
        self.assertEqual(records[1]["sources"], [])
        self.assertIsNone(records[1]["best_distance"])
        self.assertIsNone(records[0]["cache_hit"])
        self.assertIsNone(records[0]["input_tokens"])

    def test_exception_is_logged_once_and_propagates(self):
        result = SimpleNamespace(source="guide.md", text="Context", distance=0.2)
        with patch.object(store, "search", return_value=[result]), patch.object(
            generate, "_get_client", side_effect=ValueError("private details")
        ):
            with self.assertRaisesRegex(ValueError, "private details"):
                app.instrumented_ask("Question?", threshold=0.5)
        records = self.records()
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["status"], "error")
        self.assertEqual(record["error_type"], "ValueError")
        self.assertIsNone(record["answer"])
        self.assertEqual(record["sources"], ["guide.md"])
        self.assertEqual(record["best_distance"], 0.2)
        self.assertGreaterEqual(record["duration_ms"], 0)
        self.assertNotIn("private details", self.log_path.read_text(encoding="utf-8"))

    def test_ask_one_logs_and_propagates_pipeline_exception(self):
        question = "What happens when the pipeline fails?"
        with patch.object(
            app, "ask_pipeline", side_effect=RuntimeError("simulated pipeline failure")
        ) as pipeline:
            with self.assertRaisesRegex(RuntimeError, "^simulated pipeline failure$"):
                app._ask_one(question, "city_guides", "default", None, None)

        pipeline.assert_called_once()
        records = self.records()
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["status"], "error")
        self.assertEqual(record["error_type"], "RuntimeError")
        self.assertEqual(record["question"], question)
        self.assertIn(type(record["duration_ms"]), (int, float))
        self.assertGreaterEqual(record["duration_ms"], 0)
        self.assertIsNone(record["answer"])

    def test_missing_token_metadata_is_unknown(self):
        result = SimpleNamespace(source="guide.md", text="Context", distance=0.2)
        response = SimpleNamespace(
            text="Answer", usage_metadata=SimpleNamespace(prompt_token_count=7)
        )
        client = SimpleNamespace(
            models=SimpleNamespace(generate_content=lambda **kwargs: response)
        )
        with patch.object(store, "search", return_value=[result]), patch.object(
            generate, "_get_client", return_value=client
        ):
            app.instrumented_ask("Question?")
        record = self.records()[0]
        self.assertEqual(record["input_tokens"], 7)
        self.assertIsNone(record["output_tokens"])
        self.assertFalse(record["cache_hit"])

    def test_timer_stops_before_log_writing(self):
        append_run = app._append_run
        with patch.object(store, "search", return_value=[]), patch.object(
            app.time, "perf_counter", side_effect=[10.0, 10.125]
        ) as clock:
            def append_after_timing(record):
                self.assertEqual(clock.call_count, 2)
                append_run(record)

            with patch.object(app, "_append_run", side_effect=append_after_timing):
                _, duration_ms = app.instrumented_ask("Question?")

        self.assertEqual(duration_ms, 125.0)
        self.assertEqual(self.records()[0]["duration_ms"], 125.0)

    def test_web_request_logs_once_and_invalid_request_does_not_log(self):
        result = SimpleNamespace(source="far.md", text="Context", distance=0.9)
        client = serve.app.test_client()
        with patch.object(store, "search", return_value=[result]):
            invalid = client.post("/ask", json={})
            self.assertEqual(invalid.status_code, 400)
            self.assertFalse(self.log_path.exists())
            response = client.post("/ask", json={"question": "Far?"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["refused"])
        self.assertEqual(len(self.records()), 1)

    def test_web_pipeline_error_is_logged_once(self):
        with patch.object(store, "search", side_effect=ValueError("failure")):
            response = serve.app.test_client().post("/ask", json={"question": "Q?"})
        self.assertEqual(response.status_code, 500)
        records = self.records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["status"], "error")
        self.assertEqual(records[0]["error_type"], "ValueError")
        self.assertIsNone(records[0]["best_distance"])

    def test_logging_failure_does_not_mask_pipeline_exception(self):
        with patch.object(store, "search", side_effect=ValueError("original")), patch.object(
            app, "_append_run", side_effect=OSError("disk")
        ), contextlib.redirect_stderr(io.StringIO()) as stderr:
            with self.assertRaisesRegex(ValueError, "original"):
                app.instrumented_ask("Question?")
        self.assertIn("Audit log write failed: OSError", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
