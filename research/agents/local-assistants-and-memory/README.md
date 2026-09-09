# Local AI Memory: Retrieval and Temporal Validity

This study asks whether a bounded memory policy helps a model reuse facts across sessions.

[Read the study](local-assistants-and-memory.md)

## Implementation

The request recorder now filters by opaque owner ID, effective time and recorded time, resolves supersession per fact key, and logs selected and omitted candidates. Thirty synthetic histories cover corrections, historical queries and same display name owners.

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
uv run --no-project --python .venv/bin/python python retrieval.py
```

Relevance and recency policies share the same eligibility logic. The current rule uses term overlap and a fixed budget; no final history outcome tunes either rule.

## Scope and limitations

The 30 histories repeat a narrow fixture pattern; they are not twenty independent held out dispute families or a model recall benchmark. Budget units are explicitly whitespace words, not tokenizer counts. Model generation and retrieval quality comparisons remain unmeasured.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study local-assistants-and-memory --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
