+++
title = "Temporal attention: elapsed time inside the prediction"
date = "2026"
description = "A saved elapsed-time attention pilot finds task-dependent results against timestamp features and a last-observation baseline."
draft = false
id = "research/temporal-attention-that-changes-predictions"
type = "research-note"
author = "tegridydev"
topic = "architecture-experiments"
related = ["research/reflective-transformer-memory-and-adaptation"]
status = "pilot"
updated = "2026-09-08"
+++

# [td] tegridydev | Temporal attention: elapsed time inside the prediction

*method proposal and experimental protocol*

I originally played with temporal attention by reweighting attention maps after a model had already produced its hidden states. That is useful for visualisation, but it cannot show that elapsed time changed the prediction.

This version puts time **inside** the prediction path. The question is whether an explicit age penalty helps a model use irregular observations, compared with an otherwise identical model that already receives timestamp features.


<!-- cpu-comparison:start -->
## Results

Learned decay reached 79.69% on the ordinary periodic task but fell to 62.75% under the gap shift, below the last-observation baseline at 71.48%. On switching data it was close to the simpler controls and near chance after the shift. The result depends on the generator and arrival gaps; it does not establish universal recency weighting.

Two synthetic temporal generators, frozen final and gap-shift sets, development-selected checkpoints; no universal recency or real-arrival-process claim.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| periodic-features · final · accuracy | 0.789453 | 0.01265 |
| periodic-features · shift · accuracy | 0.636133 | 0.018639 |
| periodic-fixed · final · accuracy | 0.790039 | 0.0118 |
| periodic-fixed · shift · accuracy | 0.627539 | 0.016596 |
| periodic-learned · final · accuracy | 0.796875 | 0.010653 |
| periodic-learned · shift · accuracy | 0.627539 | 0.016596 |
| periodic-position · final · accuracy | 0.742578 | 0.0013102 |
| periodic-position · shift · accuracy | 0.713867 | 0.0013811 |
| periodic · last observation · final · accuracy | 0.743164 | 0 |
| periodic · last observation · shift · accuracy | 0.714844 | 0 |
| switching-features · final · accuracy | 0.727734 | 0.0021171 |
| switching-features · shift · accuracy | 0.506445 | 0.010509 |
| switching-fixed · final · accuracy | 0.72832 | 0.00368 |
| switching-fixed · shift · accuracy | 0.500391 | 0.0075833 |
| switching-learned · final · accuracy | 0.728711 | 0.004223 |
| switching-learned · shift · accuracy | 0.500195 | 0.0073535 |
| switching-position · final · accuracy | 0.730078 | 0.00087346 |
| switching-position · shift · accuracy | 0.504883 | 0 |
| switching · last observation · final · accuracy | 0.730469 | 0 |
| switching · last observation · shift · accuracy | 0.504883 | 0 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.
<!-- cpu-comparison:end -->

## Earlier pilot results

The temporal bias helped on the switching fixture, but the last-observation baseline led the periodic fixture. The task and baseline change the conclusion; there is no general win for recency here.

| Task | Condition | Accuracy | Shifted accuracy |
| --- | --- | --- | --- |
| switching | position | 61.7188% | 43.7500% |
| switching | features | 70.3125% | 39.8438% |
| switching | fixed | 73.4375% | 57.8125% |
| switching | learned | 73.4375% | 57.8125% |
| switching | last_observation | 71.0938% | 57.8125% |
| periodic | position | 54.6875% | 57.8125% |
| periodic | features | 46.8750% | 51.5625% |
| periodic | fixed | 57.0312% | 61.7188% |
| periodic | learned | 57.0312% | 61.7188% |
| periodic | last_observation | 74.2188% | 67.9688% |

Seed 1729; 40 steps; 256 training and 128 test episodes per task. Fixed steps, with no final-data tuning. Multi-seed and broader temporal processes remain untested.

Records: [smoke-results.json](smoke-results.json). These values are transcribed from the saved records, not newly rerun experiments.

## The actual attention bias

For query time `t_q` and observation time `t_i`, start with the ordinary content score and subtract an age term:

