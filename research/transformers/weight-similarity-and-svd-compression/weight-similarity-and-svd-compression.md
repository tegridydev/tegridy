+++
title = "Weight similarity and functional low-rank compression"
date = "2026"
description = "Compare complete stored factor bytes with calibration and held-out functional error, rather than inferring usefulness from weight similarity."
draft = false
id = "research/weight-similarity-and-svd-compression"
type = "research-note"
author = "tegridydev"
topic = "architecture-experiments"
related = ["research/bitnet-quantization-and-conversion"]
status = "implemented"
updated = "2026-09-08"
+++

# [td] tegridydev | Weight similarity and functional low-rank compression

*design study and proposed evaluation*

A weight-similarity heatmap can look wonderfully compressible while saving exactly zero bytes. I’m testing a more annoying question: **does similarity help choose weight-sharing or low-rank transformations that preserve function better than simple baselines once the entire saved representation is counted?**

Parameter resemblance, functional resemblance and actual compression stay separate throughout the pipeline.


<!-- cpu-comparison:start -->
## Results

Rank-128 factors occupied 1.97 MB versus 9.44 MB for the original stored matrix, a reduction of about 79%. Layer-output mean squared error was 0.298; smaller ranks saved more space but increased that error. These measurements cover one projection and four short texts, not end-to-end model quality or inference speed.

First GPT-Neo MLP projection, four declared short texts split into calibration/evaluation; measured factor bytes and layer-output error. No end-to-end language-model loss or speed claim.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| rank128 · dense file bytes | 9.43731e+06 | — |
| rank128 · factor file bytes | 1.96658e+06 | — |
| rank128 · held out mse | 0.297697 | — |
| rank32 · dense file bytes | 9.43731e+06 | — |
| rank32 · factor file bytes | 492024 | — |
| rank32 · held out mse | 0.470541 | — |
| rank64 · dense file bytes | 9.43731e+06 | — |
| rank64 · factor file bytes | 983544 | — |
| rank64 · held out mse | 0.388916 | — |
| rank8 · dense file bytes | 9.43731e+06 | — |
| rank8 · factor file bytes | 123384 | — |
| rank8 · held out mse | 0.572879 | — |

The [comparison record](comparison-results.json) includes the 1 recorded run, measured values, source hashes and dependency versions. This is a single fixed evaluation; no across-seed uncertainty is estimated.
<!-- cpu-comparison:end -->

## show stored cost beside the answer error

For an `m × n` matrix and rank `r`, the two factors contain `r(m+n)` values. With equal scalar width, a 64×64 matrix at rank 8 uses 1,024 factor values instead of 4,096; rank 32 merely breaks even on values before metadata.

That count is not the complete file size. The [report implementation](compress.py) serialises the factors and reports the actual payload, including its container overhead. Keep it beside the functional error on both calibration and held-out inputs.

The [functional fixture](test_compress.py) uses `diag(10, 1)` at rank 1. Calibration input `[1, 0]` has zero MSE, while held-out `[0, 100]` has MSE 5,000. A small discarded weight can matter a lot on a different input distribution. This example does not measure end-to-end model speed.

## Similarity only makes sense when the matrices are comparable

For role- and shape-matched matrices, flattened cosine is a descriptive parameter statistic. Truncating two differently shaped tensors until their prefixes happen to match is not meaningful alignment, and even equal-shaped layers can represent information in different internal bases.

Keep tensor names, roles and shapes attached to every row/column in the similarity matrix. Then add **functional similarity** on calibration inputs by comparing `Ax` and `Bx`. Weight cosine and output similarity can disagree; that disagreement is useful because it tells me whether the selection metric tracks behaviour at all.

## Three transformations, three different claims

**Interpolation** replaces two weights with a blend. That tests tolerance to parameter change but does not compress anything by itself.

**Weight tying** makes modules reference the same stored parameter. The serializer/loader must preserve that sharing rather than writing two identical dense arrays.

**Low-rank factorisation** stores factors such as `U_r`, singular values and `V_r` and computes through those factors. For an `m×n` matrix, the rough value count is `r(m+n)` rather than `mn`, before metadata. Two smaller matrix multiplications can still be slower than one tuned dense multiply, so actual latency stays a separate measurement.

Reject incompatible shapes instead of silently resizing them.

## A cheap controlled pilot

Start with one small model and one shape/role-matched candidate pair, not every matrix in BERT-large. Freeze checkpoint/tokeniser and split calibration, validation and final text by source document.

Compare candidate selection by:

1. random matched pair;
2. highest raw weight similarity;
3. highest calibration-output similarity.

Apply interpolation, tying and low-rank approximation as separate experiments. Evaluate the untouched model and transformed model using the correct language/task head. If extra fine-tuning is allowed after compression, give an untouched control the same additional training tokens so recovery training does not become part of the compression claim for free.

The main hypotheses are that functional similarity chooses less damaging transformations than raw cosine, a complete factorised checkpoint becomes smaller at a declared quality tolerance, and selected sharing beats random matched sharing at the same storage budget.

**What kills the claim:** the full artifact is not smaller after embeddings, heads, factors, scales, indexes and loader metadata are counted; reload changes the function unexpectedly; or quality comparisons use different prompts/heads. Average loss should also be broken down enough to catch rare-feature regressions hidden by the mean.

## Count the bytes you actually need to reload

Report complete checkpoint bytes, factor/raw array bytes, parameter count, peak load memory, steady resident memory and execution dtype separately. A hash identifies stored content; it cannot reconstruct discarded arbitrary weights.

For a 64×64 matrix, rank 16 stores 2,048 factor values versus 4,096 dense values before metadata. Rank 32 already reaches the dense value count. That arithmetic is a useful sanity check, not a speed benchmark.

Functional error also depends on the inputs a layer sees. A direction with small weight error can matter a lot if calibration data uses it frequently, which motivates activation-aware rank selection as a later extension. Another extension uses a shared basis across layers plus layer-specific coefficients/residuals, but the shared basis only counts as “shared” if I count it once **and** count every per-layer residual needed to recover the model.

SVD-LLM and ASVD are direct prior context for low-rank and activation-aware compression. The contribution I’m testing here is less ambitious: **does the criterion used to call two weights “similar” actually predict a better compression decision under complete accounting?**

## Implementation

The factorizer now creates actual NumPy low-rank factors, reloads serialized arrays and measures calibration/held-out output error. Reports separate parameter count, raw array bytes and complete file bytes. Tests verify an exact low-rank matrix and a calibration/held-out counterexample.

Start with [compress.py](compress.py); the [module README](README.md) lists setup, commands and every supporting file.

`weight` has shape `[output,input]`; both input arrays have shape `[samples,input]`. Rank 32 on a 64×64 matrix only breaks even in factor parameter count, and serialization headers still cost bytes. Existing output files are refused.

## References

- **Xin Wang; Yu Zheng; Zhongwei Wan; Mi Zhang. [SVD-LLM: Truncation-aware Singular Value Decomposition for Large Language Model Compression](https://arxiv.org/abs/2403.07378v5).** 2025-03-16, arXiv v5; ICLR 2025; first submitted 2024-03-12.
- **Zhihang Yuan; Yuzhang Shang; Yue Song; Dawei Yang; Qiang Wu; Yan Yan; Guangyu Sun. [ASVD: Activation-aware Singular Value Decomposition for Compressing Large Language Models](https://arxiv.org/abs/2312.05821v5).** 2025-08-28, arXiv v5; first submitted 2023-12-10.

## Status

The results apply to the stated datasets and controls. Further experiments described here are proposals unless accompanied by a recorded result.

[Research index](../../README.md)
