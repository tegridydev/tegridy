# Arithmetic across notations: testing causal transfer

The same addition can be written with digits or English words.

[Read the study](arithmetic-across-notations.md)

## Included implementation

The intervention runner now checks prompt/completion token boundaries, modifies selected features only at the last prompt position, scores every answer token and removes hooks even after errors. A tiny causal fixture verifies score arithmetic and an actual intervention effect.

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
python3 intervene.py /path/to/local/model "Calculate 2 + 3. Answer:" " 5" --hook MODULE_PATH --features 0
```

The earlier standard-library references have their own self-tests:

```bash
python3 protocol_reference.py
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

No suitable pretrained arithmetic model was available for the two-notation feasibility gate. Candidate discovery, matched controls and the full within/cross-notation experiment remain unrun. The optional Transformers loader is not covered by the local model-free tests.

[Topic index](../README.md) · [Research index](../../README.md)
