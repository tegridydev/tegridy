# Hydraform: trainable structural adaptation under a fixed budget

Hydraform proposes changing attention-head structure during training.

[Read the study](hydraform.md)

## Included implementation

An independent local attention module now widens or narrows a head, copies overlapping weights, enforces a parameter budget and rebuilds Adam with all moment state reset. Tests prove optimizer coverage, new-weight updates, padding isolation and architecture-aware save/reload.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

`mutate` returns both the replacement optimizer and a before/after parameter-identity event. Its all-moment reset policy must also be applied to fixed and random controls before any quality comparison.

## Files

- [adaptation.py](adaptation.py) — Runnable implementation.
- [hydraform.md](hydraform.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_adaptation.py](test_adaptation.py) — Local regression checks.

## Remaining work

The upstream revision remains unpinned; this is a local reconstruction of the mutation contract. The bounded synthetic study includes a two-candidate guided width choice and fixed-size/reset controls. It does not establish AG News performance or reproduce an upstream search system.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study hydraform --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The guided mutation averaged 95.47% accuracy, compared with 95.55% for both the fixed-final and random-mutation controls and 95.70% for the reset control. These synthetic results do not establish a benefit from guided mutation.

See the [article](hydraform.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
