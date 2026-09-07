+++
title = "Sparse feature recovery: reconstruction is only one target"
date = "2026"
description = "A synthetic sparse-autoencoder pilot separates held-out reconstruction error from recovery of the generating features."
draft = false
id = "research/sparse-feature-recovery"
type = "research-note"
author = "tegridydev"
topic = "model-interpretation-evaluation"
related = ["research/neuron-mapping-and-token-trajectories", "blog/what-a-model-map-can-show"]
status = "pilot"
updated = "2026-09-08"
+++

# [td] tegridydev | Sparse feature recovery: reconstruction is only one target

*design study and proposed evaluation*

Sparse autoencoders can reconstruct a vector very well without recovering the independent features that generated it. That distinction is the entire point of this study.

I want three measurements kept separate: **reconstruction**, **dictionary recovery** and **support recovery**. If the first improves while the other two stay bad, the autoencoder has learned a useful code for reconstruction, not necessarily the original latent features.


<!-- cpu-comparison:start -->
## Results

Low reconstruction error did not imply clean feature recovery. Across the feature-count, correlation and noise conditions, mean signed dictionary alignment stayed around 0.45–0.48 and support F1 around 0.13–0.33. The full receipt includes zero-reconstruction and all-positive-support controls; these synthetic dictionary results do not identify real-model concepts.

Synthetic nonnegative sparse codes; independent dictionary/initialisation replicates; threshold selected on development rows; no recovery claim for real-model features.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| features100 correlation0 · 0 noise0 · 0 · mean signed cosine | 0.451469 | 0.0065578 |
| features100 correlation0 · 0 noise0 · 0 · mse | 0.000579255 | 3.8369e-05 |
| features100 correlation0 · 0 noise0 · 0 · support f1 | 0.214083 | 0.0058181 |
| features100 correlation0 · 0 noise0 · 05 · mean signed cosine | 0.451106 | 0.0065758 |
| features100 correlation0 · 0 noise0 · 05 · mse | 0.000585862 | 4.431e-05 |
| features100 correlation0 · 0 noise0 · 05 · support f1 | 0.214218 | 0.0064553 |
| features100 correlation0 · 9 noise0 · 0 · mean signed cosine | 0.449627 | 0.0052811 |
| features100 correlation0 · 9 noise0 · 0 · mse | 0.000455789 | 3.1375e-05 |
| features100 correlation0 · 9 noise0 · 0 · support f1 | 0.208143 | 0.0020971 |
| features200 correlation0 · 0 noise0 · 0 · mean signed cosine | 0.463252 | 0.0045774 |
| features200 correlation0 · 0 noise0 · 0 · mse | 0.00146767 | 0.00016886 |
| features200 correlation0 · 0 noise0 · 0 · support f1 | 0.133829 | 0.0019691 |
| features200 correlation0 · 0 noise0 · 05 · mean signed cosine | 0.463127 | 0.0044714 |
| features200 correlation0 · 0 noise0 · 05 · mse | 0.00148771 | 0.00017997 |
| features200 correlation0 · 0 noise0 · 05 · support f1 | 0.13308 | 0.0018584 |
| features200 correlation0 · 9 noise0 · 0 · mean signed cosine | 0.452857 | 0.001176 |
| features200 correlation0 · 9 noise0 · 0 · mse | 0.00104145 | 0.00021126 |
| features200 correlation0 · 9 noise0 · 0 · support f1 | 0.135201 | 0.0012175 |
| features50 correlation0 · 0 noise0 · 0 · mean signed cosine | 0.476465 | 0.0075805 |
| features50 correlation0 · 0 noise0 · 0 · mse | 0.000511496 | 6.4923e-05 |
| features50 correlation0 · 0 noise0 · 0 · support f1 | 0.327349 | 0.017519 |
| features50 correlation0 · 0 noise0 · 05 · mean signed cosine | 0.473572 | 0.0080547 |
| features50 correlation0 · 0 noise0 · 05 · mse | 0.000541304 | 6.0297e-05 |
| features50 correlation0 · 0 noise0 · 05 · support f1 | 0.320935 | 0.014186 |
| features50 correlation0 · 9 noise0 · 0 · mean signed cosine | 0.478803 | 0.013165 |
| features50 correlation0 · 9 noise0 · 0 · mse | 0.000403885 | 3.6608e-05 |
| features50 correlation0 · 9 noise0 · 0 · support f1 | 0.311325 | 0.017698 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.
<!-- cpu-comparison:end -->

## Earlier pilot results

The saved model reconstructed held-out inputs with modest error but did not recover the true features closely. Reconstruction and identification need separate measurements.

| Measurement | Saved value |
| --- | --- |
| Held-out reconstruction MSE | 0.056118 |
| Mean matched signed cosine | 0.425241 |
| Dead learned features | 0 |
| Matched true features | 100 |

1024 synthetic rows, 768 train/256 held out; no correlated-feature study. Seed 17; 100 training steps. Correlated-feature and non-identifiable dictionaries still require separate studies.

