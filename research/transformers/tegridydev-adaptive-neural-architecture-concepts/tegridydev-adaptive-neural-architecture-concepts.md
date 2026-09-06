# [td] tegridydev | Adaptive neural architectures: mechanisms and research priorities

*research overview and implementation priorities*

I’ve got a lot of old adaptive-architecture ideas, and the easiest way to make them useless would be to combine them all into one giant “self-evolving transformer” before any individual mechanism earns its keep.

This overview organises them by **what actually changes**—memory, routing, representation, repair or precision—and gives each one a smallest useful comparison.

## Memory and lifecycle

**AI-01 — Attention Ponds / Dynamic Metamorphic Matrix.** Keep active context plus a few bounded secondary pools with explicit relevance, age and access history. Compare staged retention with FIFO, LRU and one delay queue at the same stored bytes and retrieval budget. The question is whether giving low-ranked information several chances to become relevant again improves later recall.

**AI-02 — Metamorphic Neural Ecosystem.** Replace the biological language with a fixed expert pool moving through exploration, consolidation and mature states. Compare bounded perturbation/copying with fixed experts and random reassignment at equal parameters and training tokens. Animated UI values are not evidence of emergence.

**AI-03 — selective corruption and repair.** This is now the [self-healing token](../self-healing-tokens/self-healing-tokens.md) study: detect damage, decide whether repair is justified, and measure clean-input harm separately from recovery.

## Routing and feature use

**AI-04 — conditional routing.** A gate predicts whether the expensive route is worth running **before** both routes execute. Compare learned routing with random routing and always-deep execution under a fixed compute budget. Post-hoc weighting cannot claim saved compute.

**AI-05 — hybrid feature processing.** Cross-layer attention, temporal convolution, long-context attention, repair and pooling can be combined on a task containing both local motifs and long dependencies, but each component needs an ablation at matched capacity. The combination does not inherit evidence from the parts.

**AI-07 — temporal weighting.** This is now developed in [temporal attention](../temporal-attention-that-changes-predictions/temporal-attention-that-changes-predictions.md). A dashboard that reweights attention after prediction is not the same mechanism as elapsed time affecting the prediction itself.

## Representation experiments

**AI-06 — spatial population encodings.** Encode coordinates with sinusoidal/Fourier features, declare the domain and inspect aliasing. Compare raw coordinates with fixed Fourier features on held-out spatial regions before attaching robotics or geospatial application claims.

**AI-08 — geometric feature dynamics.** Keep unit-sphere projection, geometry-aware updates and Fisher/natural-gradient approximations separate. Any manifold version needs a declared metric and transport rule and should be compared with ordinary normalisation/learning-rate controls.

**AI-09 — complex phase representations.** Use explicit real/imaginary components on periodic tasks and compare with an equal-parameter real model. Complex arithmetic is a classical representation choice; it does not create a quantum-computing claim.

## Precision and tooling

**AI-10 — adaptive precision/pruning.** The [weight/SVD](../weight-similarity-and-svd-compression/weight-similarity-and-svd-compression.md) and [BitNet](../bitnet-quantization-and-conversion/bitnet-quantization-and-conversion.md) studies now carry the concrete storage questions. Pruning, low-rank factorisation and quantisation should each work alone before a controller tries to mix them.

**AI-11 — optimisation CLI.** A useful interface needs a capability table connecting each displayed method to an actual backend, supported model family, calibration/training input and export format. A button labelled QAT is not evidence that a valid QAT/export path exists.

## Combinations worth testing only after the parts work

Two combinations still interest me. The first crosses staged memory with temporal validity in a 2×2 experiment: neither, each alone and both, all at equal memory. The second spends a limited repair budget using corruption scores and compares detector allocation with random and oracle allocation.

The evidence ladder across the whole portfolio is simple:

1. **defined transformation** — I can state exactly what changes;
2. **verified implementation** — tests prove that change really occurs;
3. **controlled result** — the mechanism beats or clarifies a baseline on a held-out task.

Moving an item between ponds establishes a state transition, not better memory. A sparse gate establishes a numerical pattern, not fewer executed operations. The existing pilots are useful mostly because they make that distinction harder to hand-wave away.

For now I would keep building these as small falsifiable mechanisms rather than trying to crown a combined adaptive architecture before the individual pieces deserve it.

## References

- [Switch Transformers](https://jmlr.org/papers/v23/21-0998.html) — sparse expert routing context.
- [Memorizing Transformers](https://arxiv.org/abs/2203.08913v1) — external-memory context.

## Current implementation map

The individual mechanisms now have local code: [temporal attention](../temporal-attention-that-changes-predictions/README.md), [selective repair](../self-healing-tokens/README.md), [FBAC](../face-based-attention-circuits/README.md), [head mutation](../hydraform/README.md) and [causal memory](../reflective-transformer-memory-and-adaptation/README.md). The first saved pilots do not support combining them into a new architecture: FBAC roughly matches its dense control, majority repair beats the learned repair models, and temporal gains depend on the generator. Keep geometric, phase and hybrid leads at the mechanism-definition stage until they have comparably explicit tests.

[Research index](../../README.md)

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
