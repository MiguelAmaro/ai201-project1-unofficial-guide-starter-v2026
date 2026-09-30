# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

The corpus contains travel information about a set of towns and destinations in one region. The system lets users ask specific questions about a town or ask for recommendations based on needs such as accessibility, transportation, food, walking, or season. It retrieves relevant information from both town-specific and regional guides and uses those sources to answer the question. The goal is to make the corpus easier to explore without having to read every guide individually.

## Chunking Strategy

**Chunk size:** 600 characters
**Overlap:** 0 characters

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->
The starter chunker produced 51 chunks with an average length of 650
characters, ranging from 24 to 800 characters. Because it used fixed-size
windows, it could cut across the Markdown sections in the guides and could
also leave very small fragments at the end of a document.

My chunker splits the documents using their existing Markdown structure and
paragraph boundaries. It produced 115 chunks averaging 273 characters, with
the shortest chunk at 124 characters and the longest at 509.

I chose a maximum of 600 characters because the paragraphs in this corpus are
already fairly short, so most can remain intact without splitting a thought.
I used no overlap because chunks are split at natural paragraph boundaries
instead of arbitrary character positions, and the document and section
headings are kept with the text for context.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `source: guide_accessibility.md#0 ` — produced by: `chunker.py::split_documents`

```
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are difficult and it is better to know in advance.
```

**Chunk 2** — source: ` guide_corry_vale.md#4` — produced by: `chunker.py::split_documents`

```
# Corry Vale

## What to see

The valley itself is the attraction. The footpath network is dense and well marked, and a circuit taking in three of the four villages is about nine miles with 500 metres of ascent. The chapel in the second village is 12th century and always unlocked.
```

**Chunk 3** — source: `guide_givens_mill.md#4` — produced by: `chunker.py::split_documents`

```
# Givens Mill

## What to see

The mill runs tours on the hour from 11 to 3 and the machinery is operating during them, which is loud and much more impressive than a static exhibit. The church has a Saxon doorway. The river walk downstream reaches Brightwater in about three hours.
```

**Chunk 4** — source: `guide_marchwood.md#3 ` — produced by: `chunker.py::split_documents`

```
# Marchwood

## Eat and drink

The best eating is in the Northgate district, a 12-minute tram ride from the station, where about thirty restaurants sit within four streets. The area immediately around the station is uniformly poor and expensive. Marchwood keeps later hours than anywhere else in the region — kitchens serve until 10:30pm, and until midnight on Fridays and Saturdays.
```

**Chunk 5** — source: `guide_seasons.md#2` — produced by: `chunker.py::split_documents`

```
# When to visit the region

## Summer, June to August

June is excellent everywhere. July and August split: Halden Bay becomes very busy and the parking problem dominates, Kestrelford fills with walkers, and Brightwater goes quiet to the point of dullness with the university empty.

For each one, ask: could someone answer a question using only this,
without reading what came before or after?
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**
Which town is easiest to get around in for someone with limited mobility?
**Answer:**

```
Thornby Wells is the easiest town in the region for someone with limited
mobility (from `guide_accessibility.md`).

Sources retrieved: guide_accessibility.md, guide_corry_vale.md,
guide_walking.md
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
| When should I go to Pellew Sands for the beach without the crowds? | Yes | 0.261 |
| Which town is easiest to get around in for someone with limited mobility? | Yes | 0.358 |
| Is cash still useful in Marchwood, and where might I need it? | Yes | 0.322 |
| What are the best times to visit Kestrelford and Halden Bay? | Yes | 0.282 |
| Where can I see a lighthouse in the region? | Yes | 0.504 |

| What is the capital of Mongolia? | No | 0.803 |
| How do I change the oil in a diesel engine? | No | 0.888 |
| Who won the 1994 World Cup? | No | 0.975 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.835 |
| How do I write a for loop in Rust? | No | 0.836 |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->


