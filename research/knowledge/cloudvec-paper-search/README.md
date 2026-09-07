# CloudVec: measuring index freshness separately from search quality

A paper can exist in the metadata database and still be absent from search.

[Read the study](cloudvec-paper-search.md)

## Included implementation

SQLite now commits metadata and outbox jobs together. The in-memory index adapter enforces monotonically increasing versions and retains deletion tombstones. Crash-before-ack, out-of-order retry, restart, empty-store and full-rebuild fixtures converge to the same final state.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

Use `Store.write`, `deliver`, `replay` and `rebuild`; the test provides the complete crash/recovery sequence. The database is authoritative; an index lost after jobs were acknowledged requires a rebuild.

## Files

- [cloudvec-paper-search.md](cloudvec-paper-search.md) — Article.
- [outbox.py](outbox.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_outbox.py](test_outbox.py) — Local regression checks.

## Remaining work

The durable SQLite adapter demonstrates index freshness, tombstones and supplied-vector retrieval, not a remote vector service or semantic relevance. Encoder manifests, worker backoff, persistent remote index verification and labelled retrieval evaluation remain integrations.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study cloudvec-paper-search --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Rebuilt and reverse-replayed indexes matched across the declared runs after updates, deletions and injected pre-acknowledgement crashes. This tests application replay and version freshness, not power-loss durability or semantic retrieval quality.

See the [article](cloudvec-paper-search.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
