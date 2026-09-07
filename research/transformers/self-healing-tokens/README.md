# Self-healing tokens: recovery without unnecessary edits

This study separates corruption detection from value recovery on redundant synthetic records.

[Read the study](self-healing-tokens.md)

## Included implementation

The detector/recovery Transformer now trains beside a same-backbone ordinary denoiser and compares both with identity and majority repair. Clean records are split before corruption. The gate threshold uses development data under a 1% clean-edit constraint, with explicit abstention if no threshold qualifies.

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
uv run --no-project --python .venv/bin/python python experiment.py --steps 40
```

The earlier standard-library references have their own self-tests:

```bash
uv run --no-project --python .venv/bin/python python repair_reference.py
```

Report corrupted-position recovery, clean false edits and whole-record accuracy together. A development clean-edit constraint is not a guarantee on unseen records. The majority rule is a strong task-specific baseline and must remain visible.

## Earlier pilot result

On the saved held-out fixture, majority repair recovered 69.8% of corrupted positions, the ordinary denoiser 14.4%, and the gated model 9.4%. All three measured zero false edits on clean positions in this small sample. The gated threshold selected on development data was 0.0, so this run did not demonstrate useful selective abstention. The simple rule remains substantially stronger; longer or more complicated models are not justified by this result alone.

## Files

- [experiment.py](experiment.py) — Runnable implementation.
- [repair_reference.py](repair_reference.py) — Project-local support file.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [self-healing-tokens.md](self-healing-tokens.md) — Article.
- [smoke-results.json](smoke-results.json) — Recorded synthetic run; scope and provenance included.
- [test_experiment.py](test_experiment.py) — Local regression checks.

## Remaining work

The saved run is a small synthetic pilot, not general text repair. Checksum validation remains in the rule reference rather than a learned post-filter. The separate CPU comparison now records five seeds, equal optimiser-step budgets and three corruption severities; those additions do not establish general-text repair.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study self-healing-tokens --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Majority repair recovered more corrupted positions than either learned model at every tested severity. At 15% corruption its recovery rate was 70.99%, versus about 12% for the learned models. Checksum abstention suppressed edits but also suppressed recovery; these results do not support general-text repair claims.

See the [article](self-healing-tokens.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