Records: [pilot-results.json](pilot-results.json). These values are transcribed from the saved records, not newly rerun experiments.

## A synthetic problem where the ground truth exists

Generate sparse coefficients `x` over 100 source features, project them through 100 normalised directions in a 30-dimensional observation space and optionally add noise:

`y = Wᵀx + ε`.

The SAE produces `z = ReLU(Ey+b)` and `ŷ = Dz`, trained with reconstruction MSE plus an L1 sparsity penalty. Decoder columns are renormalised after updates so the model cannot shrink encoder activations and inflate decoder magnitude just to make the L1 term cheap.

For the first independent regime, activate each feature with probability 0.05 and sample positive coefficients from `[0.5, 1.5]`. Use separate train/development/final observations under the same dictionary, then repeat the whole experiment with independently generated dictionaries.

## Learned feature numbers do not mean anything by themselves

The biggest evaluation bug in the older toy experiment was comparing latent index 17 with learned unit 17 as though dictionary order were preserved. It is not.

Build the ground-truth-versus-learned cosine matrix and solve a one-to-one assignment. Keep signed and absolute alignment distinct where sign ambiguity matters. Report unmatched/duplicate/dead features instead of forcing every learned direction into a clean story.

Then evaluate whether aligned learned activations recover the **active support** of the original sparse vector. Support thresholds are selected on development data. Empty-support cases need a declared convention rather than accidental divide-by-zero behaviour.

Reconstruction MSE, explained variance, mean active count, dead-feature fraction, duplicate-pair fraction, dictionary cosine, support precision/recall/F1 and coefficient error all answer different parts of the question.

## Baselines that make the metric earn trust

Before a training sweep, use deterministic evaluator fixtures:

- an exactly permuted ground-truth dictionary should match perfectly;
- shuffled feature labels should fail;
- deliberately duplicated source features should be marked non-identifiable rather than “recovered badly”.

Compare the SAE with direct dictionary correlations, PCA reconstruction and a sparse solver given the true dictionary. The oracle-dictionary solver is only an upper-reference for inference. A separately learned sparse dictionary is the more relevant algorithmic baseline if compute can be made comparable.

The first hypotheses are that alignment-aware evaluation beats raw index overlap, reconstruction can stay strong while dictionary recovery degrades under correlation, and rare features fail earlier than common ones under a fixed data budget.

Vary one property at a time—correlation, sparsity, frequency skew, noise or bottleneck size—rather than immediately launching a giant factorial grid. Keep final support recovery out of hyperparameter selection unless supervised recovery is explicitly the objective.

**What would weaken the idea:** support recovery that does not beat a declared baseline in the identifiable independent regime, results that depend on one dictionary seed, or persistently good reconstruction paired with poor dictionary alignment. In correlated/underdetermined settings, some failures are non-identifiability rather than optimiser bugs, which is why the duplicated-feature fixture matters.

## Extensions

A dictionary-drift experiment could rotate a small subset of source directions between phases and compare warm-started adaptation with retraining from scratch at equal optimisation steps. That turns “adaptive representation” into a specific changing-ground-truth test.

A recovery-confidence audit could align several independently trained SAEs to one another **without** using ground truth, then ask whether cross-run agreement predicts actual recovery. The ambiguous fixture is essential because several models can confidently agree on the same wrong merged feature.

Toy Models of Superposition provides obvious prior context for synthetic superposition. The narrow lesson I want from this implementation is simpler: **a good reconstruction loss is not a licence to call every learned direction a recovered feature.**

## Implementation

The sparse autoencoder now trains on normalized synthetic dictionaries with the stated activation probability and coefficient range. The evaluator uses one-to-one signed matching, detects duplicated true features and records dead learned columns. Decoder columns are renormalized after optimizer steps.

Start with [recovery.py](recovery.py); the [module README](README.md) lists setup, commands and every supporting file.

The permutation fixture must match perfectly and the duplicated dictionary must be labelled non-identifiable before interpreting a learned score. `pilot-results.json` retains every matched cosine rather than only a favorable average.

## Earlier observations

The 100-step pilot reached held-out reconstruction MSE 0.0561, while mean one-to-one signed dictionary cosine was only 0.425. The evaluator passes the exact-permutation fixture, but the trained dictionary has not recovered the original features cleanly. Report these two measurements separately; increasing reconstruction quality cannot stand in for support recovery. See the [saved result](pilot-results.json) for the exact values and run scope.

## References

- **Nelson Elhage; Tristan Hume; Catherine Olsson; Nicholas Schiefer; Tom Henighan; Shauna Kravec; Zac Hatfield-Dodds; Robert Lasenby; Dawn Drain; Carol Chen; Roger Grosse; Sam McCandlish; Jared Kaplan; Dario Amodei; Martin Wattenberg; Christopher Olah. [Toy Models of Superposition](https://arxiv.org/abs/2209.10652v1).** 2022-09-21, arXiv v1.

## Status

The results apply to the stated datasets and controls. Further experiments described here are proposals unless accompanied by a recorded result.

[Research index](../../README.md)
