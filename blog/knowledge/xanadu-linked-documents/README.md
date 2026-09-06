# xanadu-2: links that remember what they point to

A link to a document is useful until the document changes.

[Read the post](xanadu-linked-documents.md)

## Included implementation

The SQLite document store now preserves immutable versions, optimistic edit preconditions and exact Unicode passage spans. Links retain IDs through JSON export/import, resolve historical versions after edits and distinguish missing targets from corrupted quotes. Invalid imports roll back as a transaction.

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
python3 documents.py documents.sqlite
```

The earlier standard-library references have their own self-tests:

```bash
python3 link_reference.py
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
