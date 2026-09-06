# getting a useful export out of a chat log

A chat export gets interesting once I need to do something with it.

[Read the post](discord-log-export-and-field-extraction-toolkit.md)

## Included implementation

The offline exporter follows explicit page cursors, reconciles duplicate message IDs, preserves edit history and records conflicting revisions instead of silently replacing them. A 250-message fixture covers three pages, an edit and a repeated delivery. Interrupted or malformed input produces a partial receipt.

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
python3 export_logs.py pages.json export.json
```

Input is a JSON array of pages. Each page has `cursor`, `next_cursor` and `messages`; the first cursor and final next cursor are null. Messages require string `id`, `author_id`, `channel_id`, timezone-qualified `timestamp` and `content`; `edited_timestamp` is optional. Output preserves raw message objects and source-file hash.

## Files

- [discord-log-export-and-field-extraction-toolkit.md](discord-log-export-and-field-extraction-toolkit.md) — Article.
- [export_logs.py](export_logs.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_export_logs.py](test_export_logs.py) — Local regression checks.

## Remaining work

A live Discord acquisition adapter, PDF input adapter and interactive field-review screen are still separate integrations. The local exporter consumes saved JSON pages and does not connect to Discord.

[Topic index](../README.md) · [Blog index](../../README.md)
