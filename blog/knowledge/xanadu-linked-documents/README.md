# xanadu-2: links that remember what they point to

A link to a document is useful until the document changes.

[Read the post](xanadu-linked-documents.md)

## Included implementation

The SQLite document store now preserves immutable versions, optimistic edit preconditions and exact Unicode passage spans. Links retain IDs through JSON export/import, resolve historical versions after edits and distinguish missing targets from corrupted quotes. Invalid imports roll back as a transaction.

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
uv run --no-project --python .venv/bin/python python documents.py documents.sqlite
```

The earlier standard-library references have their own self-tests:

```bash
uv run --no-project --python .venv/bin/python python link_reference.py
```

`Documents.update(document, text, expected_version)` creates a version; `link(document, version, start, end)` creates a passage link; `resolve(link_id)` follows it. The CLI exports JSON, and `--import-file export.json` restores into an empty store. Duplicate imports fail explicitly instead of silently rewriting history.

## Files

- [documents.py](documents.py) — Runnable implementation.
- [link_reference.py](link_reference.py) — Project-local support file.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_documents.py](test_documents.py) — Local regression checks.
- [xanadu-linked-documents.md](xanadu-linked-documents.md) — Article.

## Remaining work

This is a local storage API rather than a collaborative editor or remote repository patch. Authentication, distributed synchronisation and automatic passage relocation remain outside its scope.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study xanadu-linked-documents --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

All 1,000 passage links survived export/import across 1,000 documents and 2,000 versions. This supports the immutable-passage round-trip contract, including Unicode text; it does not establish distributed editing or an upstream repair.

See the [article](xanadu-linked-documents.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
