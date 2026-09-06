# Mixture of Perspectives: preserving useful disagreement

Mixture of Perspectives is a decision-support study: expose competing values, factual assumptions and unresolved objections, then test whether reviewers detect important omissions.

[Read the study](mixture-of-perspectives.md)

## Included implementation

The evaluator now applies hard constraints before utility ranking, preserves Pareto alternatives and separates value-weight changes from a changed factual budget. Forty fictional cases expose both perspectives and all rejected actions.

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
python3 perspectives.py
```

All criteria use declared [0,1] scales and nonnegative weights. Ties remain multiple winners; an infeasible high-scoring action cannot win.

## Files

- [mixture-of-perspectives.md](mixture-of-perspectives.md) — Article.
- [perspectives.py](perspectives.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_perspectives.py](test_perspectives.py) — Local regression checks.

## Remaining work

Scores are hand-defined fictional utilities. The forty cases vary one scenario rather than establishing transfer to held-out wording or real decisions. Independent rubric review and wording-sensitivity evaluation remain necessary.

[Topic index](../README.md) · [Research index](../../README.md)
