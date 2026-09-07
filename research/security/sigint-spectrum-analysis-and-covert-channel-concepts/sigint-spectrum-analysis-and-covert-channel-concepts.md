+++
title = "Signal detection under nuisance and session shift"
date = "2026"
description = "A saved synthetic signal pilot shows why detection, false alarms and session shift must be evaluated together."
draft = false
id = "research/sigint-spectrum-analysis-and-covert-channel-concepts"
type = "research-note"
author = "tegridydev"
topic = "model-interpretation-evaluation"
related = ["research/tegridydev-security-research-catalogue"]
status = "pilot"
updated = "2026-09-08"
+++

# [td] tegridydev | Signal detection under nuisance and session shift

*design study and proposed evaluation*

Signal classifiers are very good at finding *something*. The uncomfortable part is working out whether that something is the labelled phenomenon or an accidental shortcut in SNR, plotting, session identity or generator settings.

This study keeps the object deliberately synthetic. I generate complex-valued sequences with known nuisance parameters and ask whether a detector survives session and parameter shift. It is an anomaly-detection benchmark, not a covert-radio implementation and not evidence about a named protocol.



<!-- cpu-comparison:start -->
## Results

Across the five seeds, the sequence model flagged every shifted negative example at its frozen threshold: a 100% shifted false-alarm rate. The statistical baseline averaged 3.92%. Strong ordinary-set AUROC did not establish threshold robustness under this synthetic shift.

Seeded synthetic session-held-out detector comparison with frozen development threshold and offset shift. Raw probabilities retained; no real RF performance claim. Deliberately label-correlated-SNR audit remains separate.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| sequence · final · auroc | 0.995034 | 0.0062537 |
| sequence · final · false alarm | 0.0336 | 0.039355 |
| sequence · shifted · auroc | 0.658488 | 0.20105 |
| sequence · shifted · false alarm | 1 | 0 |
| statistics · final · auroc | 0.999773 | 0.00028157 |
| statistics · final · false alarm | 0.036 | 0.0056569 |
| statistics · shifted · auroc | 0.999885 | 0.00016135 |
| statistics · shifted · false alarm | 0.0392 | 0.015595 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.
<!-- cpu-comparison:end -->

## Earlier pilot results

Under the synthetic shift, the sequence model labelled everything positive at its fixed threshold. Its detection rate therefore looks perfect while its false-alarm rate is also 100%. Both numbers are needed to see the failure.

| Condition | Evaluation | AUROC | Detection | False alarms |
| --- | --- | --- | --- | --- |
| statistics | final | 1.000000 | 100.00% | 4.80% |
| statistics | shifted | 1.000000 | 100.00% | 4.40% |
| sequence | final | 0.760752 | 56.40% | 22.00% |
| sequence | shifted | 0.502896 | 100.00% | 100.00% |

Seed 17; 100 training steps; 3,000 sequences with 20/5/5 train/development/test sessions and five shifted sessions. Session resampling is not evidence from real RF recordings.

Records: [pilot-results.json](pilot-results.json). These values are transcribed from the saved records, not newly rerun experiments.

## Build the dataset so shortcuts are visible

Each record keeps generator revision, seed, base waveform family, nuisance parameters, perturbation label, sample-rate convention, duration and split group. Store the complex samples—or a losslessly specified recipe—not just spectrogram images. Plots are derived views and their scaling can leak labels.

Noise, frequency offset, timing offset and session/channel parameters should be sampled independently of the anomaly label. Windows derived from one underlying sequence stay in one split. Otherwise a classifier can memorise a recording/session fingerprint while looking impressively accurate on random windows.

The core counterfactual is a **nuisance twin**: same underlying signal and anomaly label, one benign nuisance changed. The model’s confidence should be much more stable on those pairs than when the actual labelled perturbation changes.

## The first fixture

Use a 256-sample unit-energy complex sinusoid with random phase. The altered class receives a small amplitude-envelope perturbation, then both classes receive the same nuisance distributions and independent complex Gaussian noise. Thirty simulated sessions provide balanced pairs; a separate shift set uses a frequency-offset range outside training.

That fixture is intentionally simple enough that a statistical baseline has a real chance of winning. The point is not to make a neural network look necessary.

Compare energy/variance-style summaries, simple spectral/statistical features and a small temporal model. Report AUROC, precision-recall behaviour under the declared class balance, Brier score/calibration, detection at a fixed development false-alarm target and results by session/nuisance bin. False alarm also needs a unit—window, sequence or session—rather than one ambiguous percentage.

The main hypotheses are:

- a learned detector can beat simple features under held-out nuisance conditions;
- combining observation views helps beyond either view alone without shared-seed leakage;
- calibration degrades under distribution shift, and that degradation should be reported rather than tuned away on the final set.

An intentionally defective fixture with label-correlated SNR is important. If the audit does not catch that shortcut, I should not trust it on subtler leakage.

**What would weaken the idea:** if the statistical baseline matches or beats the neural model, keep it. If performance collapses only after switching from random windows to session-held-out data, the original “accuracy” was mostly split leakage. If a development threshold produces a huge shifted false-alarm rate, that is the result rather than an invitation to retune on the shift set.

## What this can and cannot tell me

O’Shea, Corgan and Clancy are clear prior work for learned modulation recognition. I am not claiming that learned RF classification is new. The narrower contribution is a nuisance-controlled evaluation that tries to make shortcut dependence painfully obvious.

A later **detectability envelope** could plot performance against observer assumptions such as duration and available feature types, producing a conditional surface instead of one headline score. That would still describe this synthetic observation model, not absolute detectability in real radio traffic.

The result I want is actually quite modest: **when the detector fires, can I show that it is reacting to the thing I labelled rather than the way I happened to generate the dataset?**

## Implementation

The waveform generator now produces 3,000 balanced sequences in thirty sessions, matched nuisance pairs, unit clean energy and a separate shifted frequency range. A statistical classifier and a small sequence CNN train on twenty sessions; thresholds are selected on five development sessions and frozen for final/shift evaluation.

Start with [signal_experiment.py](signal_experiment.py); the [module README](README.md) lists setup, commands and every supporting file.

The report includes AUROC, Brier score, sequence false-alarm/detection rates, per-session outcomes and a session bootstrap interval. The development false-alarm target is not a promise that final false alarms stay below it.

## Earlier observations

The statistical baseline achieved final AUROC 1.000, detection 100.0% and false alarms 4.8%. The CNN achieved AUROC 0.761, detection 56.4% and false alarms 22.0%. On the shifted set its false-alarm rate reached 100.0%. A threshold satisfying the development constraint did not transfer. This is a concrete reason to keep session-level reporting and the statistical baseline; it is not evidence about real radio traffic. See the [saved result](pilot-results.json) for the exact values and run scope.

## References

- **Convolutional Radio Modulation Recognition Networks** — Timothy J. O’Shea, Johnathan Corgan, T. Charles Clancy. 2016-06-10 (arXiv v3; first submitted 2016-02-12). [Source](https://arxiv.org/abs/1602.04105).

## Status

The results apply to the stated datasets and controls. Further experiments described here are proposals unless accompanied by a recorded result.

[Research index](../../README.md)
