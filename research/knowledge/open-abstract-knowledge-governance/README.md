# OpenAbstract: correction, evidence and the public reading view

OpenAbstract studies how a knowledge platform should preserve history while changing what readers see after a correction.

[Read the study](open-abstract-knowledge-governance.md)

## Included implementation

The correction ledger now separates immutable claim versions, append-only review events and the default reading pointer. Challenges and appeals suspend an affected default; appeals identify an earlier decision. Missing support defers rather than manufacturing corroboration.

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
uv run --no-project --python .venv/bin/python python governance.py
```

The equal-permission fixture retains rejected and deferred versions. Duplicate evidence IDs do not become additional votes. A workflow decision is distinct from evidence being true.

## Files

- [governance.py](governance.py) — Runnable implementation.
- [open-abstract-knowledge-governance.md](open-abstract-knowledge-governance.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_governance.py](test_governance.py) — Local regression checks.

## Remaining work

Forty replay histories exercise a repeated fixture pattern, not a held-out governance benchmark. The evidence rule consumes explicit external support labels; majority voting, independent-source weighting, and adversarial dispute families remain unimplemented. An append-only SQLite command journal now supports persistent replay.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study open-abstract-knowledge-governance --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The command journal replayed 100 synthetic cases per seed with zero replay errors. Support labels were supplied explicitly, so this demonstrates persistent state transitions rather than independent evidence assessment or better human governance.

See the [article](open-abstract-knowledge-governance.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
