# MoA orchestration: routing, events and honest aggregation

A multi-agent result depends on which workers ran, what each returned and how those outputs became the final answer.

[Read the study](moa-framework.md)

## Included implementation

Three asynchronous fake providers now exercise normal text, empty deltas and timeout after partial output. The reducer enforces contiguous sequence numbers, detects conflicting duplicates and keeps the first terminal outcome. Aggregation excludes failed partial streams, and canonical cache keys include the complete supplied request.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

Run the tool or experiment after setup:

```bash
python3 orchestrator.py
```

The demo prints exact per-attempt events, reconstructed streams, excluded workers and labelled completed output. Retry callers must assign a new attempt ID; the reducer does not merge attempts.

## Files

- [moa-framework.md](moa-framework.md) — Article.
- [orchestrator.py](orchestrator.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_orchestrator.py](test_orchestrator.py) — Local regression checks.

## Remaining work

The implementation bounds dispatch attempts and wall time, not provider token/currency spend. SDK adapters, persistent cache expiry, automatic retries, adaptive routing and answer-quality comparisons remain unimplemented.

[Topic index](../README.md) · [Research index](../../README.md)
