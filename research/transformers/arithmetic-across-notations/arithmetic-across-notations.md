# [td] tegridydev | Arithmetic across notations: testing causal transfer

*experimental protocol*

The same addition can be written with digits or English words. A model getting both right tells me it can handle both forms; it does **not** tell me that the same internal machinery performed the calculation.

This experiment asks the stronger question: **if I select components because they causally matter for digit-form addition, do those same components matter when the identical arithmetic is written in words, and vice versa?**

I’m treating intervention effects as the primary evidence. Activation similarity and pretty overlays can help locate candidates, but they do not get to become “the arithmetic circuit” on their own.

## What counts as shared machinery

For this study, a component is *important* when replacing its activation reduces the complete correct-answer score more than matched control interventions. It is *shared across notation* when a set discovered on digit prompts also has a held-out effect on word prompts, or the reverse.

Those are bounded operational definitions. A positive result would support shared causal involvement in this checkpoint/task; it would not establish a unique or complete addition algorithm.

Nikankin and colleagues’ work on arithmetic heuristics is useful prior context for looking beyond raw answer accuracy. This protocol tests a different surface-form transfer question.

## Dataset and split

Use non-negative additions with operands from 0 to 99. Enumerate the 5,050 unordered pairs, stratify by ones-column carry and answer length, then sample 600 pairs with seed 1729. Split by **unordered pair** into exactly 200 development, 200 discovery and 200 final pairs so every notation/order variant of one arithmetic fact stays together.

For each pair create digit and English-word prompts in both operand orders, for example:

```text
Calculate 17 + 28. Answer with digits only:
Calculate seventeen plus twenty-eight. Answer with digits only:
```

Use one deterministic number renderer and one canonical decimal target. Equal operands only keep unique prompts. Save the pair list and split before loading the model.

Choose an openly available causal LM with interceptable activations and record exact checkpoint/tokeniser revision, precision and runtime. Before component discovery, require at least 80% development exact-match accuracy in **each notation**. If the checkpoint cannot do the task, change the model or task and document that decision before touching final data.

## Score the whole answer

The answer score is the conditional log probability of the complete target continuation:

```text
S(x, y) = sum over t of log P(y_t | x, y_<t)
```

That matters because a multi-token answer cannot be evaluated from its first token. Verify the prompt/continuation token boundary explicitly and compare every prompt with its own baseline.

Generation is also reported using strict canonical exact match, with a small fixed token limit and truncations separated. Extra prose is a failure under this particular task contract.

## Discovery, intervention and controls

Start with feed-forward activation coordinates at the **final prompt token**, which gives both notations the same functional position used to begin predicting the answer. Operand-internal token alignment is a later study.

On discovery pairs, replace each tested coordinate with its layer mean estimated from development prompts. Rank by the resulting drop in correct-answer score and lock the top 20 separately for digit and word prompts.

Final evaluation runs four directions:

- digit-selected → digit prompts;
- digit-selected → word prompts;
- word-selected → word prompts;
- word-selected → digit prompts.

Compare each selected set with random same-layer sets, activation-magnitude-matched sets and **non-arithmetic number controls** such as copying an operand. Repeat the main study with both mean and zero ablation. Agreement is stronger evidence; disagreement says the result depends on the intervention distribution.

The intervention should be applied only at the final prompt position during prefill, then the answer is teacher-forced normally. Reapplying the hook to every answer position would test a different mechanism.

## Similarity stays secondary

Cosine similarity is useful for describing whether representations align, but keep its sign. Taking absolute cosine turns opposite vectors into apparent agreement. Exclude zero-norm cases and report them.

The key statistic is transfer effect: selected-set damage minus matched-control damage, bootstrapped over complete operand pairs so all variants stay together. Report both transfer directions, notation, carry status and answer length. A secondary “correct in both notations” analysis is fine if it is labelled as conditioning on baseline success.

**What would weaken the idea:** strong within-notation effects with no cross-notation transfer support notation-specific machinery. Weak effects everywhere could mean redundancy, poor discovery or a bad intervention and should not be sold as “arithmetic has no circuit”. If number-output controls break just as much, the selected components may be generic answer machinery.

The result I want is deliberately modest and specific: **which components transferred, under which intervention, for which prompts, and how far above matched disruption controls?** That is enough to make the experiment useful without claiming a universal maths circuit.

## What exists locally

The intervention runner now checks prompt/completion token boundaries, modifies selected features only at the last prompt position, scores every answer token and removes hooks even after errors. A tiny causal fixture verifies score arithmetic and an actual intervention effect.

Start with [intervene.py](intervene.py); the [module README](README.md) lists setup, commands and every supporting file.

Install `requirements-model.txt` only for the optional local Hugging Face loader. It uses `local_files_only=True` and disables remote model code; it does not download weights. Supply an exact named module exposing `[batch,position,feature]`. A zero ablation can measure broad damage, so it is not sufficient evidence of arithmetic specificity.

## References

1. Yaniv Nikankin, Anja Reusch, Aaron Mueller and Yonatan Belinkov. *Arithmetic Without Algorithms: Language Models Solve Math With a Bag of Heuristics*. 2024, revised 2025. [arXiv:2410.21272, version 2](https://arxiv.org/abs/2410.21272v2).

## Local reference example

[protocol_reference.py](protocol_reference.py) — Generates the 600 pair assignments and strict answer checks. It does not load a model or perform ablations. It uses only Python’s standard library. From this article folder, run:

```sh
python3 protocol_reference.py
```

The command runs the included deterministic checks without writing files or contacting a service. Passing these checks establishes the illustrated contract, not the broader project’s performance.

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