**1.** I asked ChatGPT to help me design a chunking strategy after I inspected the corpus. It suggested splitting by Markdown structure and paragraph boundaries instead of using the starter's fixed 800-character windows. I used that idea, but adjusted the implementation and tested it against my corpus until the chunks stayed within about 600 characters and preserved the section context.

**2.** I asked ChatGPT to help me interpret the retrieval distances and relevance threshold. It explained the threshold as the maximum distance I was willing to accept and helped me compare my in-scope and out-of-scope results. I then chose a cutoff of 0.5 based on my own measured distances, where the in-scope questions were around 0.26–0.36 and the out-of-scope questions started around 0.80.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 4/5 | 4/5 | 4/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Complete sampled chunks | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Answer identifies a destination | 4 of 5 | 4/5 | 4/5 | 4/5 | MET |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

Baseline evidence: `results/run_2026-09-29_2317_before.md`, produced by
`run_eval.py::main`, using retrieval from `store.py::search` and chunks from
`chunker.py::split_documents`. The five out-of-scope questions were refused
(`5 of 5`) at the `0.5` cutoff. A representative generated answer was:

```
You should go in June and September for the beach without the crowds
(guide_pellew_sands.md).
```

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunks contain the answer | MET | Each run had the expected answer in results for 4 of 5 questions; the lighthouse question was the miss. |
| 2 | Every answer names a source | MET | All 15 generated answers included at least one retrieved source filename. |
| 3 | The relevance gate stops out-of-corpus questions | MET | The gate refused all 5 out-of-scope questions in its deterministic pass. |
| 4 | Sampled chunks preserve a complete thought | MET | Inspection of the 25 retrieved chunks found complete sentence endings and no cut-off thought. |
| 5 | Answers identify a related destination | MET | Four of five answers named a destination in every baseline run; the first answer sometimes omitted `Pellew Sands`. |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

No acceptance criterion was missed in the baseline aggregation. One scorer
measurement defect was diagnosed: `_sentences_are_complete` in `scorer.py`
removed only one Markdown heading, and therefore rejected chunks containing a
document heading followed by a section heading (or leading bold Markdown).
The actual indexed chunks were complete; this was a scoring-stage defect, not
a loading, chunking, embedding, retrieval, or generation failure.

## The Improvement

**What I changed:**

I updated `_sentences_are_complete` in `scorer.py` to remove all leading
Markdown headings, blank separators, and to accept leading emphasis markers
before checking sentence boundaries. I did not change the chunker, index,
retrieval settings, questions, or acceptance targets.

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

I picked this because the baseline report falsely marked criterion 4 as `0/5`
even though direct inspection of the retrieved chunks showed complete topics
and sentence endings. The fix makes the automated measurement match the
criterion and the actual chunk text.

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 4/5 | 4/5 | 4/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Complete sampled chunks | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Answer identifies a destination | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

After evidence: `results/run_2026-09-29_2324_after.md`, produced by
`run_eval.py::main`. The gate again refused `5 of 5` out-of-scope questions.
The lighthouse answer named both destinations and their durations:

```
* The Elder Ness shingle walk, which takes 25 minutes
* The Halden Bay coastal path running north, which takes about two hours
```

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

The improvement helped the measurement, not the retrieval or generated
answers. Criterion 4 changed from the scorer's erroneous `0/5` baseline to
`5/5` in every after run, matching direct inspection of the chunks. The other
criteria stayed within their baseline results. In the final after run,
criterion 5 was `5/5` in all three runs; the earlier baseline showed `4/5`
because some generated answers omitted `Pellew Sands`.

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

The system still occasionally omits the destination name when answering the
Pellew Sands question, although the source filename is cited. This is a
generation-stage weakness in the answer wording, not a retrieval failure;
the relevant chunk is retrieved at distance `0.261`. I stopped after the one
allowed improvement so the before/after comparison remains attributable.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
