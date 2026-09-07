# Weight similarity and functional low-rank compression

This study asks whether similarity helps select less damaging weight-sharing or factorisation operations.

[Read the study](weight-similarity-and-svd-compression.md)

## Included implementation

The factorizer now creates actual NumPy low-rank factors, reloads serialized arrays and measures calibration/held-out output error. Reports separate parameter count, raw array bytes and complete file bytes. Tests verify an exact low-rank matrix and a calibration/held-out counterexample.

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
uv run --no-project --python .venv/bin/python python compress.py weight.npy calibration.npy heldout.npy factors.npz --rank 16
```

`weight` has shape `[output,input]`; both input arrays have shape `[samples,input]`. Rank 32 on a 64×64 matrix only breaks even in factor parameter count, and serialization headers still cost bytes. Existing output files are refused.

## Files

- [compress.py](compress.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_compress.py](test_compress.py) — Local regression checks.
- [weight-similarity-and-svd-compression.md](weight-similarity-and-svd-compression.md) — Article.

## Remaining work

This is single-matrix compression, not an end-to-end compressed language model. The separate CPU study measures the first pinned GPT-Neo MLP projection on four short texts. Broader layer selection, end-to-end task loss, activation-weighted fitting and latency comparisons remain outside that measurement.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study weight-similarity-and-svd-compression --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Rank-128 factors occupied 1.97 MB versus 9.44 MB for the original stored matrix, a reduction of about 79%. Layer-output mean squared error was 0.298; smaller ranks saved more space but increased that error. These measurements cover one projection and four short texts, not end-to-end model quality or inference speed.

See the [article](weight-similarity-and-svd-compression.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
