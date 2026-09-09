+++
title = "Self Rewarding Training: DPO and Evaluation"
date = "2026"
description = "Check preference loss direction, answer masks and judge bias, and distinguish objective tests from a toy training run that failed to generalise."
draft = false
id = "research/self-rewarding-training-loops"
type = "research-note"
author = "tegridydev"
topic = "agent-systems"
related = ["research/recursive-self-correction-with-uncertainty"]
status = "implemented"
updated = "2026-09-09"
+++

# Self Rewarding Training: DPO and Evaluation

A self rewarding loop can look better every iteration simply because the model is getting better at satisfying its own judge. I want an independent measuring point outside that loop.

The core separation is **generator → training time judge → final evaluator**. Those roles can share model weights in some conditions, but the records and objectives stay distinct. A rising judge score is especially weak evidence when the judge itself changes during training.

## Recorded findings

Both trained policies scored zero on held out operand combinations across the five seeds, while the unchanged policy averaged 9%. Accepted preference pairs did not produce combinatorial generalisation in this finite task. This does not evaluate free form self judging language models.

Single token modulo addition policy, on policy candidate sampling and exact objective checking; comparison with unchanged and supervised policies on held out operand pairs. This is not validation of a free form self judging language model.

For percentage rows, the mean is a percentage and the standard deviation is in percentage points.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| preference · accuracy (%) | 0 | 0 |
| supervised · accuracy (%) | 0 | 0 |
| unchanged · accuracy (%) | 9 | 5.477 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.

## check the objective before trusting the judge

The [objective tests](test_preference.py) improve the preferred sequence log probability and check that the loss falls; improving the rejected sequence instead makes it rise. Reference scores remain detached, and prompt positions outside the answer mask do not affect the sequence score.

The judge check deliberately offers correct `13` against a longer polished explanation claiming `14`. A length biased judge fails. Presenting both orders tests whether position affects the choice, but passing that check would still not make the judge an independent source of truth. Preference optimisation and preference quality need separate evidence.

## First, name the loss honestly

A preferred/rejected pair is data, not a training algorithm. If training keeps only the preferred response and uses token cross entropy, that is supervised fine tuning even if a preference pair existed earlier. Pairwise ranking, DPO and reward based RL are different mechanisms and should not inherit each other’s names from a UI label.

For a DPO style condition, both preferred and rejected responses must enter the policy/reference log ratio margin under the same prompt boundary and response mask. Swapping the pair should reverse the margin. Ties need a declared policy. A supervised best answer baseline trains on the same selected preferred responses with ordinary token loss.

Self Rewarding Language Models is direct prior work for LLM generated rewards and iterative DPO. The local question is narrower: can I audit objective fidelity and evaluator drift in a small task with independently checkable answers?

## Keep the judge on a leash

Store the judge prompt, model revision, candidate order, scores, ties and reasons. Randomise and swap response order because judges can have presentation bias. Include style traps such as concise correct versus verbose confident wrong, then reverse the styling while holding substance fixed.

The final evaluator should be frozen or use a deterministic answer key wherever possible. On open ended tasks, use a fixed rubric and blinded human checks on a declared sample rather than letting the training judge certify itself.

## A bounded first loop

Start with structured extraction or small arithmetic: 1,000 training prompts, 200 validation and 300 final, grouped by template/content. Generate a small fixed number of candidates per training prompt and keep final prompts completely outside pair generation, judge tuning and stopping decisions.

Compare:

- untouched base model;
- supervised training on valid targets;
- supervised best candidate training;
- random pair preference training;
- self scored preference training.

Match training tokens, generation budget and update steps as closely as possible. One or two iterations are enough for the first study.

Measure independent task accuracy, structured output validity, judge pair accuracy, swapped order consistency, reward/accuracy correlation and response length. BLEU/ROUGE/BERTScore can be diagnostics where appropriate, but they do not replace task correctness.

The main hypotheses are that the judge can identify objectively better pairs above chance, self scored updates beat equal budget supervised training on the independent evaluator, and any gain survives style/length controls. A second iteration then tests whether the feedback loop continues helping or starts amplifying its own bias.

**What would weaken the idea:** an internal score rising while final accuracy stays flat or falls is evaluator drift, not success. If supervised best answer training performs equally well, the preference machinery has not earned its extra complexity.

## Two extensions worth keeping

A disagreement filter can accept pairs only when two differently prompted judges, or a judge plus deterministic checker, agree on a supported preference, compared with random filtering at the same retained data size. Correlated judges can still agree on errors, so the independent evaluator remains necessary.

A persistent style audit set can track whether the judge becomes easier to game across iterations. That gives the loop an explicit stop signal instead of “train again because reward went up”.

Every checkpoint should keep model/tokeniser hashes, data split, exact loss, optimiser settings and evaluator outputs. The interesting artifact is not just a new set of weights; it is a reproducible record of **what signal actually pushed them there**.

## Implementation

The DPO implementation now sums response masked token log probabilities and detaches reference ratios. Numerical tests verify both loss directions, prompt mask exclusion and an actual trainable parameter update. A swapped order judge audit rejects a deliberately style biased fixture judge.

See [preference.py](preference.py); the [module README](README.md) describes usage and dependencies.

Use `sequence_logprob`, `dpo` and `judge_audit`. The tiny gradient test is an objective fidelity fixture, not a preference learning quality result.

## Related public work

[RLTPF](https://github.com/tegridydev/RLTPF) names the related idea of feedback on a model’s reasoning process. Its inspected public tree contains a README and licence, so it does not supply a training implementation or evaluation results. The independent evaluation protocol above also applies when process feedback is the proposed reward signal.

## References

- **Weizhe Yuan; Richard Yuanzhe Pang; Kyunghyun Cho; Xian Li; Sainbayar Sukhbaatar; Jing Xu; Jason Weston. [Self-Rewarding Language Models](https://arxiv.org/abs/2401.10020v3).** 2025-03-28, arXiv v3; ICML 2024.

[Research index](../../README.md)
