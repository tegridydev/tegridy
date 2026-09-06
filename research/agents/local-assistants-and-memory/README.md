# Local assistant memory: retrieval, validity and reuse

This study asks whether a bounded memory policy helps a model reuse facts across sessions.

[Read the study](local-assistants-and-memory.md)

## Included implementation

The request recorder now filters by opaque owner ID, effective time and recorded time, resolves supersession per fact key, and logs selected and omitted candidates. Thirty synthetic histories cover corrections, historical queries and same-display-name owners.

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
python3 retrieval.py
```

Relevance and recency policies share the same eligibility logic. The current rule uses term overlap and a fixed budget; no final-history outcome tunes either rule.

## Files

- [local-assistants-and-memory.md](local-assistants-and-memory.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [retrieval.py](retrieval.py) — Runnable implementation.
- [test_retrieval.py](test_retrieval.py) — Local regression checks.

## Remaining work

The 30 histories repeat a narrow fixture pattern; they are not twenty independent held-out dispute families or a model recall benchmark. Budget units are explicitly whitespace words, not tokenizer counts. Model generation and retrieval-quality comparisons remain unmeasured.

[Topic index](../README.md) · [Research index](../../README.md)
