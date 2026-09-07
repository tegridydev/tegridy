# MoA orchestration: routing, events and honest aggregation

A multi-agent result depends on which workers ran, what each returned and how those outputs became the final answer.

[Read the study](moa-framework.md)

## Included implementation

Three asynchronous fake providers now exercise normal text, empty deltas and timeout after partial output. The reducer enforces contiguous sequence numbers, detects conflicting duplicates and keeps the first terminal outcome. Aggregation excludes failed partial streams, and canonical cache keys include the complete supplied request.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

Run the tool or experiment after setup:

```bash
uv run --no-project --python .venv/bin/python python orchestrator.py
```

The demo prints exact per-attempt events, reconstructed streams, excluded workers and labelled completed output. Retry callers must assign a new attempt ID; the reducer does not merge attempts.

## Files

- [moa-framework.md](moa-framework.md) — Article.
- [orchestrator.py](orchestrator.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_orchestrator.py](test_orchestrator.py) — Local regression checks.

## Remaining work

The implementation bounds dispatch attempts and wall time, not provider token/currency spend. The SQLite cache supports restart and explicit expiry. SDK adapters, automatic retries, adaptive routing and answer-quality comparisons remain outside this implementation.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study moa-framework --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The 100 requests produced 50 completions and 50 deliberately injected failure outcomes. The latter are expected fault-handling cases, not an observed 50% production failure rate. The fixture also exercises persistent cache expiry; live providers and answer quality were not evaluated.

See the [article](moa-framework.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
