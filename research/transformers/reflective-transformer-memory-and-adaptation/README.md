# Reflective transformer: causal memory and bounded adaptation

This proposal combines a causally written memory bank with head-level retrieval.

[Read the study](reflective-transformer-memory-and-adaptation.md)

## Included implementation

The memory module now stores episode-isolated `[batch,head,slot,width]` keys/values, performs detached FIFO writes only at increasing completed steps and masks same-step/future entries. Empty banks return zero; per-head gates start at 0.5. Tests check reset, reload and 32/128 total capacities.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

Use `Memory.write` after processing a segment and query with a later prediction step. A reset is explicit between episodes. The caller remains responsible for not supplying future labels as earlier observations.

## Files

- [memory.py](memory.py) — Runnable implementation.
- [reflective-transformer-memory-and-adaptation.md](reflective-transformer-memory-and-adaptation.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_memory.py](test_memory.py) — Local regression checks.

## Remaining work

This is the memory component, not a trained reflective Transformer. The bounded delayed-reuse study compares no memory, full attention over eight items and four-slot FIFO with a learned query/head. LRU/utility policies, stale-association semantics and integration into a full reflective Transformer remain outside its scope.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study reflective-transformer-memory-and-adaptation --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Attention over all eight written items averaged 97.19% accuracy; four-slot FIFO averaged 35.98% and no memory 7.42%. FIFO was much worse on evicted than retained targets. The capacity difference is intentional, so this is an eligibility/eviction study, not a capacity-matched architecture comparison.

See the [article](reflective-transformer-memory-and-adaptation.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
