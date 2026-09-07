# Arithmetic across notations: testing causal transfer

The same addition can be written with digits or English words.

[Read the study](arithmetic-across-notations.md)

## Included implementation

The intervention runner now checks prompt/completion token boundaries, modifies selected features only at the last prompt position, scores every answer token and removes hooks even after errors. A tiny causal fixture verifies score arithmetic and an actual intervention effect.

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
uv run --no-project --python .venv/bin/python python intervene.py /path/to/local/model "Calculate 2 + 3. Answer:" " 5" --hook MODULE_PATH --features 0
```

The earlier standard-library references have their own self-tests:

```bash
uv run --no-project --python .venv/bin/python python protocol_reference.py
```

Install `requirements-model.txt` only for the optional local Hugging Face loader. It uses `local_files_only=True` and disables remote model code; it does not download weights. Supply an exact named module exposing `[batch,position,feature]`. A zero ablation can measure broad damage, so it is not sufficient evidence of arithmetic specificity.

## Files

- [arithmetic-across-notations.md](arithmetic-across-notations.md) — Article.
- [intervene.py](intervene.py) — Runnable implementation.
- [protocol_reference.py](protocol_reference.py) — Project-local support file.
- [requirements-model.txt](requirements-model.txt) — Optional local model-loader dependencies.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_intervene.py](test_intervene.py) — Local regression checks.

## Remaining work

The study adapter evaluates a pinned GPT-Neo checkpoint against the development-only two-notation feasibility gate. Availability of a checkpoint does not mean it passes that gate. Candidate discovery, matched controls and the full within/cross-notation experiment remain unrun. The optional Transformers loader is not covered by the local model-free tests.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study arithmetic-across-notations --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

This checkpoint and strict prompt/stopping configuration failed the development competence gate in both notations. No component discovery or final transfer evaluation was run. As in the self-correction setup, this does not isolate arithmetic ability from response formatting and early newline termination.

See the [article](arithmetic-across-notations.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