```text
s_i = (qᵀ k_i) / sqrt(d_k) − λ · (t_q − t_i) / τ + m_i
a = softmax(s)
```

`m_i` masks padding, future events and anything unavailable at query time. Event time and arrival time are different fields when delayed reports exist; an observation about yesterday cannot influence yesterday’s prediction if it only arrived today.

`λ=0` recovers ordinary attention over the same eligible observations. Larger `λ` prefers more recent evidence. That is a modelling choice, not a claim that newer evidence is always better.

There is also a useful limitation in the rule: adding the same constant age to every eligible observation subtracts the same value from every logit, which softmax cancels. The bias depends on **relative ages**, not absolute staleness. Explicit age features therefore matter if the model should become less certain simply because all evidence is old.

## Two tasks that pull in different directions

The first generator has a hidden binary state that flips stochastically over time. Sixteen noisy observations arrive after irregular gaps, then the model predicts the state after another gap. Recent evidence should often be more useful because the hidden state can change after old observations.

The second generator is periodic with a hidden phase. Older observations can help infer that phase, so aggressively decaying them may hurt. This is an important control: I do not want to design a benchmark where recency is guaranteed to win by construction.

Both tasks use independent episodes and separate train/development/final streams. Add a final shift set with larger observation/query gaps and never tune on it.

## Fair model comparison

Use the same width-64, two-layer, four-head observation encoder and final query-to-observation readout for every condition. Compare:

| Condition | Time path |
| --- | --- |
| Position only | Order/value, ordinary attention |
| Timestamp features | Explicit age features, ordinary attention |
| Fixed decay | Same features + fixed `λ=1` age bias |
| Learned decay | Same features + learned non-negative `λ` per head |

The timestamp-feature baseline is the important one. If decay only beats the position-only model, I have shown that **time information** helps, not that the particular decay rule helps.

Also keep two cheap baselines: training-majority prediction and the most recent reported value.

Report accuracy, negative log likelihood and Brier score, broken down by final observation age. Use paired episode comparisons and separate training-seed variation. Shuffle ages inside episodes as a diagnostic; if nothing changes, the model may not be using time at all.

A dashboard can show observation values, ages, masks, head weights and probabilities, but plots are inspection tools. The result is predictive performance under controlled conditions.

**What would weaken the idea:** learned decay losing to timestamp features means explicit age bias is unnecessary. Strong performance on switching data but poor periodic/shift performance says the recency prior is task-specific. An empty eligible context needs an explicit fallback rather than a NaN or invented uniform distribution.

The experiment I want is not “temporal attention improves transformers”. It is: **on which time structures does a simple recency bias help after the model already knows the timestamps, and where does that bias become the wrong prior?**

## Implementation

Both irregular-time generators now produce targets after the last query gap. Position-only, explicit-age, fixed-decay and learned-decay models receive identical observations; a last-observation baseline and longer-gap shift set make the comparison inspectable. Tests cover reproducible episodes and trainable decay.

Start with [experiment.py](experiment.py); the [module README](README.md) lists setup, commands and every supporting file.

Bias-only softmax still has the uniform-age-shift cancellation derived in the article. These models also receive explicit age features, which supply an absolute-age path; that distinction is part of the intervention.

## Earlier observations

On switching episodes, learned decay achieved 73.4% accuracy against 71.1% for the last-observation baseline. On periodic episodes it achieved 57.0%, below the last-observation baseline's 74.2%. Learned decay reached 57.8% on the longer-gap switching set. This one-seed run supports checking task dependence and shift sensitivity, not a general recency advantage. Shift gaps are 19, 37 and 83 steps so they do not all alias the twenty-step periodic cycle. See the [saved result](smoke-results.json) for the exact values and run scope.

## References

1. Ashish Vaswani and colleagues. *Attention Is All You Need*. 2017. [arXiv:1706.03762, version 7](https://arxiv.org/html/1706.03762v7), especially sections 3.2.1–3.2.3.

## Status

The results apply to the stated datasets and controls. Further experiments described here are proposals unless accompanied by a recorded result.

[Research index](../../README.md)
