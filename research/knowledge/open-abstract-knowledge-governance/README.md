# OpenAbstract: Versioned Claims and Corrections

OpenAbstract studies how a knowledge platform should preserve history while changing what readers see after a correction.

[Read the study](open-abstract-knowledge-governance.md)

## Implementation

The correction ledger now separates immutable claim versions, append only review events and the default reading pointer. Challenges and appeals suspend an affected default; appeals identify an earlier decision. Missing support defers rather than manufacturing corroboration.

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
uv run --no-project --python .venv/bin/python python governance.py
```

The equal permission fixture retains rejected and deferred versions. Duplicate evidence IDs do not become additional votes. A workflow decision is distinct from evidence being true.

## Scope and limitations

Forty replay histories exercise a repeated fixture pattern, not a held out governance benchmark. The evidence rule consumes explicit external support labels; majority voting, independent source weighting, and adversarial dispute families remain unimplemented. An append only SQLite command journal now supports persistent replay.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study open-abstract-knowledge-governance --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
