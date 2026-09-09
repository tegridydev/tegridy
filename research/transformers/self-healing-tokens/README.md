# Self Healing Tokens: Selective Denoising Experiments

This study separates corruption detection from value recovery on redundant synthetic records.

[Read the study](self-healing-tokens.md)

## Implementation

The detector/recovery Transformer now trains beside a same backbone ordinary denoiser and compares both with identity and majority repair. Clean records are split before corruption. The gate threshold uses development data under a 1% clean edit constraint, with explicit abstention if no threshold qualifies.

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
uv run --no-project --python .venv/bin/python python experiment.py --steps 40
```

The earlier standard library references have their own self tests:

```bash
uv run --no-project --python .venv/bin/python python repair_reference.py
```

Report corrupted position recovery, clean false edits and whole record accuracy together. A development clean edit constraint is not a guarantee on unseen records. The majority rule is a strong task specific baseline and must remain visible.

## Earlier pilot result

On the saved held out fixture, majority repair recovered 69.8% of corrupted positions, the ordinary denoiser 14.4%, and the gated model 9.4%. All three measured zero false edits on clean positions in this small sample. The gated threshold selected on development data was 0.0, so this run did not demonstrate useful selective abstention. The simple rule remains substantially stronger; longer or more complicated models are not justified by this result alone.

## Scope and limitations

The saved run is a small synthetic pilot, not general text repair. Checksum validation remains in the rule reference rather than a learned post filter. The separate CPU comparison now records five seeds, equal optimiser step budgets and three corruption severities; those additions do not establish general text repair.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study self-healing-tokens --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
