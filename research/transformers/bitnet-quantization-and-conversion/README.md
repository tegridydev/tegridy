# BitNet conversion: separate numerical quality from packed execution

Ternary numerical values, compact stored weights and faster inference are three different claims.

[Read the study](bitnet-quantization-and-conversion.md)

## Included implementation

A deep float clone now preserves function and tied parameters. The separate ternary-weight simulator uses a zero-scale guard and a straight-through gradient path; conversion preserves cloned weight ties and tests confirm gradient updates. The two-bit symbol reference remains a separate storage example.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

The earlier standard-library references have their own self-tests:

```bash
uv run --no-project --python .venv/bin/python python ternary_reference.py
```

`convert(model, quantized=False)` is the function-preserving baseline. `quantized=True` replaces linear projections with the explicitly different weight simulation. Packed-symbol storage and floating matrix execution are not interchangeable performance claims.

## Files

- [bitnet-quantization-and-conversion.md](bitnet-quantization-and-conversion.md) — Article.
- [quantization.py](quantization.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [ternary_reference.py](ternary_reference.py) — Project-local support file.
- [test_quantization.py](test_quantization.py) — Local regression checks.

## Remaining work

This is not a BitNet inference runtime: activations remain floating point and no new normalization is inserted. A scalar CPU matvec reads the portable two-bit packed format directly; it is not an optimised low-bit kernel. The adapter measures matrix-level stored bytes, error and runtime. Full-model quality, tokenizer equivalence, quantization-aware training and production speed improvements remain unmeasured.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study bitnet-quantization-and-conversion --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The packed representation uses fewer stored bytes, and its scalar output agrees numerically with the ternary simulation. The Python scalar packed path is slower than dense NumPy execution in this workload. Quantisation error against the original float matrix remains separate from packing error; storage reduction is not a speed or model-quality result.

See the [article](bitnet-quantization-and-conversion.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
