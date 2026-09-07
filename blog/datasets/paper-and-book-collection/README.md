# collecting papers without losing why I wanted them

I can build a reading queue much faster than I can read it.

[Read the post](paper-and-book-collection.md)

## Included implementation

A persistent SQLite reading queue separates works, editions, local acquisition receipts and page/section reading notes. Stable IDs replace title-based identity, foreign keys reject unknown editions and local files receive SHA-256 receipts. Reading one edition does not mark another edition read.

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
uv run --no-project --python .venv/bin/python python reading_queue.py reading.sqlite add cedar "Cedar manual" "Check the timeout change"
```

Add an edition with `edition cedar-v1 cedar 1 https://example.org/manual "self-authored fixture" --file manual.pdf`; record actual reading with `read cedar-v1 "pages 2–3" "checked timeout"`; use `export` for the queue JSON. Each command follows `reading.sqlite`.

## Files

- [paper-and-book-collection.md](paper-and-book-collection.md) — Article.
- [reading_queue.py](reading_queue.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_reading_queue.py](test_reading_queue.py) — Local regression checks.

## Remaining work

Provider discovery and rights verification remain outside scope. acquire.py downloads explicitly selected HTTPS files against a pinned hash and byte limit. A recorded rights description is supplied metadata, not a legal determination.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study paper-and-book-collection --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The fixture retained 100 selected items, 50 acquisition records and 25 reading records as separate states. Acquisition did not imply that an item had been read. The check validates the state model and persistence, not discovery quality or permission to redistribute a real document.

See the [article](paper-and-book-collection.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
