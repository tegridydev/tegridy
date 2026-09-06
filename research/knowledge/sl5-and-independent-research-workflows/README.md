# SL5: thread-aware evidence and prediction timelines

SL5 is a proposal for searching technical discussions without losing speaker, quotation and time context.

[Read the study](sl5-and-independent-research-workflows.md)

## Included implementation

A ten-message thread fixture now resolves nested quotes to the original author/span, retains timestamp correction history and rejects mixed or cyclic quote attribution. Forecast resolution requires a pre-outcome interpretation and leaves two vague forecasts unresolvable.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

The `Thread` API stores messages and quote edges; `Forecast` freezes target, deadline and ambiguity. Tests ask five exact-span attribution questions and resolve two ambiguous forecasts without hindsight.

## Files

- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [sl5-and-independent-research-workflows.md](sl5-and-independent-research-workflows.md) — Article.
- [test_thread.py](test_thread.py) — Local regression checks.
- [thread.py](thread.py) — Runnable implementation.

## Remaining work

No live thread acquisition, semantic retrieval or model answering is included. The larger thread-family comparison and human annotation agreement remain experiments.

[Topic index](../README.md) · [Research index](../../README.md)
