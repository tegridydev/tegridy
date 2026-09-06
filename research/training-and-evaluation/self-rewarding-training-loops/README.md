# Self-rewarding training: objective fidelity and evaluator drift

This study separates candidate generation, training-time judgement and independent evaluation.

[Read the study](self-rewarding-training-loops.md)

## Included implementation

The DPO implementation now sums response-masked token log probabilities and detaches reference ratios. Numerical tests verify both loss directions, prompt-mask exclusion and an actual trainable parameter update. A swapped-order judge audit rejects a deliberately style-biased fixture judge.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
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
