# Weight similarity and functional low-rank compression

This study asks whether similarity helps select less damaging weight-sharing or factorisation operations.

[Read the study](weight-similarity-and-svd-compression.md)

## Included implementation

The factorizer now creates actual NumPy low-rank factors, reloads serialized arrays and measures calibration/held-out output error. Reports separate parameter count, raw array bytes and complete file bytes. Tests verify an exact low-rank matrix and a calibration/held-out counterexample.

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
python3 compress.py weight.npy calibration.npy heldout.npy factors.npz --rank 16
```

`weight` has shape `[output,input]`; both input arrays have shape `[samples,input]`. Rank 32 on a 64×64 matrix only breaks even in factor parameter count, and serialization headers still cost bytes. Existing output files are refused.

## Files

- [compress.py](compress.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_compress.py](test_compress.py) — Local regression checks.
- [weight-similarity-and-svd-compression.md](weight-similarity-and-svd-compression.md) — Article.

## Remaining work

This is single-matrix compression, not an end-to-end compressed language model. Layer selection, task loss, activation-weighted fitting and latency comparisons still require a supplied model and inputs.

[Topic index](../README.md) · [Research index](../../README.md)
