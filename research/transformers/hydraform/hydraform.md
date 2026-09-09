+++
title = "Hydraform: Adaptive Attention Head Mutation"
date = "2026"
description = "Examine attention head mutation, optimiser replacement and checkpoint recovery alongside fixed and random mutation controls on a synthetic task."
draft = false
id = "research/hydraform"
type = "research-note"
author = "tegridydev"
topic = "architecture-experiments"
related = ["research/tegridydev-adaptive-neural-architecture-concepts", "research/judge-head-attention"]
status = "implemented"
updated = "2026-09-09"
+++

# Hydraform: Adaptive Attention Head Mutation

*Local mutation experiment and further evaluation plans*

Hydraform explores changing attention head structure while a model trains. The interesting part is not drawing a lineage of heads; it is making sure every structural mutation becomes a **real trainable state transition** and then separating the value of adaptation from final model size, optimiser resets and unrelated architectural differences.

The [public repository](https://github.com/tegridydev/hydraform) is the project reference. The protocol here narrows the comparison; it does not report a new AG News training result.

## Recorded findings

The guided mutation averaged 95.47% accuracy, compared with 95.55% for both the fixed final and random mutation controls and 95.70% for the reset control. These synthetic results do not establish a benefit from guided mutation.

Synthetic sequence classification, equal total head width, fixed/final size/reset controls and two candidate development guided mutation. Candidate evaluation time is included. Not an upstream reproduction or AG News result.

For percentage rows, the mean is a percentage and the standard deviation is in percentage points.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| fixed final · accuracy (%) | 95.547 | 1.671 |
| fixed initial · accuracy (%) | 95.078 | 0.98 |
| guided mutation · accuracy (%) | 95.469 | 0.941 |
| random mutation · accuracy (%) | 95.547 | 1.055 |
| reset control · accuracy (%) | 95.703 | 0.916 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.

## prove the replacement optimiser sees the new weights

The [mutation fixture](test_adaptation.py) widens a head to 20, then narrows it to 12 under a parameter budget. After each mutation it compares parameter identities in the returned optimiser with every current model parameter, takes a gradient step and checks that the new projection weights change.

Save/reload must also preserve architecture and predictions. The implementation resets all Adam moments, so a fair downstream comparison needs the same reset treatment in its controls.

The historical upstream observation remains unpinned. This test supports the independent local mutation contract, not a claim about a particular upstream release or an accuracy improvement from adaptation.

## Mutation is not just another gradient step

Widening a head changes tensor shapes. Adding/removing a head changes which parameters exist. A mutation record therefore needs the parent architecture, operation, stable head IDs, old/new shapes, parameter counts, acceptance rule and resulting architecture ID.

That matters because an optimiser tracks parameter objects. If mutation replaces a projection after Adam was created, the new weights are not automatically part of the old optimiser. A model can look structurally different while some of the new parameters never receive the intended updates.

For the first study I’d use one explicit policy: after every accepted width mutation, rebuild the optimiser and reset all moment state. I am not claiming that reset is optimal; it is simply easy to reason about. Frozen and random mutation controls need matching reset opportunities so “Adam got reset” cannot masquerade as an adaptation benefit. State transfer can be a later experiment.

## Make every condition the same model except for adaptation

The earlier prototype paths differ in more than mutation, for example custom attention versus a standard Transformer encoder and different masking behaviour. A fair comparison should use the same embedding, attention implementation, feed forward block, normalisation, padding policy and classifier everywhere.

Then compare:

1. fixed architecture;
2. random structural mutations;
3. performance guided mutations.

All conditions receive the same maximum parameter budget and training token budget. Architecture decisions use a development split only; the final test partition remains untouched until the end.

Before any dataset training, a tiny fixture should prove that a width mutation has the expected shape, every intended parameter appears in the rebuilt optimiser, new weights actually change after one gradient step, padded positions stay isolated and save/reload preserves both architecture and predictions.

Run several initialisation seeds and report final accuracy/loss, total training time, peak memory, parameter count and rejected mutations, including the cost of evaluating candidate changes.

## The controls that can kill the story

If a frozen model built directly at the **final evolved architecture** performs equally well, the benefit may be final capacity rather than the path taken to get there. If random mutation matches performance guided mutation, the guidance signal has not demonstrated value. If the optimiser coverage fixture fails, no downstream accuracy comparison is worth interpreting.

That is why I see the head lineage visualisation as explanation rather than evidence. It becomes useful once the training state transition is real and the controls survive.

The upstream revision used for the earlier source observations is not pinned here, so the implementation is a reconstruction of the mutation contract. The recorded synthetic comparison includes fixed final and reset controls but found no advantage for guided mutation. Broader task evaluation is required before claiming an adaptive attention benefit.

## Implementation

An independent local attention module now widens or narrows a head, copies overlapping weights, enforces a parameter budget and rebuilds Adam with all moment state reset. Tests prove optimizer coverage, new weight updates, padding isolation and architecture aware save/reload.

See [adaptation.py](adaptation.py); the [module README](README.md) describes usage and dependencies.

`mutate` returns both the replacement optimizer and a before/after parameter identity event. Its all moment reset policy must also be applied to fixed and random controls before any quality comparison.

[Research index](../../README.md)
