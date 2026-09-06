# Temporal attention: elapsed time inside the prediction

This protocol tests an elapsed-time penalty at a query-to-observation attention readout.

[Read the study](temporal-attention-that-changes-predictions.md)

## Included implementation

Both irregular-time generators now produce targets after the last query gap. Position-only, explicit-age, fixed-decay and learned-decay models receive identical observations; a last-observation baseline and longer-gap shift set make the comparison inspectable. Tests cover reproducible episodes and trainable decay.

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
python3 experiment.py --steps 40
```

The earlier standard-library references have their own self-tests:

```bash
python3 attention_reference.py
```

Bias-only softmax still has the uniform-age-shift cancellation derived in the article. These models also receive explicit age features, which supply an absolute-age path; that distinction is part of the intervention.

## Local result

On switching episodes, learned decay achieved 73.4% accuracy against 71.1% for the last-observation baseline. On periodic episodes it achieved 57.0%, below the last-observation baseline's 74.2%. Learned decay reached 57.8% on the longer-gap switching set. This one-seed run supports checking task dependence and shift sensitivity, not a general recency advantage. Shift gaps are 19, 37 and 83 steps so they do not all alias the twenty-step periodic cycle.

## Files

- [attention_reference.py](attention_reference.py) — Project-local support file.
- [experiment.py](experiment.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [smoke-results.json](smoke-results.json) — Recorded synthetic run; scope and provenance included.
- [temporal-attention-that-changes-predictions.md](temporal-attention-that-changes-predictions.md) — Article.
- [test_experiment.py](test_experiment.py) — Local regression checks.

## Remaining work

The saved pilot is one seed and forty steps. Multi-seed intervals, calibration tuning, periodicity/arrival-shift controls and the full study remain unrun. An observed gain on switching data cannot establish a universal preference for recent evidence.

[Topic index](../README.md) · [Research index](../../README.md)
