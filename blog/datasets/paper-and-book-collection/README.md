# collecting papers without losing why I wanted them

I can build a reading queue much faster than I can read it.

[Read the post](paper-and-book-collection.md)

## Included implementation

A persistent SQLite reading queue separates works, editions, local acquisition receipts and page/section reading notes. Stable IDs replace title-based identity, foreign keys reject unknown editions and local files receive SHA-256 receipts. Reading one edition does not mark another edition read.

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
python3 reading_queue.py reading.sqlite add cedar "Cedar manual" "Check the timeout change"
```

Add an edition with `edition cedar-v1 cedar 1 https://example.org/manual "self-authored fixture" --file manual.pdf`; record actual reading with `read cedar-v1 "pages 2–3" "checked timeout"`; use `export` for the queue JSON. Each command follows `reading.sqlite`.

## Files

- [paper-and-book-collection.md](paper-and-book-collection.md) — Article.
- [reading_queue.py](reading_queue.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_reading_queue.py](test_reading_queue.py) — Local regression checks.

## Remaining work

Provider discovery, rights verification and automatic downloading are not implemented. A recorded rights description is supplied metadata, not a legal determination.

[Topic index](../README.md) · [Blog index](../../README.md)
