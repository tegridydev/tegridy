# an embedding column needs more than a convincing name

An embedding workbench should let me load text, search it and understand why a result appeared.

[Read the post](embeddings-need-a-contract.md)

## Included implementation

The search tool now runs a BM25-style lexical baseline, signed-cosine ranking over supplied vectors and reciprocal-rank fusion. It checks unique document IDs, declared dimensions and exact representation-manifest compatibility before comparing vectors. Negative cosine scores remain visible.

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
uv run --no-project --python .venv/bin/python python search.py index.json "byte model"
```

The earlier standard-library references have their own self-tests:

```bash
uv run --no-project --python .venv/bin/python python vector_reference.py
```

The index is an object with `documents` containing string `id` and `text`. Vector documents also include `vector`, and the index includes `manifest` with `model_revision`, `tokenizer_revision`, `pooling`, `dimension`. Optional `--query-vector query.json` expects `vector` plus the identical `manifest`. The test contains a complete small fixture.

## Files

- [embeddings-need-a-contract.md](embeddings-need-a-contract.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [search.py](search.py) — Runnable implementation.
- [test_search.py](test_search.py) — Local regression checks.
- [vector_reference.py](vector_reference.py) — Project-local support file.

## Remaining work

The optional index builder uses an explicitly acquired and hash-checked public encoder; model weights are not bundled. Neural relevance depends on externally supplied vectors and a truthful model/tokenizer/pooling manifest. Index construction and a ten-question engineering-fixture comparison are implemented. An independently labelled retrieval benchmark remains future work.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study embeddings-need-a-contract --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

On these ten authored fixtures, vector search ranked the labelled documents better than lexical search. Rank fusion performed worse than vector search alone; adding lexical ranks did not improve this fixture.

See the [article](embeddings-need-a-contract.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
