+++
title = "Temporal Attention for Irregular Observations"
date = "2026"
description = "Compare learned time decay, timestamp features and a last observation baseline across synthetic switching, periodic and shifted arrival tasks."
draft = false
id = "research/temporal-attention-that-changes-predictions"
type = "research-note"
author = "tegridydev"
topic = "architecture-experiments"
related = ["research/reflective-transformer-memory-and-adaptation"]
status = "pilot"
updated = "2026-09-09"
+++

# Temporal Attention for Irregular Observations

I originally played with temporal attention by reweighting attention maps after a model had already produced its hidden states. That is useful for visualisation, but it cannot show that elapsed time changed the prediction.

This version puts time **inside** the prediction path. The question is whether an explicit age penalty helps a model use irregular observations, compared with an otherwise identical model that already receives timestamp features.

## Results

Learned decay reached 79.69% on the ordinary periodic task but fell to 62.75% under the gap shift, below the last observation baseline at 71.48%. On switching data it was close to the simpler controls and near chance after the shift. The result depends on the generator and arrival gaps; it does not establish universal recency weighting.

Two synthetic temporal generators, frozen final and gap shift sets, development selected checkpoints; no universal recency or real arrival process claim.

For percentage rows, the mean is a percentage and the standard deviation is in percentage points.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| periodic features · final · accuracy (%) | 78.945 | 1.265 |
| periodic features · shift · accuracy (%) | 63.613 | 1.864 |
| periodic fixed · final · accuracy (%) | 79.004 | 1.18 |
| periodic fixed · shift · accuracy (%) | 62.754 | 1.66 |
| periodic learned · final · accuracy (%) | 79.688 | 1.065 |
| periodic learned · shift · accuracy (%) | 62.754 | 1.66 |
| periodic position · final · accuracy (%) | 74.258 | 0.131 |
| periodic position · shift · accuracy (%) | 71.387 | 0.138 |
| periodic · last observation · final · accuracy (%) | 74.316 | 0 |
| periodic · last observation · shift · accuracy (%) | 71.484 | 0 |
| switching features · final · accuracy (%) | 72.773 | 0.212 |
| switching features · shift · accuracy (%) | 50.645 | 1.051 |
| switching fixed · final · accuracy (%) | 72.832 | 0.368 |
| switching fixed · shift · accuracy (%) | 50.039 | 0.758 |
| switching learned · final · accuracy (%) | 72.871 | 0.422 |
| switching learned · shift · accuracy (%) | 50.019 | 0.735 |
| switching position · final · accuracy (%) | 73.008 | 0.087 |
| switching position · shift · accuracy (%) | 50.488 | 0 |
| switching · last observation · final · accuracy (%) | 73.047 | 0 |
| switching · last observation · shift · accuracy (%) | 50.488 | 0 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.

## Earlier pilot results

This smaller pilot used a different protocol, so its results are not directly comparable with the later experiment.

The temporal bias helped on the switching fixture, but the last observation baseline led the periodic fixture. The task and baseline change the conclusion; there is no general win for recency here.

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

Seed 1729; 40 steps; 256 training and 128 test episodes per task. Fixed steps, with no final data tuning. Multi seed and broader temporal processes remain untested.

Records: [smoke results.json](smoke-results.json). These values are transcribed from the saved records, not newly rerun experiments.

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

Use the same width 64, two layer, four head observation encoder and final query to observation readout for every condition. Compare:

| Condition | Time path |
| --- | --- |
| Position only | Order/value, ordinary attention |
| Timestamp features | Explicit age features, ordinary attention |
| Fixed decay | Same features + fixed `λ=1` age bias |
| Learned decay | Same features + learned non negative `λ` per head |

The timestamp feature baseline is the important one. If decay only beats the position only model, I have shown that **time information** helps, not that the particular decay rule helps.

Also keep two cheap baselines: training majority prediction and the most recent reported value.

Report accuracy, negative log likelihood and Brier score, broken down by final observation age. Use paired episode comparisons and separate training seed variation. Shuffle ages inside episodes as a diagnostic; if nothing changes, the model may not be using time at all.

A dashboard can show observation values, ages, masks, head weights and probabilities, but plots are inspection tools. The result is predictive performance under controlled conditions.

**What would weaken the idea:** learned decay losing to timestamp features means explicit age bias is unnecessary. Strong performance on switching data but poor periodic/shift performance says the recency prior is task specific. An empty eligible context needs an explicit fallback rather than a NaN or invented uniform distribution.

The experiment I want is not “temporal attention improves transformers”. It is: **on which time structures does a simple recency bias help after the model already knows the timestamps, and where does that bias become the wrong prior?**

## Implementation

Both irregular time generators now produce targets after the last query gap. Position only, explicit age, fixed decay and learned decay models receive identical observations; a last observation baseline and longer gap shift set make the comparison inspectable. Tests cover reproducible episodes and trainable decay.

See [experiment.py](experiment.py); the [module README](README.md) describes usage and dependencies.

Bias only softmax still has the uniform age shift cancellation derived in the article. These models also receive explicit age features, which supply an absolute age path; that distinction is part of the intervention.

## References

1. Ashish Vaswani and colleagues. *Attention Is All You Need*. 2017. [arXiv:1706.03762, version 7](https://arxiv.org/html/1706.03762v7), especially sections 3.2.1–3.2.3.

[Research index](../../README.md)
