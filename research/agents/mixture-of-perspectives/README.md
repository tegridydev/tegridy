# Mixture of Perspectives: preserving useful disagreement

Mixture of Perspectives is a decision-support study: expose competing values, factual assumptions and unresolved objections, then test whether reviewers detect important omissions.

[Read the study](mixture-of-perspectives.md)

## Included implementation

The evaluator now applies hard constraints before utility ranking, preserves Pareto alternatives and separates value-weight changes from a changed factual budget. Forty fictional cases expose both perspectives and all rejected actions.

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
uv run --no-project --python .venv/bin/python python perspectives.py
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

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study mixture-of-perspectives --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The perspectives disagreed in 37.3% of the fictional utility cases while producing no infeasible winners. This demonstrates sensitivity to declared value weights while retaining hard constraints; it does not evaluate moral judgement or language-model deliberation.

See the [article](mixture-of-perspectives.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
