# Neuron mapping: selectivity, trajectories and causal checks

This study connects token-occurrence activation records to category tests and layer trajectories.

[Read the study](neuron-mapping-and-token-trajectories.md)

## Included implementation

The capture API now records every selected hook in one forward pass, keys values by sample/token occurrence/component/feature, preserves measured zero and enforces a storage ceiling. It removes hooks and restores training mode on failure. Shared PCA and guarded high-dimensional path straightness are supplied.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

`capture(model, token_ids, hooks, model_revision, tokenizer_revision)` returns schema-1 JSON-compatible records. Selected hooks must expose `[batch,position,feature]` and execute exactly once. The blog measurement viewer reads this format; model/tokenizer identities are supplied by the caller.

## Files

- [capture.py](capture.py) — Runnable implementation.
- [neuron-mapping-and-token-trajectories.md](neuron-mapping-and-token-trajectories.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_capture.py](test_capture.py) — Local regression checks.

## Remaining work

The tests use a tiny local network; no semantic category or real-model circuit has been established. Discovery/final corpus selection, category statistics and matched causal interventions remain experiments.

[Topic index](../README.md) · [Research index](../../README.md)
