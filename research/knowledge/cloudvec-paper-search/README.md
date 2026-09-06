# CloudVec: measuring index freshness separately from search quality

A paper can exist in the metadata database and still be absent from search.

[Read the study](cloudvec-paper-search.md)

## Included implementation

SQLite now commits metadata and outbox jobs together. The in-memory index adapter enforces monotonically increasing versions and retains deletion tombstones. Crash-before-ack, out-of-order retry, restart, empty-store and full-rebuild fixtures converge to the same final state.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

Use `Store.write`, `deliver`, `replay` and `rebuild`; the test provides the complete crash/recovery sequence. The database is authoritative; an index lost after jobs were acknowledged requires a rebuild.

## Files

- [cloudvec-paper-search.md](cloudvec-paper-search.md) — Article.
- [outbox.py](outbox.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_outbox.py](test_outbox.py) — Local regression checks.

## Remaining work

The adapter demonstrates index freshness mechanics, not a remote vector service or semantic relevance. Encoder manifests, worker backoff, persistent remote index verification and labelled retrieval evaluation remain integrations.

[Topic index](../README.md) · [Research index](../../README.md)
