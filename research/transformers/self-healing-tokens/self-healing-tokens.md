# [td] tegridydev | Self-healing tokens: recovery without unnecessary edits

*controlled denoising proposal*

“Self-healing tokens” sounds much more dramatic than the first experiment actually is. I’m testing a simple question on redundant synthetic records: **does separating “should I edit this position?” from “what value should replace it?” improve recovery without unnecessarily changing clean tokens?**

This is offline denoising with known corruption. It is not a model rewriting its own weights, deciding that unusual language is wrong or establishing truth in arbitrary text.

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

## What exists locally

The detector/recovery Transformer now trains beside a same-backbone ordinary denoiser and compares both with identity and majority repair. Clean records are split before corruption. The gate threshold uses development data under a 1% clean-edit constraint, with explicit abstention if no threshold qualifies.

Start with [experiment.py](experiment.py); the [module README](README.md) lists setup, commands and every supporting file.

Report corrupted-position recovery, clean false edits and whole-record accuracy together. A development clean-edit constraint is not a guarantee on unseen records. The majority rule is a strong task-specific baseline and must remain visible.

## What I actually observed

On the saved held-out fixture, majority repair recovered 69.8% of corrupted positions, the ordinary denoiser 14.4%, and the gated model 9.4%. All three measured zero false edits on clean positions in this small sample. The gated threshold selected on development data was 0.0, so this run did not demonstrate useful selective abstention. The simple rule remains substantially stronger; longer or more complicated models are not justified by this result alone. See the [saved result](smoke-results.json) for the exact values and run scope.

## References

1. Jacob Devlin, Ming-Wei Chang, Kenton Lee and Kristina Toutanova. *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. 2018, revised 2019. [arXiv:1810.04805, version 2](https://arxiv.org/html/1810.04805v2), especially section 3.1.

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
