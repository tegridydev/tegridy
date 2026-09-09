# Transformer Memory: Causal Retrieval and Adaptation

This proposal combines a causally written memory bank with head level retrieval.

[Read the study](reflective-transformer-memory-and-adaptation.md)

## Implementation

The memory module now stores episode isolated `[batch,head,slot,width]` keys/values, performs detached FIFO writes only at increasing completed steps and masks same step/future entries. Empty banks return zero; per head gates start at 0.5. Tests check reset, reload and 32/128 total capacities.

## Run locally

Run from this directory with Python 3.12.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

Use `Memory.write` after processing a segment and query with a later prediction step. A reset is explicit between episodes. The caller remains responsible for not supplying future labels as earlier observations.

## Scope and limitations

This is the memory component, not a trained reflective Transformer. The bounded delayed reuse study compares no memory, full attention over eight items and four slot FIFO with a learned query/head. LRU/utility policies, stale association semantics and integration into a full reflective Transformer remain outside its scope.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study reflective-transformer-memory-and-adaptation --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
