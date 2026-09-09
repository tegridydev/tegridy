# CloudVec: Vector Index Freshness with a SQLite Outbox

A paper can exist in the metadata database and still be absent from search.

[Read the study](cloudvec-paper-search.md)

## Implementation

SQLite now commits metadata and outbox jobs together. The in memory index adapter enforces monotonically increasing versions and retains deletion tombstones. Crash before ack, out of order retry, restart, empty store and full rebuild fixtures converge to the same final state.

## Run locally

Run from this directory with Python 3.12.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

Use `Store.write`, `deliver`, `replay` and `rebuild`; the test provides the complete crash/recovery sequence. The database is authoritative; an index lost after jobs were acknowledged requires a rebuild.

## Scope and limitations

The durable SQLite adapter demonstrates index freshness, tombstones and supplied vector retrieval, not a remote vector service or semantic relevance. Encoder manifests, worker backoff, persistent remote index verification and labelled retrieval evaluation remain integrations.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study cloudvec-paper-search --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
