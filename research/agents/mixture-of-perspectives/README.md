# Mixture of Perspectives: Decision Support with Disagreement

Mixture of Perspectives is a decision support study: expose competing values, factual assumptions and unresolved objections, then test whether reviewers detect important omissions.

[Read the study](mixture-of-perspectives.md)

## Implementation

The evaluator now applies hard constraints before utility ranking, preserves Pareto alternatives and separates value weight changes from a changed factual budget. Forty fictional cases expose both perspectives and all rejected actions.

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
uv run --no-project --python .venv/bin/python python perspectives.py
```

All criteria use declared [0,1] scales and nonnegative weights. Ties remain multiple winners; an infeasible high scoring action cannot win.

## Scope and limitations

Scores are hand defined fictional utilities. The forty cases vary one scenario rather than establishing transfer to held out wording or real decisions. Independent rubric review and wording sensitivity evaluation remain necessary.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study mixture-of-perspectives --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
