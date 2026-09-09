# Embedding Compatibility: Models, Vectors and Search

An embedding workbench should let me load text, search it and understand why a result appeared.

[Read the post](embeddings-need-a-contract.md)

## Implementation

The search tool now runs a BM25-style lexical baseline, signed cosine ranking over supplied vectors and reciprocal rank fusion. It checks unique document IDs, declared dimensions and exact representation manifest compatibility before comparing vectors. Negative cosine scores remain visible.

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
uv run --no-project --python .venv/bin/python python search.py index.json "byte model"
```

The earlier standard library references have their own self tests:

```bash
uv run --no-project --python .venv/bin/python python vector_reference.py
```

The index is an object with `documents` containing string `id` and `text`. Vector documents also include `vector`, and the index includes `manifest` with `model_revision`, `tokenizer_revision`, `pooling`, `dimension`. Optional `--query-vector query.json` expects `vector` plus the identical `manifest`. The test contains a complete small fixture.

## Scope and limitations

The optional index builder uses an explicitly acquired and hash checked public encoder; model weights are not bundled. Neural relevance depends on externally supplied vectors and a truthful model/tokenizer/pooling manifest. Index construction and a ten question engineering fixture comparison are implemented. An independently labelled retrieval benchmark remains future work.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study embeddings-need-a-contract --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
