# [td] tegridydev | Temporal attention: elapsed time inside the prediction

*method proposal and experimental protocol*

I originally played with temporal attention by reweighting attention maps after a model had already produced its hidden states. That is useful for visualisation, but it cannot show that elapsed time changed the prediction.

This version puts time **inside** the prediction path. The question is whether an explicit age penalty helps a model use irregular observations, compared with an otherwise identical model that already receives timestamp features.

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

## What exists locally

Both irregular-time generators now produce targets after the last query gap. Position-only, explicit-age, fixed-decay and learned-decay models receive identical observations; a last-observation baseline and longer-gap shift set make the comparison inspectable. Tests cover reproducible episodes and trainable decay.

Start with [experiment.py](experiment.py); the [module README](README.md) lists setup, commands and every supporting file.

Bias-only softmax still has the uniform-age-shift cancellation derived in the article. These models also receive explicit age features, which supply an absolute-age path; that distinction is part of the intervention.

## What I actually observed

On switching episodes, learned decay achieved 73.4% accuracy against 71.1% for the last-observation baseline. On periodic episodes it achieved 57.0%, below the last-observation baseline's 74.2%. Learned decay reached 57.8% on the longer-gap switching set. This one-seed run supports checking task dependence and shift sensitivity, not a general recency advantage. Shift gaps are 19, 37 and 83 steps so they do not all alias the twenty-step periodic cycle. See the [saved result](smoke-results.json) for the exact values and run scope.

## References

1. Ashish Vaswani and colleagues. *Attention Is All You Need*. 2017. [arXiv:1706.03762, version 7](https://arxiv.org/html/1706.03762v7), especially sections 3.2.1–3.2.3.

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
