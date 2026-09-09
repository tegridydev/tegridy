# Multi Agent Orchestration: Streaming, Failures and Replay

A multi agent result depends on which workers ran, what each returned and how those outputs became the final answer.

[Read the study](moa-framework.md)

## Implementation

Three asynchronous fake providers now exercise normal text, empty deltas and timeout after partial output. The reducer enforces contiguous sequence numbers, detects conflicting duplicates and keeps the first terminal outcome. Aggregation excludes failed partial streams, and canonical cache keys include the complete supplied request.

## Run locally

Run from this directory with Python 3.12.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

Run:

```bash
uv run --no-project --python .venv/bin/python python orchestrator.py
```

The demo prints exact per attempt events, reconstructed streams, excluded workers and labelled completed output. Retry callers must assign a new attempt ID; the reducer does not merge attempts.

## Scope and limitations

The implementation bounds dispatch attempts and wall time, not provider token/currency spend. The SQLite cache supports restart and explicit expiry. SDK adapters, automatic retries, adaptive routing and answer quality comparisons remain outside this implementation.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study moa-framework --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
