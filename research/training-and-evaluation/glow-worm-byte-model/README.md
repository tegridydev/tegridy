# Glow Worm: A Small Byte Level Language Model

glow worm starts with a small language modelling task: predict UTF-8 bytes and measure held out probability quality.

[Read the study](glow-worm-byte-model.md)

## Implementation

The four block, width-128 causal byte Transformer now trains and reports held out bits per byte. Tests cover prefix invariance to future tokens, one batch learning and checkpoint reload. The runner accepts separate raw byte training/evaluation documents and rejects identical hashes across those partitions.

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
uv run --no-project --python .venv/bin/python python byte_baseline.py
```

Optional `--training-documents train.txt --evaluation-documents heldout.txt` uses local files. Multiple filenames are accepted for each option. The report identifies document hashes and scored byte counts; byte only evaluation excludes the end of document control target.

## Earlier pilot result

The saved run scores 352 held out byte targets at 7.637 bits per byte. Its final training loss is much lower than its held out loss, which is unsurprising for repeated training on a tiny document. A uniform 256-byte baseline assigns eight bits per byte; this comparison alone is weak evidence because the learned model and unigram baselines must also be compared on the exact same scored bytes and document groups.

## Scope and limitations

The saved smoke run uses two self authored documents, 32-token windows and forty optimizer steps. Incomplete tails are excluded and the first byte in each window is context only. The separate CPU comparison uses pinned article grouped WikiText-2 with approximately ten million available training bytes and a fixed 2.1-million token exposure budget. A generation quality comparison remains outside that study.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study glow-worm-byte-model --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
