# Self-rewarding training: objective fidelity and evaluator drift

This study separates candidate generation, training-time judgement and independent evaluation.

[Read the study](self-rewarding-training-loops.md)

## Included implementation

The DPO implementation now sums response-masked token log probabilities and detaches reference ratios. Numerical tests verify both loss directions, prompt-mask exclusion and an actual trainable parameter update. A swapped-order judge audit rejects a deliberately style-biased fixture judge.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

Use `sequence_logprob`, `dpo` and `judge_audit`. The tiny gradient test is an objective-fidelity fixture, not a preference-learning quality result.

## Files

- [preference.py](preference.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [self-rewarding-training-loops.md](self-rewarding-training-loops.md) — Article.
- [test_preference.py](test_preference.py) — Local regression checks.

## Remaining work

No production judge or iterative self-rewarding trainer has been validated. Sequence masks and external correctness labels remain caller responsibilities; style-controlled audits must pass before using model-generated preferences.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study self-rewarding-training-loops --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Both trained policies scored zero on held-out operand combinations across the five seeds, while the unchanged policy averaged 9%. Accepted preference pairs did not produce combinatorial generalisation in this finite task. This does not evaluate free-form self-judging language models.

See the [article](self-rewarding-training-loops.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
