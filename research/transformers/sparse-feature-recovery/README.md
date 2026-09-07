# Sparse feature recovery: reconstruction is only one target

A sparse autoencoder can reconstruct observations without recovering the independent features that generated them.

[Read the study](sparse-feature-recovery.md)

## Included implementation

The sparse autoencoder now trains on normalized synthetic dictionaries with the stated activation probability and coefficient range. The evaluator uses one-to-one signed matching, detects duplicated true features and records dead learned columns. Decoder columns are renormalized after optimizer steps.

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
uv run --no-project --python .venv/bin/python python recovery.py --seed 17 --steps 100
```

The permutation fixture must match perfectly and the duplicated dictionary must be labelled non-identifiable before interpreting a learned score. `pilot-results.json` retains every matched cosine rather than only a favorable average.

## Earlier pilot result

The 100-step pilot reached held-out reconstruction MSE 0.0561, while mean one-to-one signed dictionary cosine was only 0.425. The evaluator passes the exact-permutation fixture, but the trained dictionary has not recovered the original features cleanly. Report these two measurements separately; increasing reconstruction quality cannot stand in for support recovery.

## Files

- [pilot-results.json](pilot-results.json) — Recorded synthetic run; scope and provenance included.
- [recovery.py](recovery.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [sparse-feature-recovery.md](sparse-feature-recovery.md) — Article.
- [test_recovery.py](test_recovery.py) — Local regression checks.

## Remaining work

The original pilot uses 1,024 rows and one seed. The separate CPU comparison uses 10,000 rows, five dictionary/initialisation seeds, support F1, correlation/noise conditions and feature-count sweeps. It does not test real-model features or transfer a trained dictionary to a new generating dictionary. Good reconstruction alone does not demonstrate recovery.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study sparse-feature-recovery --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Low reconstruction error did not imply clean feature recovery. Across the feature-count, correlation and noise conditions, mean signed dictionary alignment stayed around 0.45–0.48 and support F1 around 0.13–0.33. The full receipt includes zero-reconstruction and all-positive-support controls; these synthetic dictionary results do not identify real-model concepts.

See the [article](sparse-feature-recovery.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
