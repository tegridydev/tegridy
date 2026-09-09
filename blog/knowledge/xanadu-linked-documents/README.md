# Xanadu Inspired Links to Versioned Document Passages

A link to a document is useful until the document changes.

[Read the post](xanadu-linked-documents.md)

## Implementation

The SQLite document store now preserves immutable versions, optimistic edit preconditions and exact Unicode passage spans. Links retain IDs through JSON export/import, resolve historical versions after edits and distinguish missing targets from corrupted quotes. Invalid imports roll back as a transaction.

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
uv run --no-project --python .venv/bin/python python documents.py documents.sqlite
```

The earlier standard library references have their own self tests:

```bash
uv run --no-project --python .venv/bin/python python link_reference.py
```

`Documents.update(document, text, expected_version)` creates a version; `link(document, version, start, end)` creates a passage link; `resolve(link_id)` follows it. The CLI exports JSON, and `--import-file export.json` restores into an empty store. Duplicate imports fail explicitly instead of silently rewriting history.

## Scope and limitations

This is a local storage API rather than a collaborative editor or remote repository patch. Authentication, distributed synchronisation and automatic passage relocation remain outside its scope.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study xanadu-linked-documents --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
