# cleaning a dataset without cleaning away its meaning

I want dataset tools to save me repetitive work.

[Read the post](dataset-discovery-and-preparation.md)

## Included implementation

The recipe engine reads CSV, JSON arrays or JSONL without numeric ID coercion. It preserves protected fields, logs whitespace edits, quarantines every conflicting duplicate, accounts for identical repeats separately and assigns deterministic group splits. Accepted, rejected, quarantined and duplicate counts reconcile to all input rows.

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
uv run --no-project --python .venv/bin/python python prepare.py input.csv recipe.json prepared.json
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

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study dataset-discovery-and-preparation --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The 11,592 input rows were accounted for as 9,411 accepted rows, 941 duplicates, 1,237 quarantined rows, and three rejected rows. The split check found no group leakage. This establishes accounting for the supplied synthetic recipe, not improved downstream model quality.

See the [article](dataset-discovery-and-preparation.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
