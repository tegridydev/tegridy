# glow-worm: an inspectable byte-language-model baseline

glow-worm starts with a small language-modelling task: predict UTF-8 bytes and measure held-out probability quality.

[Read the study](glow-worm-byte-model.md)

## Included implementation

The four-block, width-128 causal byte Transformer now trains and reports held-out bits per byte. Tests cover prefix invariance to future tokens, one-batch learning and checkpoint reload. The runner accepts separate raw-byte training/evaluation documents and rejects identical hashes across those partitions.

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
python3 byte_baseline.py
```

Optional `--training-documents train.txt --evaluation-documents heldout.txt` uses local files. Multiple filenames are accepted for each option. The report identifies document hashes and scored byte counts; byte-only evaluation excludes the end-of-document control target.

## Local result

The saved run scores 352 held-out byte targets at 7.637 bits per byte. Its final training loss is much lower than its held-out loss, which is unsurprising for repeated training on a tiny document. A uniform 256-byte baseline assigns eight bits per byte; this comparison alone is weak evidence because the learned model and unigram baselines must also be compared on the exact same scored bytes and document groups.

## Files

- [byte_baseline.py](byte_baseline.py) — Project-local support file.
- [experiment.py](experiment.py) — Runnable implementation.
- [glow-worm-byte-model.md](glow-worm-byte-model.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [smoke-results.json](smoke-results.json) — Recorded synthetic run; scope and provenance included.
- [test_experiment.py](test_experiment.py) — Local regression checks.

## Remaining work

The saved smoke run uses two self-authored documents, 32-token windows and forty optimizer steps. Incomplete tails are excluded and the first byte in each window is context-only. The ten-million-byte corpus study, corpus-level grouping and generation comparison remain unrun.

[Topic index](../README.md) · [Research index](../../README.md)
