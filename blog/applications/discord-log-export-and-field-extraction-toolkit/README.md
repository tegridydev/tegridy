# getting a useful export out of a chat log

A chat export gets interesting once I need to do something with it.

[Read the post](discord-log-export-and-field-extraction-toolkit.md)

## Included implementation

The offline exporter follows explicit page cursors, reconciles duplicate message IDs, preserves edit history and records conflicting revisions instead of silently replacing them. A 250-message fixture covers three pages, an edit and a repeated delivery. Interrupted or malformed input produces a partial receipt.

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
uv run --no-project --python .venv/bin/python python export_logs.py pages.json export.json
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

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study discord-log-export-and-field-extraction-toolkit --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The saved-JSON exporter retained all 10,000 unique messages across 100 overlapping pages. This checks reconciliation and export completeness for the supplied inputs, including an edit; it does not measure live Discord acquisition.

See the [article](discord-log-export-and-field-extraction-toolkit.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
