# an embedding column needs more than a convincing name

An embedding workbench should let me load text, search it and understand why a result appeared.

[Read the post](embeddings-need-a-contract.md)

## Included implementation

The search tool now runs a BM25-style lexical baseline, signed-cosine ranking over supplied vectors and reciprocal-rank fusion. It checks unique document IDs, declared dimensions and exact representation-manifest compatibility before comparing vectors. Negative cosine scores remain visible.

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
python3 search.py index.json "byte model"
```

The earlier standard-library references have their own self-tests:

```bash
python3 vector_reference.py
```

The index is an object with `documents` containing string `id` and `text`. Vector documents also include `vector`, and the index includes `manifest` with `model_revision`, `tokenizer_revision`, `pooling`, `dimension`. Optional `--query-vector query.json` expects `vector` plus the identical `manifest`. The test contains a complete small fixture.

## Files

- [embeddings-need-a-contract.md](embeddings-need-a-contract.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [search.py](search.py) — Runnable implementation.
- [test_search.py](test_search.py) — Local regression checks.
- [vector_reference.py](vector_reference.py) — Project-local support file.

## Remaining work

No embedding model is bundled or called. Neural relevance depends on externally supplied vectors and a truthful model/tokenizer/pooling manifest. Index building, model adapters and labelled retrieval evaluation remain future work.

[Topic index](../README.md) · [Blog index](../../README.md)
