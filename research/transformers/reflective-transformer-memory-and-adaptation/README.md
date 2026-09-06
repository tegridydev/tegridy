# Reflective transformer: causal memory and bounded adaptation

This proposal combines a causally written memory bank with head-level retrieval.

[Read the study](reflective-transformer-memory-and-adaptation.md)

## Included implementation

The memory module now stores episode-isolated `[batch,head,slot,width]` keys/values, performs detached FIFO writes only at increasing completed steps and masks same-step/future entries. Empty banks return zero; per-head gates start at 0.5. Tests check reset, reload and 32/128 total capacities.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

Use `Memory.write` after processing a segment and query with a later prediction step. A reset is explicit between episodes. The caller remains responsible for not supplying future labels as earlier observations.

## Files

- [memory.py](memory.py) — Runnable implementation.
- [reflective-transformer-memory-and-adaptation.md](reflective-transformer-memory-and-adaptation.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_memory.py](test_memory.py) — Local regression checks.

## Remaining work

This is the memory component, not a trained reflective Transformer. The delayed-reuse task, ordinary-attention integration, LRU/utility policies, stale-association semantics and feedback-driven adaptation remain unimplemented.

[Topic index](../README.md) · [Research index](../../README.md)
