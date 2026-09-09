# Extracting Contact Fields with Source Evidence

I'm interested in the bit where messy text becomes a useful table.

[Read the post](lead-extraction-and-cleaning.md)

## Implementation

A local SQLite pipeline extracts email candidates with exact Unicode spans, retains the source text, requires an explicit accepted/rejected review, and applies suppression again during CSV export. No owner relationship is guessed from nearby prose. Formula like CSV cells are escaped.

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
uv run --no-project --python .venv/bin/python python extract_contacts.py contacts.sqlite ingest notes.txt
```

Use `list` to inspect candidate IDs; `review ID accepted REVIEWER --relation "reviewed relation"` to accept; `suppress EMAIL REASON` to exclude; and `export output.csv` to write accepted, unsuppressed candidates. These commands follow the database argument. No messages are sent.

## Scope and limitations

Acquisition, deliverability validation and model assisted relation extraction are not included. The regex is a deliberately limited candidate finder, not a complete email address parser. Suppression uses a conservative case insensitive key and retains source spellings.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study lead-extraction-and-cleaning --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
