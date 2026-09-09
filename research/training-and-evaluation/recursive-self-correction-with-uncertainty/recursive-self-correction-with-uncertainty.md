+++
title = "LLM Self Correction: Evaluation and Stopping"
date = "2026"
description = "Evaluate helpful and harmful answer revisions, frozen stopping rules and baseline competence before drawing conclusions about LLM self correction."
draft = false
id = "research/recursive-self-correction-with-uncertainty"
type = "research-note"
author = "tegridydev"
topic = "agent-systems"
related = ["research/self-rewarding-training-loops"]
status = "implemented"
updated = "2026-09-09"
+++

# LLM Self Correction: Evaluation and Stopping

Recursive self correction sounds useful until a model confidently “fixes” an answer that was already right. I’m interested in both sides of that transition: **when does critique repair an answer, when does it damage one, and when should the system stop answering and do something else instead?**

Confidence is not proof. I treat uncertainty as a decision about the next action: answer from evidence, retrieve a dated fact, ask for missing scope, or admit that the available evidence cannot resolve the question.

## Recorded findings

The strict prompt and stopping configuration scored zero before revision, after revision and under independent sampling. Saved greedy responses commonly terminated on an initial newline. This is a failed baseline configuration, not evidence that a capable arithmetic model cannot self correct; the run cannot distinguish useful from harmful revisions.

Pinned GPT Neo digit arithmetic with exact response labels, one prompted revision and independent sampling at the same maximum output length. Actual token counts vary and are retained. Token likelihood is evaluated as a confidence proxy, not assumed calibrated.

| Recorded metric | Value |
| --- | ---: |
| independent accuracy (%) | 0 |
| initial accuracy (%) | 0 |
| revision accuracy (%) | 0 |

The [comparison record](comparison-results.json) includes the 1 recorded run, measured values, source hashes and dependency versions. This is a single fixed evaluation; no across seed uncertainty is estimated.

## keep all four revision transitions

| Before | After | Interpretation |
| --- | --- | --- |
| Wrong | Correct | Repair |
| Correct | Wrong | Damage |
| Correct | Correct | Retained correctness |
| Wrong | Wrong | Still wrong; wording may have changed |

The [selection fixture](test_evaluate.py) freezes a development selected threshold of `0.21`, then evaluates two final cases: one repair and one damage. The selective risk is `0.5`. A repair count alone would hide half the story.

Development and final groups must not overlap, and the final action must match the action evaluated during selection. This is a fixture for accounting and frozen selection, not evidence that self correction generally helps.

## Response needs before confidence scores

The first dataset should cover those response needs with overlapping wording. If every retrieval item contains `latest` and every answerable item looks like a textbook exercise, the system can learn style instead of evidence requirements. Refusal is also a separate policy category rather than generic “low confidence”.

Reference answers need their own audit. A factual target can depend on date, language, convention or scope, so each retained question should record the derivation/source, acceptable alternatives and conditions. Dynamic facts get an as of date and retrieval policy. Semantic similarity alone is not enough because a contradiction can still sound very similar to the reference.

## Test revision before training anything

Use 120 newly designed cases: 40 development and 80 final, grouped by underlying fact/template so paraphrases remain together. Compare:

1. direct answer;
2. answer → one critique → revision;
3. response need classification → selected action;
4. an equal token direct reasoning/resampling baseline.

That fourth condition matters because a critique loop simply gets more generation unless I control for it.

Measure the full transition table: `wrong→right`, `right→wrong`, unchanged correct and unchanged wrong. From that report repair rate, damage rate and net accuracy change. Also measure action policy accuracy, factual accuracy conditional on answering, unnecessary abstention and clarification quality.

For numerical confidence, define the event precisely, e.g. “my final factual answer is correct”, and use a proper score such as Brier plus a reliability plot. Plot selective risk against coverage under a threshold frozen on development data. A model that abstains on everything has low answered risk and zero usefulness.

**What would weaken the idea:** if critique’s gains disappear against the equal token baseline, the mechanism may just be extra sampling. If `right→wrong` damage cancels repairs, automatic revision is not helping. If confidence does not calibrate on held out data, it should not drive abstention policy.

## Better feedback, not just more feedback

One extension lets the critic request a specific external check, arithmetic verification, source lookup or a missing variable, then compares grounded correction with purely self generated critique while counting the extra cost.

Another uses disagreement between independent samples as one uncertainty feature. Agreement is not correctness, so the fixture needs shared wrong traps and calibration on development data rather than “the agents agreed” being treated as evidence.

If the pilot ever justifies training, the optimiser loop becomes its own correctness problem. Loss normalisation, gradient accumulation and final partial batches need deterministic tests so changing micro batch size does not secretly change the objective. Training bugs are not evidence for or against self correction.

The immediate goal is smaller: build an evaluator that makes helpful and harmful revisions equally visible. A self correction system should have to earn permission to rewrite a correct answer.

## Implementation

The evaluator now consumes externally scored before/after records, freezes a confidence threshold on development data, rejects overlapping split groups and accounts for one critique round, retrieval evidence and declared cost. Harmful edits stay in net change and selective risk results.

See [evaluate.py](evaluate.py); the [module README](README.md) describes usage and dependencies.

Each row needs `id`, `group`, Boolean `before`/`after`, `confidence`, `rounds: 1`, nonnegative `cost` and `action`. A retrieval action also needs a nonempty `evidence` ledger. No qualifying development threshold produces explicit abstention.

## References

- **Aman Madaan; Niket Tandon; Prakhar Gupta; Skyler Hallinan; Luyu Gao; Sarah Wiegreffe; Uri Alon; Nouha Dziri; Shrimai Prabhumoye; Yiming Yang; Shashank Gupta; Bodhisattwa Prasad Majumder; Katherine Hermann; Sean Welleck; Amir Yazdanbakhsh; Peter Clark. [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651v2).** 2023-05-25, arXiv v2; first submitted 2023-03-30.
- **Hugging Face contributors. [Trainer — Transformers documentation](https://huggingface.co/docs/transformers/main_classes/trainer).** Living documentation accessed 2026-09-05; historical dependency version unspecified.

[Research index](../../README.md)
