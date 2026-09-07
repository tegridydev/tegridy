# Temporal attention: elapsed time inside the prediction

This protocol tests an elapsed-time penalty at a query-to-observation attention readout.

[Read the study](temporal-attention-that-changes-predictions.md)

## Included implementation

Both irregular-time generators now produce targets after the last query gap. Position-only, explicit-age, fixed-decay and learned-decay models receive identical observations; a last-observation baseline and longer-gap shift set make the comparison inspectable. Tests cover reproducible episodes and trainable decay.

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
uv run --no-project --python .venv/bin/python python experiment.py --steps 40
```

The earlier standard-library references have their own self-tests:

```bash
uv run --no-project --python .venv/bin/python python attention_reference.py
```

Bias-only softmax still has the uniform-age-shift cancellation derived in the article. These models also receive explicit age features, which supply an absolute-age path; that distinction is part of the intervention.

## Earlier pilot result

On switching episodes, learned decay achieved 73.4% accuracy against 71.1% for the last-observation baseline. On periodic episodes it achieved 57.0%, below the last-observation baseline's 74.2%. Learned decay reached 57.8% on the longer-gap switching set. This one-seed run supports checking task dependence and shift sensitivity, not a general recency advantage. Shift gaps are 19, 37 and 83 steps so they do not all alias the twenty-step periodic cycle.

## Files

- [attention_reference.py](attention_reference.py) — Project-local support file.
- [experiment.py](experiment.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [smoke-results.json](smoke-results.json) — Recorded synthetic run; scope and provenance included.
- [temporal-attention-that-changes-predictions.md](temporal-attention-that-changes-predictions.md) — Article.
- [test_experiment.py](test_experiment.py) — Local regression checks.

## Remaining work

The original pilot is one seed and forty steps. The separate CPU comparison now covers five seeds, two generators and a frozen gap shift. Calibration tuning and real arrival-process validation remain outside it. An observed gain on switching data cannot establish a universal preference for recent evidence.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study temporal-attention-that-changes-predictions --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Learned decay reached 79.69% on the ordinary periodic task but fell to 62.75% under the gap shift, below the last-observation baseline at 71.48%. On switching data it was close to the simpler controls and near chance after the shift. The result depends on the generator and arrival gaps; it does not establish universal recency weighting.

See the [article](temporal-attention-that-changes-predictions.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
