# BitNet Style Quantisation: Storage vs Execution

Ternary numerical values, compact stored weights and faster inference are three different claims.

[Read the study](bitnet-quantization-and-conversion.md)

## Implementation

A deep float clone now preserves function and tied parameters. The separate ternary weight simulator uses a zero scale guard and a straight through gradient path; conversion preserves cloned weight ties and tests confirm gradient updates. The two bit symbol reference remains a separate storage example.

## Run locally

Run from this directory with Python 3.12.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

The earlier standard library references have their own self tests:

```bash
uv run --no-project --python .venv/bin/python python ternary_reference.py
```

`convert(model, quantized=False)` is the function preserving baseline. `quantized=True` replaces linear projections with the explicitly different weight simulation. Packed symbol storage and floating matrix execution are not interchangeable performance claims.

## Scope and limitations

This is not a BitNet inference runtime: activations remain floating point and no new normalization is inserted. A scalar CPU matvec reads the portable two bit packed format directly; it is not an optimised low bit kernel. The adapter measures matrix level stored bytes, error and runtime. Full model quality, tokenizer equivalence, quantization aware training and production speed improvements remain unmeasured.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study bitnet-quantization-and-conversion --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
