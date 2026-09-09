+++
title = "Judge Head Attention: Contextual Head Gating"
date = "2026"
description = "Compare contextual attention head gating with standard attention and a token MLP control, separating initial failures from a longer recall comparison."
draft = false
id = "research/judge-head-attention"
type = "research-note"
author = "tegridydev"
topic = "architecture-experiments"
related = ["research/face-based-attention-circuits", "research/hydraform"]
status = "pilot"
updated = "2026-09-09"
+++

# Judge Head Attention: Contextual Head Gating

Judge head attention reserves one attention head as a little referee. Every worker head computes normally, the judge produces a context dependent signal, and that signal gates how strongly the worker outputs contribute before the final projection.

The first research question is **influence allocation**, not speed. Because all worker heads already ran, a small gate value does not mean less compute. Conditional skipping would need a different mechanism that predicts the choice before the expensive work happens.

## Results

The judge gate averaged 44.10% accuracy, ordinary attention 43.92% and the token MLP gate 44.84%. The small mean differences do not establish a judge specific advantage; parameter counts differ and all heads are still computed.

64 token two pair synthetic recall; disjoint key/value associations and development checkpoint selection. Gating computes all heads; parameter differences are reported, not claimed matched. Causal head importance study remains separate.

For percentage rows, the mean is a percentage and the standard deviation is in percentage points.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| judge · accuracy (%) | 44.102 | 2.747 |
| ordinary · accuracy (%) | 43.916 | 1.361 |
| static · accuracy (%) | 42.949 | 1.508 |
| token · accuracy (%) | 44.844 | 1.883 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.

## Earlier pilot results

This smaller pilot used a different protocol, so its results are not directly comparable with the later experiment.

The first run barely learned the task. A longer follow up improved accuracy, but ordinary attention still led the gated variants. The two runs answer a learnability question on the same small task; they are not independent architecture benchmarks.

| Condition | 40 steps | 400 steps |
| --- | --- | --- |
| ordinary | 0.7812% | 48.4375% |
| static | 0.0000% | 45.3125% |
| token | 0.0000% | 39.0625% |
| judge | 0.0000% | 38.2812% |

Both records use seed 1729 and the 12 token two pair fixture, with separately seeded evaluation episodes. They do not establish transfer to disjoint combinations.

Records: [learning check.json](learning-check.json), [smoke results.json](smoke-results.json). These values are transcribed from the saved records, not newly rerun experiments.

## Define what the judge actually controls

For each token, ordinary attention produces worker outputs `o[t,h]`. The judge output goes through a small MLP and sigmoid to produce `g[t,h]`, and the final attention output concatenates gated workers plus the ungated judge.

Raw sigmoid gates, clamped gates and executed gates should be logged separately. Otherwise a dashboard can display one number while the model actually used another after thresholds or minimum clamps.

A gate is also not automatically a faithful importance score. If I want to say a worker mattered, I need to intervene on that worker’s pre output projection representation and measure the resulting query loss/accuracy.

## A clean causal recall task

Generate sequences with distinct key/value pairs followed later by query markers asking for the associated values. Reserve key, value and query positions as a unit, assert that every referenced pair is strictly earlier than its causal query, then fill distractors independently of the label.

The recorded larger comparison uses 64 token sequences, two pairs and disjoint key/value combinations across train/development/final. Report **query only** cross entropy and exact query accuracy; reconstruction can exist as an auxiliary loss but should not dominate the metric.

Before trusting any neural result, keep a deterministic key/value lookup oracle and a trivial frequency baseline to verify labels and task difficulty.

## Controls that separate gating from “having another MLP”

Compare:

1. ordinary attention;
2. parameter matched ordinary attention;
3. static learned worker scalars;
4. token state gating MLP without a reserved judge;
5. judge head gating.

All use the same causal mask, optimiser, token budget and common predictive evaluation loss. Add a shuffled judge input control. Introduce entropy penalties, clamps or hard thresholds only after the soft gate version is understood.

The hypotheses are that judge gating beats static scalars, changes with the queried key rather than just token type, and ranks workers in a way that agrees with held out causal interventions.

**What would weaken the idea:** if token state gating matches the judge, the reserved head may be unnecessary. If shuffled judge features work equally well, contextual information is not doing the job I claimed. If high gate workers are causally interchangeable or low gate workers are essential, gate plots are not reliable contribution maps.

## If I ever want a speed claim

A later version could use intervention derived contribution labels on training episodes and distil that signal into a **pre attention** router that chooses a small worker subset. That would finally make skipping possible, but it becomes a distinct conditional compute study.

Any efficiency result then needs actual prefill/decode timings, warm up, hardware synchronisation and executed operation accounting. A threshold derived “pruning ratio” is only sparsity until a head is physically skipped or removed.

The point of the current study is smaller: **can one contextual signal allocate influence in a way that predicts which already computed workers actually matter for recall?**

## Implementation

The causal recall model now compares ordinary attention, static worker scalars, token state gates and a reserved judge head. A deterministic key/value oracle checks labels, causal tests check masks and gradient tests confirm the gate alters executed worker contributions.

See [experiment.py](experiment.py); the [module README](README.md) describes usage and dependencies.

Every head is computed before gating. Saved results are one seed with a separate seeded evaluation set; they are not an independently held out combination benchmark.

## References

- **William Fedus; Barret Zoph; Noam Shazeer. [Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity](https://jmlr.org/papers/v23/21-0998.html).** 2022, JMLR 23(120):1–39.

[Research index](../../README.md)
