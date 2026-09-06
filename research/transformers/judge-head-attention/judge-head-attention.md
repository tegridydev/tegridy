# [td] tegridydev | Judge-head attention: measuring contextual influence

*design study and proposed evaluation*

Judge-head attention reserves one attention head as a little referee. Every worker head computes normally, the judge produces a context-dependent signal, and that signal gates how strongly the worker outputs contribute before the final projection.

The first research question is **influence allocation**, not speed. Because all worker heads already ran, a small gate value does not mean less compute. Conditional skipping would need a different mechanism that predicts the choice before the expensive work happens.

## Define what the judge actually controls

For each token, ordinary attention produces worker outputs `o[t,h]`. The judge output goes through a small MLP and sigmoid to produce `g[t,h]`, and the final attention output concatenates gated workers plus the ungated judge.

Raw sigmoid gates, clamped gates and executed gates should be logged separately. Otherwise a dashboard can display one number while the model actually used another after thresholds or minimum clamps.

A gate is also not automatically a faithful importance score. If I want to say a worker mattered, I need to intervene on that worker’s pre-output-projection representation and measure the resulting query loss/accuracy.

## A clean causal recall task

Generate sequences with distinct key/value pairs followed later by query markers asking for the associated values. Reserve key, value and query positions as a unit, assert that every referenced pair is strictly earlier than its causal query, then fill distractors independently of the label.

The proposed larger task uses 64-token sequences, two pairs and disjoint key/value combinations across train/development/final. Report **query-only** cross-entropy and exact query accuracy; reconstruction can exist as an auxiliary loss but should not dominate the metric.

Before trusting any neural result, keep a deterministic key/value lookup oracle and a trivial frequency baseline to verify labels and task difficulty.

## Controls that separate gating from “having another MLP”

Compare:

1. ordinary attention;
2. parameter-matched ordinary attention;
3. static learned worker scalars;
4. token-state gating MLP without a reserved judge;
5. judge-head gating.

All use the same causal mask, optimiser, token budget and common predictive evaluation loss. Add a shuffled-judge-input control. Introduce entropy penalties, clamps or hard thresholds only after the soft-gate version is understood.

The hypotheses are that judge gating beats static scalars, changes with the queried key rather than just token type, and ranks workers in a way that agrees with held-out causal interventions.

**What would weaken the idea:** if token-state gating matches the judge, the reserved head may be unnecessary. If shuffled judge features work equally well, contextual information is not doing the job I claimed. If high-gate workers are causally interchangeable or low-gate workers are essential, gate plots are not reliable contribution maps.

## If I ever want a speed claim

A later version could use intervention-derived contribution labels on training episodes and distil that signal into a **pre-attention** router that chooses a small worker subset. That would finally make skipping possible, but it becomes a distinct conditional-compute study.

Any efficiency result then needs actual prefill/decode timings, warm-up, hardware synchronisation and executed-operation accounting. A threshold-derived “pruning ratio” is only sparsity until a head is physically skipped or removed.

The point of the current study is smaller: **can one contextual signal allocate influence in a way that predicts which already-computed workers actually matter for recall?**

## What exists locally

The causal recall model now compares ordinary attention, static worker scalars, token-state gates and a reserved judge head. A deterministic key/value oracle checks labels, causal tests check masks and gradient tests confirm the gate alters executed worker contributions.

Start with [experiment.py](experiment.py); the [module README](README.md) lists setup, commands and every supporting file.

Every head is computed before gating. Saved results are one seed with a separate seeded evaluation set; they are not an independently held-out combination benchmark.

## What I actually observed

The original forty-step run failed to learn useful held-out recall: the ordinary condition scored below 1% and the three gated conditions scored 0%. Passing causal-mask and gradient tests therefore did not establish task competence. This failed smoke result is retained instead of being hidden. A fixed 400-step follow-up produced ordinary 48.4%, static 45.3%, token 39.1%, judge 38.3%. This follow-up investigates learnability on the same small task; it is not a new independent evaluation set or a full architecture benchmark. See [learning-check.json](learning-check.json). See the [saved result](smoke-results.json) for the exact values and run scope.

## References

- **William Fedus; Barret Zoph; Noam Shazeer. [Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity](https://jmlr.org/papers/v23/21-0998.html).** 2022, JMLR 23(120):1–39.

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
