# Hydraform: trainable structural adaptation under a fixed budget

Hydraform proposes changing attention-head structure during training.

[Read the study](hydraform.md)

## Included implementation

An independent local attention module now widens or narrows a head, copies overlapping weights, enforces a parameter budget and rebuilds Adam with all moment state reset. Tests prove optimizer coverage, new-weight updates, padding isolation and architecture-aware save/reload.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

`mutate` returns both the replacement optimizer and a before/after parameter-identity event. Its all-moment reset policy must also be applied to fixed and random controls before any quality comparison.

## Files

- [adaptation.py](adaptation.py) — Runnable implementation.
- [hydraform.md](hydraform.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_adaptation.py](test_adaptation.py) — Local regression checks.

## Remaining work

The upstream revision remains unpinned; this is a local reconstruction of the mutation contract. It does not include guided architecture search, AG News training or final-size/reset-matched comparisons.

[Topic index](../README.md) · [Research index](../../README.md)
