# [td] tegridydev | Sparse feature recovery: reconstruction is only one target

*design study and proposed evaluation*

Sparse autoencoders can reconstruct a vector very well without recovering the independent features that generated it. That distinction is the entire point of this study.

I want three measurements kept separate: **reconstruction**, **dictionary recovery** and **support recovery**. If the first improves while the other two stay bad, the autoencoder has learned a useful code for reconstruction, not necessarily the original latent features.

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

## What exists locally

The sparse autoencoder now trains on normalized synthetic dictionaries with the stated activation probability and coefficient range. The evaluator uses one-to-one signed matching, detects duplicated true features and records dead learned columns. Decoder columns are renormalized after optimizer steps.

Start with [recovery.py](recovery.py); the [module README](README.md) lists setup, commands and every supporting file.

The permutation fixture must match perfectly and the duplicated dictionary must be labelled non-identifiable before interpreting a learned score. `pilot-results.json` retains every matched cosine rather than only a favorable average.

## What I actually observed

The 100-step pilot reached held-out reconstruction MSE 0.0561, while mean one-to-one signed dictionary cosine was only 0.425. The evaluator passes the exact-permutation fixture, but the trained dictionary has not recovered the original features cleanly. Report these two measurements separately; increasing reconstruction quality cannot stand in for support recovery. See the [saved result](pilot-results.json) for the exact values and run scope.

## References

- **Nelson Elhage; Tristan Hume; Catherine Olsson; Nicholas Schiefer; Tom Henighan; Shauna Kravec; Zac Hatfield-Dodds; Robert Lasenby; Dawn Drain; Carol Chen; Roger Grosse; Sam McCandlish; Jared Kaplan; Dario Amodei; Martin Wattenberg; Christopher Olah. [Toy Models of Superposition](https://arxiv.org/abs/2209.10652v1).** 2022-09-21, arXiv v1.

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
