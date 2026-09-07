+++
title = "Face-based attention circuits: a controlled feature-mixing study"
date = "2026"
description = "A saved feature-mixing pilot roughly matches its dense control and does not establish a gate-specific advantage."
draft = false
id = "research/face-based-attention-circuits"
type = "research-note"
author = "tegridydev"
topic = "architecture-experiments"
related = ["research/judge-head-attention", "research/sparse-feature-recovery"]
status = "pilot"
updated = "2026-09-08"
+++

# [td] tegridydev | Face-based attention circuits: a controlled feature-mixing study

*architecture proposal and evaluation plan*

Face-Based Attention Circuits (FBAC) is a deliberately small feature-mixing idea. Split a hidden vector into fixed coordinate slices—**faces**—then let the current token representation choose how strongly each projected slice contributes back to the residual stream.

The name is just a name. A face is not assumed to be a semantic unit, geometric object or little independent neuron society. The research question is whether **input-dependent mixing of fixed slices does anything useful beyond adding roughly the same number of dense parameters**.


<!-- cpu-comparison:start -->
## Results

FBAC averaged 82.34% on the ordinary final split, below the base model at 89.06%. Under the layout shift it averaged 58.59%, close to the dense control at 58.83% and below the static gate at 59.80%. The swap comparisons do not supply the missing matched-magnitude causal control.

Grouped 1024 operand pairs, per-mode and layout-shift evaluation, five initialisation seeds. Swap effects are not a matched-magnitude causal identification result.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| base · final · accuracy | 0.890625 | 0.10534 |
| base · layout shift · accuracy | 0.510547 | 0.10018 |
| dense · final · accuracy | 0.787109 | 0.10388 |
| dense · layout shift · accuracy | 0.588281 | 0.078798 |
| fbac · cross mode swap · accuracy | 0.819922 | 0.092216 |
| fbac · final · accuracy | 0.823438 | 0.090073 |
| fbac · layout shift · accuracy | 0.585938 | 0.078247 |
| fbac · within mode swap · accuracy | 0.817187 | 0.089275 |
| static · final · accuracy | 0.819922 | 0.13953 |
| static · layout shift · accuracy | 0.598047 | 0.10812 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.
<!-- cpu-comparison:end -->

## Earlier pilot results

The saved pilot did not establish a gate-specific advantage: the dense adapter slightly exceeded FBAC, and gate swaps did not consistently hurt it. This is a reason to improve the comparison, not evidence that conditional mixing works.

| Condition | Final accuracy |
| --- | --- |
| base | 32.8125% |
| dense | 34.3750% |
| static | 31.0547% |
| fbac | 34.1797% |

Seed 1729; 40 training steps; 768/128/128 train/development/final operand pairs. These are the saved CPU smoke settings, not the full protocol below.

Records: [smoke-results.json](smoke-results.json). These values are transcribed from the saved records, not newly rerun experiments.

## The module

Let a width-64 token representation be divided into four 16-dimensional faces. A small gate scores each face using the full token state plus that slice, then softmax produces four non-negative weights. Each face is projected back to width 64, passed through GELU and added through a residual update:

```text
z_i = x_i + sum over j=1…4 of g_{i,j} · GELU(W_j f_{i,j})
```

The full mixer adds 4,420 trainable parameters: 324 in the gates and 4,096 in the projections. All four projections execute in this soft version, so a near-zero gate is **not** a compute saving. Hard routing would be a separate mechanism and benchmark.

Gate magnitude alone also does not tell me influence because one face projection may have a much larger update norm than another. Inspect weighted update norms and actual ablation effects beside the gates.

## A task where the gate has something specific to choose

Use a synthetic sequence containing two labelled values, independent noise and one of four modes: copy left, copy right, maximum or minimum.

```text
MODE LEFT value_a RIGHT value_b NOISE value_n QUERY
```

The output is one of 32 value classes predicted at `QUERY`. The same operands can require different answers when the mode changes, while noise never determines the target. That gives me controlled “task changed” versus “nuisance changed” pairs.

Enumerate all 1,024 ordered operand pairs, split by pair into train/development/final with seed 1729 and keep every mode/noise variant of one pair together. Resample training noise, but freeze several noise draws for held-out evaluation. Add a separate layout-shift set where the labelled LEFT/RIGHT fields swap physical order without changing their meaning.

## Controls that can explain the win away

Use one shared two-layer width-64 Transformer encoder and the same classifier head everywhere. Compare:

1. base encoder;
2. dense residual adapter with almost the same parameter count;
3. static global face weights with the same projections;
4. full input-dependent FBAC.

Train with the same optimiser/checkpoint rule and several seeds. Report accuracy by mode, parameter count, full-forward latency and seed variation.

Then intervene on the mechanism. Swap gate vectors between evaluation examples while keeping recipient features/projections fixed. Do within-mode and cross-mode swaps, and zero one face update at a time. Compare examples with the same operands but different mode, then the same mode with different noise.

A convincing result needs more than concentrated-looking gates. I want task-sensitive gate behaviour, low nuisance sensitivity and an accuracy/intervention advantage over the dense/static controls.

**What would weaken the idea:** if the dense adapter performs equally well, extra capacity probably explains the gain. If static weights match FBAC, conditional routing was unnecessary. If gate swaps barely change behaviour, the model is not relying strongly on the proposed mechanism. If face roles change completely across seeds, interpretability claims need to stay very modest.

Switch Transformers is useful broad prior context for conditional routing, but FBAC is not sparse expert execution. It is feature mixing inside one representation.

The current synthetic task is intentionally small because I want the gate to earn its complexity before trying arithmetic, natural language or large-model circuit claims.

## Implementation

FBAC now trains beside base, dense-adapter and static-mixture controls on frozen operand-pair splits. The implementation checks the exact 4,420-parameter mixer, gate gradients and checkpoint reloads. Final evaluation includes gate permutations within the same task mode and across modes.

Start with [experiment.py](experiment.py); the [module README](README.md) lists setup, commands and every supporting file.

All four task modes for an operand pair stay together. Noise is resampled after pair allocation. Gate swaps intervene on computed mixture weights while preserving the recipient features and projections.

## Earlier observations

In the saved 40-step, seed-1729 run, FBAC accuracy was 34.2%, compared with 34.4% for the dense adapter and 32.8% for the base model. Within-mode gate swaps gave 34.0%; cross-mode swaps gave 34.6%. These small, mixed differences do not support a gate-specific advantage. The useful next experiment is a sufficiently trained, multi-seed comparison with matched interventions. See the [saved result](smoke-results.json) for the exact values and run scope.

## Related public work

[Face-Based-Attention-Circuits](https://github.com/tegridydev/Face-Based-Attention-Circuits) is relevant to this topic. The methods and evaluation settings in this article are proposed unless explicitly identified as observations of that repository. A related project link does not establish that all features described here are implemented.

## References

1. William Fedus, Barret Zoph and Noam Shazeer. *Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity*. 2021, revised 2022. [arXiv:2101.03961, version 3](https://arxiv.org/abs/2101.03961v3).

## Status

The results apply to the stated datasets and controls. Further experiments described here are proposals unless accompanied by a recorded result.

[Research index](../../README.md)
