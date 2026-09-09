# Transformer Activation Maps and Token Trajectories

This study connects token occurrence activation records to category tests and layer trajectories.

[Read the study](neuron-mapping-and-token-trajectories.md)

## Implementation

The capture API now records every selected hook in one forward pass, keys values by sample/token occurrence/component/feature, preserves measured zero and enforces a storage ceiling. It removes hooks and restores training mode on failure. Shared PCA and guarded high dimensional path straightness are supplied.

## Run locally

Run from this directory with Python 3.12.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

`capture(model, token_ids, hooks, model_revision, tokenizer_revision)` returns schema-1 JSON compatible records. Selected hooks must expose `[batch,position,feature]` and execute exactly once. The blog measurement viewer reads this format; model/tokenizer identities are supplied by the caller.

## Scope and limitations

The tests use a tiny local network; no semantic category or real model circuit has been established. Discovery/final corpus selection, category statistics and matched causal interventions remain experiments.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study neuron-mapping-and-token-trajectories --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
