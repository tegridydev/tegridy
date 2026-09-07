# Local assistant memory: retrieval, validity and reuse

This study asks whether a bounded memory policy helps a model reuse facts across sessions.

[Read the study](local-assistants-and-memory.md)

## Included implementation

The request recorder now filters by opaque owner ID, effective time and recorded time, resolves supersession per fact key, and logs selected and omitted candidates. Thirty synthetic histories cover corrections, historical queries and same-display-name owners.

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
uv run --no-project --python .venv/bin/python python retrieval.py
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

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study local-assistants-and-memory --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Under the fixed word budget, relevance-based selection recovered all current target facts, while recent-first selection recovered none. Both recovered the historical and known-at-the-time targets. These deliberately constructed lexical histories demonstrate a selection-policy difference, not end-to-end assistant answer quality.

See the [article](local-assistants-and-memory.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
