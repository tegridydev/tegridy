# Judge-head attention: measuring contextual influence

Judge-head attention uses one head’s output to gate other heads after they have computed their representations.

[Read the study](judge-head-attention.md)

## Included implementation

The causal recall model now compares ordinary attention, static worker scalars, token-state gates and a reserved judge head. A deterministic key/value oracle checks labels, causal tests check masks and gradient tests confirm the gate alters executed worker contributions.

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

Every head is computed before gating. Saved results are one seed with a separate seeded evaluation set; they are not an independently held-out combination benchmark.

## Local result

The original forty-step run failed to learn useful held-out recall: the ordinary condition scored below 1% and the three gated conditions scored 0%. Passing causal-mask and gradient tests therefore did not establish task competence. This failed smoke result is retained instead of being hidden. A fixed 400-step follow-up produced ordinary 48.4%, static 45.3%, token 39.1%, judge 38.3%. This follow-up investigates learnability on the same small task; it is not a new independent evaluation set or a full architecture benchmark. See [learning-check.json](learning-check.json).

## Files

- [experiment.py](experiment.py) — Runnable implementation.
- [judge-head-attention.md](judge-head-attention.md) — Article.
- [learning-check.json](learning-check.json) — Recorded synthetic run; scope and provenance included.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [smoke-results.json](smoke-results.json) — Recorded synthetic run; scope and provenance included.
- [test_experiment.py](test_experiment.py) — Local regression checks.

## Remaining work

The smoke task uses twelve tokens and two pairs, not the proposed 64-token dataset or disjoint key/value-combination study. Token-MLP parameter counts are reported but not exactly matched. No pruning, skipped work or speed claim follows from these soft gates.

[Topic index](../README.md) · [Research index](../../README.md)
