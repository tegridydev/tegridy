# cleaning a dataset without cleaning away its meaning

I want dataset tools to save me repetitive work.

[Read the post](dataset-discovery-and-preparation.md)

## Included implementation

The recipe engine reads CSV, JSON arrays or JSONL without numeric ID coercion. It preserves protected fields, logs whitespace edits, quarantines every conflicting duplicate, accounts for identical repeats separately and assigns deterministic group splits. Accepted, rejected, quarantined and duplicate counts reconcile to all input rows.

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
python3 prepare.py input.csv recipe.json prepared.json
```

The supplied recipe expects string `record_id` values. Optional `group_field` keeps children together; otherwise the ID is the split group. Hash buckets target 80/10/10 proportions without promising exact counts or class balance. Original values determine duplicate conflicts before cleaning.

## Files

- [dataset-discovery-and-preparation.md](dataset-discovery-and-preparation.md) — Article.
- [prepare.py](prepare.py) — Runnable implementation.
- [recipe.json](recipe.json) — Project-local support file.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_prepare.py](test_prepare.py) — Local regression checks.

## Remaining work

The engine supports the supplied explicit recipe operations, not arbitrary expressions or automatic schemas. Discovery providers, augmentation and an interactive row-diff screen remain extensions. Malformed JSONL rows become rejected entries; malformed whole-file JSON/CSV parsing remains a file-level error.

[Topic index](../README.md) · [Blog index](../../README.md)
