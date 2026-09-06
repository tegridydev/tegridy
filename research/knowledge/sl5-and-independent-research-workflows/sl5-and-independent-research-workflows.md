# [td] tegridydev | SL5: thread-aware evidence and prediction timelines

*design study and proposed evaluation*

SL5 is my attempt to make technical discussions searchable without flattening away the things that make them evidence: **who said what, what they were replying to, which words were actually quoted and when the statement existed**. The 3D-library stuff is fun, but the first research question is much more boring and more useful.

Does thread-aware retrieval reduce attribution and chronology errors compared with flat retrieval when both systems receive the same metadata and context budget?

## Store discussions as evidence, not loose text

Each message needs an ID, thread ID, author label, timestamp with timezone evidence, source locator, content hash, parent relation and explicit quote spans. Replying to a message and quoting part of it are separate edges.

Predictions are separate annotations with the original quoted span, date, claimed outcome, deadline or resolution rule and uncertainty. Most importantly, the interpretation has to be frozen **before** the outcome is revealed. A vague forecast can stay unresolved; I do not want a timeline getting credit for rewriting yesterday’s statement into whatever happened today.

Generated tags, entities and interpretations remain suggestions until checked. A primer built from the material should keep source quotes distinct from generated explanation and preserve competing explanations rather than smoothing them into one story.

## The first comparison

Start with ten synthetic thread families containing replies, nested quotes, corrections, disagreements and deliberately ambiguous forecasts. Write attribution, chronology and evidence questions before evaluation, then hold out entire thread families rather than splitting quoted copies of the same conversation across development and test.

Compare:

1. flat lexical retrieval;
2. flat semantic retrieval;
3. thread-aware retrieval.

Every condition receives the **same author, date, version and reply metadata**. The only difference is whether thread relationships can influence context selection. That prevents a win from being credited to graph traversal when the real advantage was simply better metadata.

Use the same answerer and token budget. Measure evidence recall, speaker/date accuracy, quotation fidelity, unsupported claims and correct `not resolvable` decisions. Add an oracle-context condition so retrieval failures can be separated from synthesis failures.

RAG and ALCE are obvious prior context for retrieval and citation evaluation. I am not claiming a new retrieval family; I’m testing whether thread structure carries useful evidence that flat ranking loses.

**What would weaken the idea:** if a metadata-matched flat retriever performs equally well, thread traversal does not earn the extra structure for this task.

## Predictions and the writing workflow

A useful side experiment is a **prediction ambiguity ledger**. Record multiple reasonable interpretations before the outcome is known, then compare them with retrospective interpretation. This makes hindsight drift measurable instead of philosophical.

Another is a disagreement-first primer that presents two competing explanations with their passages, then checks whether readers remember the limits of each position better than after a single smooth summary.

For the broader independent-research workflow, I’d keep the evaluation separate: alternate ordinary notes and a claim/evidence ledger across a handful of small writing tasks and measure citation errors, time to recover evidence and revisions caused by contradictory sources. That would be a feasibility study for one researcher, not a claim about research productivity in general.

The immediate target remains tiny: resolve five questions over ten messages correctly in a text interface before building spatial navigation, historical personas or anything else that makes the demo look cooler than the evidence system underneath it.

## What exists locally

A ten-message thread fixture now resolves nested quotes to the original author/span, retains timestamp correction history and rejects mixed or cyclic quote attribution. Forecast resolution requires a pre-outcome interpretation and leaves two vague forecasts unresolvable.

Start with [thread.py](thread.py); the [module README](README.md) lists setup, commands and every supporting file.

The `Thread` API stores messages and quote edges; `Forecast` freezes target, deadline and ambiguity. Tests ask five exact-span attribution questions and resolve two ambiguous forecasts without hindsight.

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
