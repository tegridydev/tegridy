# SVD Compression: Storage and Functional Error

This study asks whether similarity helps select less damaging weight sharing or factorisation operations.

[Read the study](weight-similarity-and-svd-compression.md)

## Implementation

The factorizer now creates actual NumPy low rank factors, reloads serialized arrays and measures calibration/held out output error. Reports separate parameter count, raw array bytes and complete file bytes. Tests verify an exact low rank matrix and a calibration/held out counterexample.

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
uv run --no-project --python .venv/bin/python python compress.py weight.npy calibration.npy heldout.npy factors.npz --rank 16
```

`weight` has shape `[output,input]`; both input arrays have shape `[samples,input]`. Rank 32 on a 64×64 matrix only breaks even in factor parameter count, and serialization headers still cost bytes. Existing output files are refused.

## Scope and limitations

This is single matrix compression, not an end to end compressed language model. The separate CPU study measures the first pinned GPT Neo MLP projection on four short texts. Broader layer selection, end to end task loss, activation weighted fitting and latency comparisons remain outside that measurement.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study weight-similarity-and-svd-compression --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
