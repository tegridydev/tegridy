# Hydraform: Adaptive Attention Head Mutation

Hydraform proposes changing attention head structure during training.

[Read the study](hydraform.md)

## Implementation

An independent local attention module now widens or narrows a head, copies overlapping weights, enforces a parameter budget and rebuilds Adam with all moment state reset. Tests prove optimizer coverage, new weight updates, padding isolation and architecture aware save/reload.

## Run locally

Run from this directory with Python 3.12.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

`mutate` returns both the replacement optimizer and a before/after parameter identity event. Its all moment reset policy must also be applied to fixed and random controls before any quality comparison.

## Scope and limitations

The upstream revision remains unpinned; this is a local reconstruction of the mutation contract. The bounded synthetic study includes a two candidate guided width choice and fixed size/reset controls. It does not establish AG News performance or reproduce an upstream search system.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study hydraform --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
