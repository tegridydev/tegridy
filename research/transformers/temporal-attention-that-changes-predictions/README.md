# Temporal Attention for Irregular Observations

This protocol tests an elapsed time penalty at a query to observation attention readout.

[Read the study](temporal-attention-that-changes-predictions.md)

## Implementation

Both irregular time generators now produce targets after the last query gap. Position only, explicit age, fixed decay and learned decay models receive identical observations; a last observation baseline and longer gap shift set make the comparison inspectable. Tests cover reproducible episodes and trainable decay.

## Run locally

Run from this directory with Python 3.12.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

Run:

```bash
uv run --no-project --python .venv/bin/python python experiment.py --steps 40
```

The earlier standard library references have their own self tests:

```bash
uv run --no-project --python .venv/bin/python python attention_reference.py
```

Bias only softmax still has the uniform age shift cancellation derived in the article. These models also receive explicit age features, which supply an absolute age path; that distinction is part of the intervention.

## Earlier pilot result

On switching episodes, learned decay achieved 73.4% accuracy against 71.1% for the last observation baseline. On periodic episodes it achieved 57.0%, below the last observation baseline's 74.2%. Learned decay reached 57.8% on the longer gap switching set. This one seed run supports checking task dependence and shift sensitivity, not a general recency advantage. Shift gaps are 19, 37 and 83 steps so they do not all alias the twenty step periodic cycle.

## Scope and limitations

The original pilot is one seed and forty steps. The separate CPU comparison now covers five seeds, two generators and a frozen gap shift. Calibration tuning and real arrival process validation remain outside it. An observed gain on switching data cannot establish a universal preference for recent evidence.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study temporal-attention-that-changes-predictions --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
