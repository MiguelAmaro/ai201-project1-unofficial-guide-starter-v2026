import re


def _sentences_are_complete(text):
    """Return whether a chunk begins and ends on a sentence boundary."""
    body = re.sub(r"^(?:#+[^\n]*\n\s*)+", "", text.strip()).strip()
    if not body:
        return False

    return bool(re.match(r"^[*_`A-Z0-9\"'(]", body)) and bool(
        re.search(r"[.!?\)](?:\"|')?$", body)
    )


def _destination_names(results):
    """Find likely place names from the retrieved chunks."""
    names = set()
    for result in results:
        source_name = result.source.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        source_stem = source_name.rsplit(".", 1)[0]
        if source_stem.lower().startswith("guide_"):
            names.add(source_stem[6:].replace("_", " ").lower())

        text = result.text
        for match in re.finditer(
            r"\b[A-Z][a-z]+[ \t]+(?:Bay|Beach|Sands|Wells)\b",
            text,
        ):
            names.add(match.group(0).lower())
    return names


def judge(question, expects, answer, results):
    """Score the acceptance criteria that can be checked from one run."""
    answer_text = answer or ""
    result_text = [result.text for result in results]
    answer_lower = answer_text.lower()

    criteria1 = any(expects.lower() in text.lower() for text in result_text)

    # The generated answer must cite the filename supplied with the evidence.
    criteria2 = any(result.source.lower() in answer_lower for result in results)

    # A retrieved chunk is usable for this criterion only if it does not cut a
    # sentence at either end (Markdown headings are context, not sentence text).
    criteria4 = bool(results) and all(
        _sentences_are_complete(text) for text in result_text
    )

    destinations = _destination_names(results)
    criteria5 = any(destination in answer_lower for destination in destinations)

    return {
        "criteria1": criteria1,
        "criteria2": criteria2,
        "criteria4": criteria4,
        "criteria5": criteria5,
    }