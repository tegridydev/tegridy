# Recursive self-correction: when revision helps and when to stop

RSCU tests whether critique changes an answer for a good reason and whether the system selects the right next action: answer, obtain evidence, clarify or acknowledge an unresolved question.

[Read the study](recursive-self-correction-with-uncertainty.md)

## Included implementation

The evaluator now consumes externally scored before/after records, freezes a confidence threshold on development data, rejects overlapping split groups and accounts for one critique round, retrieval evidence and declared cost. Harmful edits stay in net-change and selective-risk results.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

Run the tool or experiment after setup:

```bash
uv run --no-project --python .venv/bin/python python evaluate.py development.jsonl heldout.jsonl
```

The earlier standard-library references have their own self-tests:

```bash
uv run --no-project --python .venv/bin/python python metrics_reference.py
```

Each row needs `id`, `group`, Boolean `before`/`after`, `confidence`, `rounds: 1`, nonnegative `cost` and `action`. A retrieval action also needs a nonempty `evidence` ledger. No qualifying development threshold produces explicit abstention.

## Files

- [evaluate.py](evaluate.py) — Runnable implementation.
- [metrics_reference.py](metrics_reference.py) — Project-local support file.
- [recursive-self-correction-with-uncertainty.md](recursive-self-correction-with-uncertainty.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_evaluate.py](test_evaluate.py) — Local regression checks.

## Remaining work

The bounded CPU adapter generates answers with a pinned GPT-Neo checkpoint and scores arithmetic responses with exact labels. Its strict prompt/stopping setup failed the baseline; a suitable competent-model intervention dataset remains necessary. The evaluator cannot establish that a confidence estimate is calibrated or that self-critique caused an improvement.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study recursive-self-correction-with-uncertainty --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The strict prompt-and-stopping configuration scored zero before revision, after revision and under independent sampling. Saved greedy responses commonly terminated on an initial newline. This is a failed baseline configuration, not evidence that a capable arithmetic model cannot self-correct; the run cannot distinguish useful from harmful revisions.

See the [article](recursive-self-correction-with-uncertainty.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
