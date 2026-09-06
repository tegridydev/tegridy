# Self-healing tokens: recovery without unnecessary edits

This study separates corruption detection from value recovery on redundant synthetic records.

[Read the study](self-healing-tokens.md)

## Included implementation

The detector/recovery Transformer now trains beside a same-backbone ordinary denoiser and compares both with identity and majority repair. Clean records are split before corruption. The gate threshold uses development data under a 1% clean-edit constraint, with explicit abstention if no threshold qualifies.

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
python3 experiment.py --steps 40
```

The earlier standard-library references have their own self-tests:

```bash
python3 repair_reference.py
```

Report corrupted-position recovery, clean false edits and whole-record accuracy together. A development clean-edit constraint is not a guarantee on unseen records. The majority rule is a strong task-specific baseline and must remain visible.

## Local result

On the saved held-out fixture, majority repair recovered 69.8% of corrupted positions, the ordinary denoiser 14.4%, and the gated model 9.4%. All three measured zero false edits on clean positions in this small sample. The gated threshold selected on development data was 0.0, so this run did not demonstrate useful selective abstention. The simple rule remains substantially stronger; longer or more complicated models are not justified by this result alone.

## Files

- [experiment.py](experiment.py) — Runnable implementation.
- [repair_reference.py](repair_reference.py) — Project-local support file.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [self-healing-tokens.md](self-healing-tokens.md) — Article.
- [smoke-results.json](smoke-results.json) — Recorded synthetic run; scope and provenance included.
- [test_experiment.py](test_experiment.py) — Local regression checks.

## Remaining work

The saved run is a small synthetic pilot, not general text repair. Checksum validation remains in the rule reference rather than a learned post-filter. Multi-seed results, matched training budgets and higher-severity corruption are still needed.

[Topic index](../README.md) · [Research index](../../README.md)
