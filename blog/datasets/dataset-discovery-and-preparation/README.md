# Dataset Cleaning Without Losing IDs or Meaning

I want dataset tools to save me repetitive work.

[Read the post](dataset-discovery-and-preparation.md)

## Implementation

The recipe engine reads CSV, JSON arrays or JSONL without numeric ID coercion. It preserves protected fields, logs whitespace edits, quarantines every conflicting duplicate, accounts for identical repeats separately and assigns deterministic group splits. Accepted, rejected, quarantined and duplicate counts reconcile to all input rows.

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
uv run --no-project --python .venv/bin/python python prepare.py input.csv recipe.json prepared.json
```

The supplied recipe expects string `record_id` values. Optional `group_field` keeps children together; otherwise the ID is the split group. Hash buckets target 80/10/10 proportions without promising exact counts or class balance. Original values determine duplicate conflicts before cleaning.

## Scope and limitations

The engine supports the supplied explicit recipe operations, not arbitrary expressions or automatic schemas. Discovery providers, augmentation and an interactive row diff screen remain extensions. Malformed JSONL rows become rejected entries; malformed whole file JSON/CSV parsing remains a file level error.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study dataset-discovery-and-preparation --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
