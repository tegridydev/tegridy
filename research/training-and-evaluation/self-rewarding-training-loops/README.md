# Self Rewarding Training: DPO and Evaluation

This study separates candidate generation, training time judgement and independent evaluation.

[Read the study](self-rewarding-training-loops.md)

## Implementation

The DPO implementation now sums response masked token log probabilities and detaches reference ratios. Numerical tests verify both loss directions, prompt mask exclusion and an actual trainable parameter update. A swapped order judge audit rejects a deliberately style biased fixture judge.

## Run locally

Run from this directory with Python 3.12.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

Use `sequence_logprob`, `dpo` and `judge_audit`. The tiny gradient test is an objective fidelity fixture, not a preference learning quality result.

## Scope and limitations

No production judge or iterative self rewarding trainer has been validated. Sequence masks and external correctness labels remain caller responsibilities; style controlled audits must pass before using model generated preferences.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study self-rewarding-training-loops --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
