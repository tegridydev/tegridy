# Organising Research Papers, Books and Reading Notes

I can build a reading queue much faster than I can read it.

[Read the post](paper-and-book-collection.md)

## Implementation

A persistent SQLite reading queue separates works, editions, local acquisition receipts and page/section reading notes. Stable IDs replace title based identity, foreign keys reject unknown editions and local files receive SHA-256 receipts. Reading one edition does not mark another edition read.

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
uv run --no-project --python .venv/bin/python python reading_queue.py reading.sqlite add cedar "Cedar manual" "Check the timeout change"
```

Add an edition with `edition cedar-v1 cedar 1 https://example.org/manual "self-authored fixture" --file manual.pdf`; record actual reading with `read cedar-v1 "pages 2–3" "checked timeout"`; use `export` for the queue JSON. Each command follows `reading.sqlite`.

## Scope and limitations

Provider discovery and rights verification remain outside scope. acquire.py downloads explicitly selected HTTPS files against a pinned hash and byte limit. A recorded rights description is supplied metadata, not a legal determination.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study paper-and-book-collection --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
