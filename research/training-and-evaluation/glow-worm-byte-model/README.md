# glow-worm: an inspectable byte-language-model baseline

glow-worm starts with a small language-modelling task: predict UTF-8 bytes and measure held-out probability quality.

[Read the study](glow-worm-byte-model.md)

## Included implementation

The four-block, width-128 causal byte Transformer now trains and reports held-out bits per byte. Tests cover prefix invariance to future tokens, one-batch learning and checkpoint reload. The runner accepts separate raw-byte training/evaluation documents and rejects identical hashes across those partitions.

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
uv run --no-project --python .venv/bin/python python byte_baseline.py
```

Optional `--training-documents train.txt --evaluation-documents heldout.txt` uses local files. Multiple filenames are accepted for each option. The report identifies document hashes and scored byte counts; byte-only evaluation excludes the end-of-document control target.

## Earlier pilot result

The saved run scores 352 held-out byte targets at 7.637 bits per byte. Its final training loss is much lower than its held-out loss, which is unsurprising for repeated training on a tiny document. A uniform 256-byte baseline assigns eight bits per byte; this comparison alone is weak evidence because the learned model and unigram baselines must also be compared on the exact same scored bytes and document groups.

## Files

- [byte_baseline.py](byte_baseline.py) — Project-local support file.
- [experiment.py](experiment.py) — Runnable implementation.
- [glow-worm-byte-model.md](glow-worm-byte-model.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [smoke-results.json](smoke-results.json) — Recorded synthetic run; scope and provenance included.
- [test_experiment.py](test_experiment.py) — Local regression checks.

## Remaining work

The saved smoke run uses two self-authored documents, 32-token windows and forty optimizer steps. Incomplete tails are excluded and the first byte in each window is context-only. The separate CPU comparison uses pinned article-grouped WikiText-2 with approximately ten million available training bytes and a fixed 2.1-million-token exposure budget. A generation-quality comparison remains outside that study.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study glow-worm-byte-model --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Across five initialisation seeds, held-out loss averaged 3.360 bits per byte versus 4.570 for the unigram baseline. Each model used 2,097,152 training-token exposures from approximately ten million available bytes. This is a bounded byte-prediction result, not a full-corpus training pass or a chatbot evaluation.

See the [article](glow-worm-byte-model.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
