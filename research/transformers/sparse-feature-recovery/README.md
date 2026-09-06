# Sparse feature recovery: reconstruction is only one target

A sparse autoencoder can reconstruct observations without recovering the independent features that generated them.

[Read the study](sparse-feature-recovery.md)

## Included implementation

The sparse autoencoder now trains on normalized synthetic dictionaries with the stated activation probability and coefficient range. The evaluator uses one-to-one signed matching, detects duplicated true features and records dead learned columns. Decoder columns are renormalized after optimizer steps.

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
python3 recovery.py --seed 17 --steps 100
```

The permutation fixture must match perfectly and the duplicated dictionary must be labelled non-identifiable before interpreting a learned score. `pilot-results.json` retains every matched cosine rather than only a favorable average.

## Local result

The 100-step pilot reached held-out reconstruction MSE 0.0561, while mean one-to-one signed dictionary cosine was only 0.425. The evaluator passes the exact-permutation fixture, but the trained dictionary has not recovered the original features cleanly. Report these two measurements separately; increasing reconstruction quality cannot stand in for support recovery.

## Files

- [pilot-results.json](pilot-results.json) — Recorded synthetic run; scope and provenance included.
- [recovery.py](recovery.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [sparse-feature-recovery.md](sparse-feature-recovery.md) — Article.
- [test_recovery.py](test_recovery.py) — Local regression checks.

## Remaining work

The saved run uses 1,024 rows and one seed; it is not the full dictionary-seed study. Support F1, correlated-feature ablations, held-out dictionary generalization and feature-count sweeps remain work. Good reconstruction alone does not demonstrate recovery.

[Topic index](../README.md) · [Research index](../../README.md)
