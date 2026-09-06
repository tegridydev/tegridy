# Recursive self-correction: when revision helps and when to stop

RSCU tests whether critique changes an answer for a good reason and whether the system selects the right next action: answer, obtain evidence, clarify or acknowledge an unresolved question.

[Read the study](recursive-self-correction-with-uncertainty.md)

## Included implementation

The evaluator now consumes externally scored before/after records, freezes a confidence threshold on development data, rejects overlapping split groups and accounts for one critique round, retrieval evidence and declared cost. Harmful edits stay in net-change and selective-risk results.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

Run the tool or experiment after setup:

```bash
python3 evaluate.py development.jsonl heldout.jsonl
```

The earlier standard-library references have their own self-tests:

```bash
python3 metrics_reference.py
```

Each row needs `id`, `group`, Boolean `before`/`after`, `confidence`, `rounds: 1`, nonnegative `cost` and `action`. A retrieval action also needs a nonempty `evidence` ledger. No qualifying development threshold produces explicit abstention.

## Files

- [evaluate.py](evaluate.py) — Runnable implementation.
- [metrics_reference.py](metrics_reference.py) — Project-local support file.
- [recursive-self-correction-with-uncertainty.md](recursive-self-correction-with-uncertainty.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_evaluate.py](test_evaluate.py) — Local regression checks.

## Remaining work

Answer generation, correctness annotation and a real intervention dataset are external inputs. The evaluator cannot establish that a confidence estimate is calibrated or that self-critique caused an improvement.

[Topic index](../README.md) · [Research index](../../README.md)
