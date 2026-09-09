+++
title = "Transformer Activation Maps and Token Trajectories"
date = "2026"
description = "Track individual token occurrences, model revisions and shared projection bases so activation maps remain comparable and their limits stay visible."
draft = false
id = "research/neuron-mapping-and-token-trajectories"
type = "research-note"
author = "tegridydev"
topic = "model-interpretation-evaluation"
related = ["blog/what-a-model-map-can-show", "research/sparse-feature-recovery"]
status = "implemented"
updated = "2026-09-09"
+++

# Transformer Activation Maps and Token Trajectories

I keep building neuron viewers because activations are much easier to reason about when I can actually see them. The trap is that a nice cluster or top token list starts to look like a semantic explanation long before I have evidence for one.

This study treats the tooling as a **microscope, not a label printer**. Descriptive selectivity, geometry in a chosen projection and causal task effects remain three different evidence levels.

## Recorded findings

Six declared prompts produced 37,632 activation values, projected using a shared two dimensional basis fitted on the first prompt. Occurrence identity is retained across the capture. Category selectivity and causal effects require separate experiments.

Real GPT Neo first block activations for explicitly listed short prompts; shared PCA fitted only on the first prompt. Occurrence identity is retained; this does not establish semantic selectivity or causal circuits.

| Recorded metric | Value |
| --- | ---: |
| projected dimensions | 2 |
| prompts | 6 |
| recorded values | 37632 |

The [comparison record](comparison-results.json) includes the 1 recorded run, measured values, source hashes and dependency versions. This is a single fixed evaluation; no across seed uncertainty is estimated.

## the second occurrence of a token is another observation

The [capture fixture](test_capture.py) uses tokens `[2, 3, 2]`. Token ID 2 appears at two positions; merging them by token ID would discard occurrence identity. Across its two four wide components, the fixture retains 24 scalar records, including genuine zero activations.

For projection comparisons, fit one basis and apply that same basis to compatible captures. Separately fitted plots can rotate and make a visual movement look meaningful. A zero length path has undefined straightness, represented as `None`, rather than a fabricated perfect score.

## One activation record, no ambiguous identity

Key each observation by model revision, tokeniser revision, prompt hash, sample ID, token ID, token position, layer, component and statistic. Rendered token text is display metadata; two occurrences of `the` are different observations, and whitespace/subword variants need explicit alignment rules.

Keep raw activations separate from thresholded selections. “Not retained because it fell below a threshold” is not the same as a measured activation of zero. Record whether the hook is pre/post nonlinearity or another location so incompatible distributions do not get pooled.

Capture a whole layer tensor once per batch and analyse its feature axis offline. Running the model once per neuron is both expensive and conceptually backwards. Storage can be bounded by keeping aggregates plus a fixed number of source linked examples per neuron.

## Selectivity is a held out claim

If I call a neuron category associated, it should remain selective on new contexts after controlling for obvious shortcuts such as token frequency, length, position and orthography. Discovery examples choose candidates; final examples confirm them.

Use effect sizes and confidence intervals rather than a hand picked activation threshold, and correct for searching many neurons or reserve a held out confirmation set. Character heuristics based on one top token are weak until compared with their frequency in matched negatives.

Then intervene. Mean ablate candidate neurons and compare with same layer random controls on a **task outcome**, not just the neuron’s own activation. If selectivity survives but the intervention changes nothing, report an observational feature rather than a necessary circuit component.

## Token trajectories need one coordinate system

A line across layers only means something geometrically if the points share a compatible basis. Fitting PCA independently at each layer produces coordinates from different spaces and then draws a line between them.

Use one reference projection fitted on development data, or an explicit alignment method with reported distortion. Keep high dimensional distances beside the 2D view. Paths are keyed by token occurrence, not token string, so repeated words do not collapse into one trajectory.

For a path `p0…pL`, endpoint displacement divided by total path length is a straightness statistic bounded by one for nonzero paths. It is not a generic measure of “semantic convergence”. Compute it in the original compatible representation as well as the projection, and compare with shuffled layer/random projection controls.

## A cheap pilot

Use one small fixed model and roughly 300 short prompts across three controlled categories plus lexical/orthographic negatives. Split by sentence template/content family into discovery, validation and final groups. Capture all selected hooks in one pass, lock a small candidate set on discovery data, then evaluate selectivity and causal interventions on final prompts.

A useful extension is a **label challenge set**: for every proposed neuron description, construct examples that should and should not trigger it, with human/deterministic labels. Another compares raw neuron and sparse feature views using the same record IDs, making decomposition dependent conclusions visible.

**What would weaken the idea:** seed unstable labels, selectivity that disappears under matched negatives or no causal task effect all push the result down the evidence ladder. None of them makes the viewer useless; they just stop a visual pattern becoming a mechanistic claim.

That is the model microscope I actually want: easy enough to explore with, but annoying enough to keep asking **“did this component merely light up, or did changing it change the behaviour?”**

## Implementation

The capture API now records every selected hook in one forward pass, keys values by sample/token occurrence/component/feature, preserves measured zero and enforces a storage ceiling. It removes hooks and restores training mode on failure. Shared PCA and guarded high dimensional path straightness are supplied.

See [capture.py](capture.py); the [module README](README.md) describes usage and dependencies.

`capture(model, token_ids, hooks, model_revision, tokenizer_revision)` returns schema 1 JSON compatible records. Selected hooks must expose `[batch,position,feature]` and execute exactly once. The blog measurement viewer reads this format; model/tokenizer identities are supplied by the caller.

## Related public work

[mechamap](https://github.com/tegridydev/mechamap) is relevant to this topic. The local results in this article apply to the saved implementation and workload. Further proposals and linked upstream projects have separate scopes. A related project link does not establish that all features described here are implemented.

## References

- **Nelson Elhage; Tristan Hume; Catherine Olsson; Nicholas Schiefer; Tom Henighan; Shauna Kravec; Zac Hatfield-Dodds; Robert Lasenby; Dawn Drain; Carol Chen; Roger Grosse; Sam McCandlish; Jared Kaplan; Dario Amodei; Martin Wattenberg; Christopher Olah. [Toy Models of Superposition](https://arxiv.org/abs/2209.10652v1).** 2022-09-21, arXiv v1.

[Research index](../../README.md)
