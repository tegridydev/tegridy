# Sparse Autoencoders: Reconstruction vs Feature Recovery

A sparse autoencoder can reconstruct observations without recovering the independent features that generated them.

[Read the study](sparse-feature-recovery.md)

## Implementation

The sparse autoencoder now trains on normalized synthetic dictionaries with the stated activation probability and coefficient range. The evaluator uses one to one signed matching, detects duplicated true features and records dead learned columns. Decoder columns are renormalized after optimizer steps.

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
uv run --no-project --python .venv/bin/python python recovery.py --seed 17 --steps 100
```

The permutation fixture must match perfectly and the duplicated dictionary must be labelled non identifiable before interpreting a learned score. `pilot-results.json` retains every matched cosine rather than only a favorable average.

## Earlier pilot result

The 100-step pilot reached held out reconstruction MSE 0.0561, while mean one to one signed dictionary cosine was only 0.425. The evaluator passes the exact permutation fixture, but the trained dictionary has not recovered the original features cleanly. Report these two measurements separately; increasing reconstruction quality cannot stand in for support recovery.

## Scope and limitations

The original pilot uses 1,024 rows and one seed. The separate CPU comparison uses 10,000 rows, five dictionary/initialisation seeds, support F1, correlation/noise conditions and feature count sweeps. It does not test real model features or transfer a trained dictionary to a new generating dictionary. Good reconstruction alone does not demonstrate recovery.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study sparse-feature-recovery --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
