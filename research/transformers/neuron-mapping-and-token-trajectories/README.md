# Neuron mapping: selectivity, trajectories and causal checks

This study connects token-occurrence activation records to category tests and layer trajectories.

[Read the study](neuron-mapping-and-token-trajectories.md)

## Included implementation

The capture API now records every selected hook in one forward pass, keys values by sample/token occurrence/component/feature, preserves measured zero and enforces a storage ceiling. It removes hooks and restores training mode on failure. Shared PCA and guarded high-dimensional path straightness are supplied.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
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

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study neuron-mapping-and-token-trajectories --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Six declared prompts produced 37,632 activation values, projected using a shared two-dimensional basis fitted on the first prompt. Occurrence identity is retained across the capture. Category selectivity and causal effects require separate experiments.

See the [article](neuron-mapping-and-token-trajectories.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
