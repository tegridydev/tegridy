# BitNet conversion: separate numerical quality from packed execution

Ternary numerical values, compact stored weights and faster inference are three different claims.

[Read the study](bitnet-quantization-and-conversion.md)

## Included implementation

A deep float clone now preserves function and tied parameters. The separate ternary-weight simulator uses a zero-scale guard and a straight-through gradient path; conversion preserves cloned weight ties and tests confirm gradient updates. The two-bit symbol reference remains a separate storage example.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

The earlier standard-library references have their own self-tests:

```bash
python3 ternary_reference.py
```

`convert(model, quantized=False)` is the function-preserving baseline. `quantized=True` replaces linear projections with the explicitly different weight simulation. Packed-symbol storage and floating matrix execution are not interchangeable performance claims.

## Files

- [bitnet-quantization-and-conversion.md](bitnet-quantization-and-conversion.md) — Article.
- [quantization.py](quantization.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [ternary_reference.py](ternary_reference.py) — Project-local support file.
- [test_quantization.py](test_quantization.py) — Local regression checks.

## Remaining work

This is not a BitNet inference runtime: activations remain floating point, no packed kernel runs, and no new normalization is inserted. Full-model quality, tokenizer equivalence, quantization-aware training and actual speed/storage improvements remain unmeasured.

[Topic index](../README.md) · [Research index](../../README.md)
