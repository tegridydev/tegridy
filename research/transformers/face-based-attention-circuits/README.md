# Face Based Attention: Gated Feature Mixing

FBAC tests whether context dependent mixing of fixed feature slices improves a small selection task beyond added dense capacity.

[Read the study](face-based-attention-circuits.md)

## Implementation

FBAC now trains beside base, dense adapter and static mixture controls on frozen operand pair splits. The implementation checks the exact 4,420-parameter mixer, gate gradients and checkpoint reloads. Final evaluation includes gate permutations within the same task mode and across modes.

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

All four task modes for an operand pair stay together. Noise is resampled after pair allocation. Gate swaps intervene on computed mixture weights while preserving the recipient features and projections.

## Earlier pilot result

In the saved 40-step, seed-1729 run, FBAC accuracy was 34.2%, compared with 34.4% for the dense adapter and 32.8% for the base model. Within mode gate swaps gave 34.0%; cross mode swaps gave 34.6%. These small, mixed differences do not support a gate specific advantage. The useful next experiment is a sufficiently trained, multi seed comparison with matched interventions.

## Scope and limitations

The original saved pilot is one seed and forty steps. The separate CPU comparison adds five seeds and layout/swap evaluations, but still lacks a matched magnitude gate intervention. Small accuracy differences do not establish a feature mixing advantage.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study face-based-attention-circuits --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
