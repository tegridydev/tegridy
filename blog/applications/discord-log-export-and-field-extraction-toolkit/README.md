# Processing Saved Chat Logs Without Losing History

A chat export gets interesting once I need to do something with it.

[Read the post](discord-log-export-and-field-extraction-toolkit.md)

## Implementation

The offline exporter follows explicit page cursors, reconciles duplicate message IDs, preserves edit history and records conflicting revisions instead of silently replacing them. A 250-message fixture covers three pages, an edit and a repeated delivery. Interrupted or malformed input produces a partial receipt.

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
uv run --no-project --python .venv/bin/python python export_logs.py pages.json export.json
```

Input is a JSON array of pages. Each page has `cursor`, `next_cursor` and `messages`; the first cursor and final next cursor are null. Messages require string `id`, `author_id`, `channel_id`, timezone qualified `timestamp` and `content`; `edited_timestamp` is optional. Output preserves raw message objects and source file hash.

## Scope and limitations

A live Discord acquisition adapter, PDF input adapter and interactive field review screen are still separate integrations. The local exporter consumes saved JSON pages and does not connect to Discord.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study discord-log-export-and-field-extraction-toolkit --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
