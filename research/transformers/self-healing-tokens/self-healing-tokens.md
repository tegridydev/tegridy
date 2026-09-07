+++
title = "Self-healing tokens: recovery without unnecessary edits"
date = "2026"
description = "A saved repair pilot compares clean-input harm and corrupt-token recovery; majority repair leads the learned models."
draft = false
id = "research/self-healing-tokens"
type = "research-note"
author = "tegridydev"
topic = "architecture-experiments"
related = ["research/tegridydev-adaptive-neural-architecture-concepts"]
status = "pilot"
updated = "2026-09-08"
+++

# [td] tegridydev | Self-healing tokens: recovery without unnecessary edits

*controlled denoising proposal*

“Self-healing tokens” sounds much more dramatic than the first experiment actually is. I’m testing a simple question on redundant synthetic records: **does separating “should I edit this position?” from “what value should replace it?” improve recovery without unnecessarily changing clean tokens?**

This is offline denoising with known corruption. It is not a model rewriting its own weights, deciding that unusual language is wrong or establishing truth in arbitrary text.


<!-- cpu-comparison:start -->
## Recorded findings

Majority repair recovered more corrupted positions than either learned model at every tested severity. At 15% corruption its recovery rate was 70.99%, versus about 12% for the learned models. Checksum abstention suppressed edits but also suppressed recovery; these results do not support general-text repair claims.

Grouped repeated-record synthetic repair, three frozen severity levels and checksum abstention; five initialisation seeds in this comparison. No general-text repair claim.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| 0 · 15 · gated · clean false edit | 0.00544131 | 0.0014857 |
| 0 · 15 · gated · corrupt recovery | 0.120201 | 0.00425 |
| 0 · 15 · gated checksum · clean false edit | 0 | 0 |
| 0 · 15 · gated checksum · corrupt recovery | 0.0166189 | 0.0019877 |
| 0 · 15 · identity · clean false edit | 0 | 0 |
| 0 · 15 · identity · corrupt recovery | 0 | 0 |
| 0 · 15 · majority · clean false edit | 0.00025546 | 0 |
| 0 · 15 · majority · corrupt recovery | 0.709885 | 0 |
| 0 · 15 · ordinary · clean false edit | 0.0051603 | 0.00089684 |
| 0 · 15 · ordinary · corrupt recovery | 0.122206 | 0.0046864 |
| 0 · 15 · ordinary checksum · clean false edit | 0 | 0 |
| 0 · 15 · ordinary checksum · corrupt recovery | 0.019914 | 0.0035601 |
| 0 · 35 · gated · clean false edit | 0.0168045 | 0.0049296 |
| 0 · 35 · gated · corrupt recovery | 0.0993394 | 0.0040062 |
| 0 · 35 · gated checksum · clean false edit | 0 | 0 |
| 0 · 35 · gated checksum · corrupt recovery | 0.000377477 | 0.00056271 |
| 0 · 35 · identity · clean false edit | 0 | 0 |
| 0 · 35 · identity · corrupt recovery | 0 | 0 |
| 0 · 35 · majority · clean false edit | 0.00115779 | 0 |
| 0 · 35 · majority · corrupt recovery | 0.442277 | 0 |
| 0 · 35 · ordinary · clean false edit | 0.0175323 | 0.003618 |
| 0 · 35 · ordinary · corrupt recovery | 0.0983328 | 0.0039452 |
| 0 · 35 · ordinary checksum · clean false edit | 0 | 0 |
| 0 · 35 · ordinary checksum · corrupt recovery | 0.000503303 | 0.00028135 |
| 0 · 6 · gated · clean false edit | 0.028343 | 0.011412 |
| 0 · 6 · gated · corrupt recovery | 0.0747053 | 0.0026837 |
| 0 · 6 · gated checksum · clean false edit | 0 | 0 |
| 0 · 6 · gated checksum · corrupt recovery | 0 | 0 |
| 0 · 6 · identity · clean false edit | 0 | 0 |
| 0 · 6 · identity · corrupt recovery | 0 | 0 |
| 0 · 6 · majority · clean false edit | 0.0055142 | 0 |
| 0 · 6 · majority · corrupt recovery | 0.155055 | 0 |
| 0 · 6 · ordinary · clean false edit | 0.0289495 | 0.0071366 |
| 0 · 6 · ordinary · corrupt recovery | 0.0749911 | 0.0044541 |
| 0 · 6 · ordinary checksum · clean false edit | 0 | 0 |
| 0 · 6 · ordinary checksum · corrupt recovery | 0 | 0 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.
<!-- cpu-comparison:end -->

## Earlier pilot results

Majority repair beat both learned models on this fixture. Keeping the identity baseline matters too: avoiding edits protects clean tokens but leaves corrupt ones unrepaired.

