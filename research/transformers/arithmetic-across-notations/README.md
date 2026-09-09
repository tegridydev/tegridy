# LLM Arithmetic: Digits vs Number Words

The same addition can be written with digits or English words.

[Read the study](arithmetic-across-notations.md)

## Implementation

The intervention runner now checks prompt/completion token boundaries, modifies selected features only at the last prompt position, scores every answer token and removes hooks even after errors. A tiny causal fixture verifies score arithmetic and an actual intervention effect.

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
uv run --no-project --python .venv/bin/python python intervene.py /path/to/local/model "Calculate 2 + 3. Answer:" " 5" --hook MODULE_PATH --features 0
```

The earlier standard library references have their own self tests:

```bash
uv run --no-project --python .venv/bin/python python protocol_reference.py
```

Install `requirements-model.txt` only for the optional local Hugging Face loader. It uses `local_files_only=True` and disables remote model code; it does not download weights. Supply an exact named module exposing `[batch,position,feature]`. A zero ablation can measure broad damage, so it is not sufficient evidence of arithmetic specificity.

## Scope and limitations

The study adapter evaluates a pinned GPT Neo checkpoint against the development only two notation feasibility gate. Availability of a checkpoint does not mean it passes that gate. Candidate discovery, matched controls and the full within/cross notation experiment remain unrun. The optional Transformers loader is not covered by the local model free tests.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study arithmetic-across-notations --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
