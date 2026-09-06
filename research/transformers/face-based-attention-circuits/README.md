# Face-based attention circuits: a controlled feature-mixing study

FBAC tests whether context-dependent mixing of fixed feature slices improves a small selection task beyond added dense capacity.

[Read the study](face-based-attention-circuits.md)

## Included implementation

FBAC now trains beside base, dense-adapter and static-mixture controls on frozen operand-pair splits. The implementation checks the exact 4,420-parameter mixer, gate gradients and checkpoint reloads. Final evaluation includes gate permutations within the same task mode and across modes.

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

All four task modes for an operand pair stay together. Noise is resampled after pair allocation. Gate swaps intervene on computed mixture weights while preserving the recipient features and projections.

## Local result

In the saved 40-step, seed-1729 run, FBAC accuracy was 34.2%, compared with 34.4% for the dense adapter and 32.8% for the base model. Within-mode gate swaps gave 34.0%; cross-mode swaps gave 34.6%. These small, mixed differences do not support a gate-specific advantage. The useful next experiment is a sufficiently trained, multi-seed comparison with matched interventions.

## Files

- [experiment.py](experiment.py) — Runnable implementation.
- [face-based-attention-circuits.md](face-based-attention-circuits.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [smoke-results.json](smoke-results.json) — Recorded synthetic run; scope and provenance included.
- [test_experiment.py](test_experiment.py) — Local regression checks.

## Remaining work

The saved run is one seed and forty steps, without a matched-magnitude gate intervention or multi-seed confidence interval. Small accuracy differences do not establish a feature-mixing advantage.

[Topic index](../README.md) · [Research index](../../README.md)