| Condition | Corrupt-token recovery | Clean false edits | Whole-record accuracy |
| --- | --- | --- | --- |
| identity | 0.0000% | 0.0000% | 10.9375% |
| majority | 69.7842% | 0.0000% | 78.1250% |
| ordinary | 14.3885% | 0.0000% | 20.3125% |
| gated | 9.3525% | 0.0000% | 10.9375% |

Seed 1729; 40 training steps; 384/64/64 clean records for training/development/final evaluation. The gated threshold was selected on development records only.

Records: [smoke-results.json](smoke-results.json). These values are transcribed from the saved records, not newly rerun experiments.

## Give the task enough structure to be checkable

A clean record contains five values from `v00`–`v15`, repeated three times, followed by a modulo-16 checksum:

```text
v02 v05 v01 v03 v04 SEP
v02 v05 v01 v03 v04 SEP
v02 v05 v01 v03 v04 v15
```

Only the fifteen repeated data positions are corrupted in the main task. Each eligible position can remain clean, become `MASK`, or be substituted with a different valid value. Store the clean record, corrupted record and exact change mask.

Repetition makes many cases recoverable, while the checksum supplies extra consistency evidence without uniquely identifying every original. Some inputs are genuinely ambiguous—for example three disagreeing copies can leave multiple plausible originals. The evaluator knows the generated target; the repair model does **not** get to use that target as evidence.

Split 30,000 distinct clean records before generating corruption. All variants of one clean record stay in its split. Training resamples corruption; final evaluation freezes variants at several rates plus a harder 0.30 condition and a separate checksum-corruption stress test.

## Detection and recovery are separate outputs

Use a small bidirectional Transformer with two heads at each data position:

- a binary detector estimates whether the observed token was corrupted;
- a 16-way recovery head predicts the clean value.

Train both detector loss and recovery loss over the fifteen data positions. Recovery is trained on clean positions too, so the model is rewarded for preserving valid inputs rather than learning that every token wants rewriting.

At inference, the recovery prediction is applied only when detector probability exceeds a threshold chosen on development data subject to a 1% clean-position false-edit constraint. If no useful threshold satisfies that, abstention is an acceptable result.

## The rule baseline is supposed to be hard to beat

Compare:

1. identity/no repair;
2. majority repair across the three copies;
3. ordinary denoiser that predicts every position;
4. detector-gated denoiser;
5. oracle-location gating as a diagnostic only.

The majority rule can still fail when two copies share the same wrong substitution or no pair agrees. It also checks checksum consistency without forcing an arbitrary value just to make the sum work.

Report detector precision/recall, corrupted-position recovery, false edits on clean positions, whole-record exact recovery, unresolved positions and net token errors removed. Break results down by mask/substitution, corruption rate and agreement pattern. Whole-record accuracy and token repair answer different questions, so keep both.

The oracle-location condition tells me whether the bottleneck is **finding damaged positions** or **reconstructing them**. It is not a deployable competitor.

**What would weaken the idea:** if majority voting stays stronger, the neural method has not earned its complexity. If a detector can identify corruption but the recovery head still guesses badly, detection and repair should not be collapsed into one “healing score”. If the threshold edits clean tokens to gain recovery, show that trade-off rather than hiding it in average accuracy.

Masked-language modelling is obvious prior context for reconstructing hidden input. The narrower question here is whether an explicit edit decision improves preservation under a controlled corruption process.

I’d only move toward less synthetic text after the learned system can beat or meaningfully complement the stupid-simple majority rule. Right now that rule is exactly the kind of baseline I want: annoyingly competent and impossible to impress with a fancy architecture diagram.

## Implementation

The detector/recovery Transformer now trains beside a same-backbone ordinary denoiser and compares both with identity and majority repair. Clean records are split before corruption. The gate threshold uses development data under a 1% clean-edit constraint, with explicit abstention if no threshold qualifies.

Start with [experiment.py](experiment.py); the [module README](README.md) lists setup, commands and every supporting file.

Report corrupted-position recovery, clean false edits and whole-record accuracy together. A development clean-edit constraint is not a guarantee on unseen records. The majority rule is a strong task-specific baseline and must remain visible.

## Earlier observations

On the saved held-out fixture, majority repair recovered 69.8% of corrupted positions, the ordinary denoiser 14.4%, and the gated model 9.4%. All three measured zero false edits on clean positions in this small sample. The gated threshold selected on development data was 0.0, so this run did not demonstrate useful selective abstention. The simple rule remains substantially stronger; longer or more complicated models are not justified by this result alone. See the [saved result](smoke-results.json) for the exact values and run scope.

## References

1. Jacob Devlin, Ming-Wei Chang, Kenton Lee and Kristina Toutanova. *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. 2018, revised 2019. [arXiv:1810.04805, version 2](https://arxiv.org/html/1810.04805v2), especially section 3.1.

## Status

The results apply to the stated datasets and controls. Further experiments described here are proposals unless accompanied by a recorded result.

[Research index](../../README.md)
