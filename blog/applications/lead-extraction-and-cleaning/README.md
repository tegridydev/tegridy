# pulling useful fields out of messy text

I'm interested in the bit where messy text becomes a useful table.

[Read the post](lead-extraction-and-cleaning.md)

## Included implementation

A local SQLite pipeline extracts email candidates with exact Unicode spans, retains the source text, requires an explicit accepted/rejected review, and applies suppression again during CSV export. No owner relationship is guessed from nearby prose. Formula-like CSV cells are escaped.

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
python3 extract_contacts.py contacts.sqlite ingest notes.txt
```

Use `list` to inspect candidate IDs; `review ID accepted REVIEWER --relation "reviewed relation"` to accept; `suppress EMAIL REASON` to exclude; and `export output.csv` to write accepted, unsuppressed candidates. These commands follow the database argument. No messages are sent.

## Files

- [extract_contacts.py](extract_contacts.py) — Runnable implementation.
- [lead-extraction-and-cleaning.md](lead-extraction-and-cleaning.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_contacts.py](test_contacts.py) — Local regression checks.

## Remaining work

Acquisition, deliverability validation and model-assisted relation extraction are not included. The regex is a deliberately limited candidate finder, not a complete email-address parser. Suppression uses a conservative case-insensitive key and retains source spellings.

[Topic index](../README.md) · [Blog index](../../README.md)
