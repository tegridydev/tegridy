+++
title = "BitNet conversion: separate numerical quality from packed execution"
date = "2026"
description = "Separate function-preserving float conversion, ternary-weight simulation, two-bit storage and actual inference execution."
draft = false
id = "research/bitnet-quantization-and-conversion"
type = "research-note"
author = "tegridydev"
topic = "architecture-experiments"
related = ["research/weight-similarity-and-svd-compression"]
status = "implemented"
updated = "2026-09-08"
+++

# [td] tegridydev | BitNet conversion: separate numerical quality from packed execution

*design study and proposed evaluation*

“Ternary model” can mean at least three different things: the forward pass uses ternary-valued weights, the stored checkpoint is compact, or the runtime is actually faster. Those claims are related, but none of them automatically proves the others.

This study keeps the boundaries explicit so I can tell **where** quality or efficiency changed: function-preserving conversion, ternary numerical simulation, recovery training and packed execution are separate stages.


<!-- cpu-comparison:start -->
## Results

The packed representation uses fewer stored bytes, and its scalar output agrees numerically with the ternary simulation. The Python scalar packed path is slower than dense NumPy execution in this workload. Quantisation error against the original float matrix remains separate from packing error; storage reduction is not a speed or model-quality result.

Synthetic single-matrix conversion and actual scalar two-bit CPU execution. Complete packed file bytes are measured; float array bytes exclude a container. No trained-model quality or optimised-kernel speed claim.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| 512 · dense array bytes | 1.04858e+06 | 0 |
| 512 · dense seconds | 0.000369879 | 0.00014138 |
| 512 · packed file bytes | 65598 | 0 |
| 512 · packed seconds | 0.919392 | 0.013686 |
| 512 · packed simulation mse | 1.00349e-11 | 1.026e-13 |
| 512 · quantization mse | 136.985 | 2.0635 |
| 512 · simulation seconds | 0.000261063 | 3.9889e-05 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.
<!-- cpu-comparison:end -->

## four checks, four different claims

| Path in this module | What is checked | What is not established |
| --- | --- | --- |
| `convert(model, quantized=False)` | Deep clone preserves outputs and tied weights in a small fixture | Full checkpoint compatibility |
| `convert(model, quantized=True)` | Ternary-weight simulation has finite gradients and updates | Packed execution or unchanged numerical behaviour |
| `pack` / `unpack` | Two-bit symbols round-trip with padding validation | Total model storage including scales, shape and metadata |
| Inference execution | Floating tensor operations remain in use | A latency or throughput improvement |

A hand-checkable storage example, from the module folder:

```python
from ternary_reference import pack, unpack
values = [-1, 0, 1, 0, -1]
payload = pack(values)
assert len(payload) == 2
assert unpack(payload, len(values)) == values
```

Five symbols occupy two payload bytes here. That is a property of this reference format, **not** a measured compression ratio for a complete model. The caller still needs count, shape and scale information.

The [float/simulation tests](test_quantization.py) and [packing reference](ternary_reference.py) deliberately test different boundaries. Run them after [setup](README.md); a speed claim would require an actual packed kernel, comparable hardware and measured end-to-end execution.

## Start with numerical equivalence

The simulated weight path scales by mean absolute weight, rounds to ternary values and restores scale. Activations can be quantised separately into a signed low-precision range. Zero scales need an explicit zero-output rule; otherwise an all-zero block turns into undefined arithmetic.

A `BitLinear`-style training simulation can blend full-precision and quantised paths with a schedule. That schedule changes optimisation as well as numerical precision, so it needs comparison against immediate quantisation and a full-weight baseline at equal training tokens.

Most importantly, floating trainable weights are still stored. A successful ternary simulation is evidence that a model can train or run under that numerical constraint. It is **not** evidence that the checkpoint occupies 1.58 bits per weight or that a CPU/GPU kernel executes fewer bytes or instructions.

## A staged experiment

I’d use one small architecture with a verified parameter mapping and a corpus split by source document. Start with a 32-prompt equivalence fixture before training anything.

Compare five states:

1. original model;
2. function-preserving floating conversion;
3. simulated ternary weights;
4. trained/recovered simulated ternary weights;
5. packed export/runtime, only if one actually exists.

Each transition gets its own output-difference report. If quality collapses during the supposedly function-preserving step, that is a mapping/tie/tokeniser problem and I should not blame quantisation. If the packed path does not exist, the experiment stops before any inference-efficiency claim.

For training comparisons, keep model revision, tokeniser, data hashes, seeds and token budgets fixed. Report held-out language-model quality plus exact checkpoint identity and transfer coverage.

**What would weaken the idea:** if ternary recovery cannot reach an acceptable quality budget, that is a numerical result. If a packed representation saves file bytes but runtime memory/latency do not improve, that is a storage result only. I want those outcomes reported separately rather than compressed into “BitNet worked/didn’t work”.

## Storage needs honest accounting

`log2(3) ≈ 1.585` bits is the information bound for an ideal ternary symbol code. A simple independently addressable representation may use two bits, and real artifacts also store scales, shapes, padding and metadata.

A pack/unpack fixture should test every ternary symbol, block boundary, padding case and shape before touching a full model. Packed-runtime output then needs to match a dequantised reference within a declared tolerance.

A second extension is mixed precision: locate layers or token categories where ternary simulation causes the largest functional change, keep a small subset at higher precision and compare with uniform precision under the same **total stored bytes**. That is only useful if the accounting includes all per-layer scales and exceptions.

BitNet b1.58 is direct prior work for ternary-weight language modelling. The thing I’m trying to make cleaner here is the experimental language around conversion: **numerical ternarisation, packed storage and faster execution are three checkpoints, not one headline.**

## Implementation

A deep float clone now preserves function and tied parameters. The separate ternary-weight simulator uses a zero-scale guard and a straight-through gradient path; conversion preserves cloned weight ties and tests confirm gradient updates. The two-bit symbol reference remains a separate storage example.

Start with [quantization.py](quantization.py); the [module README](README.md) lists setup, commands and every supporting file.

`convert(model, quantized=False)` is the function-preserving baseline. `quantized=True` replaces linear projections with the explicitly different weight simulation. Packed-symbol storage and floating matrix execution are not interchangeable performance claims.

## References

- **Shuming Ma; Hongyu Wang; Lingxiao Ma; Lei Wang; Wenhui Wang; Shaohan Huang; Li Dong; Ruiping Wang; Jilong Xue; Furu Wei. [The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits](https://arxiv.org/abs/2402.17764v1).** 2024-02-27, arXiv v1; work-in-progress preprint.
- **Zhihang Yuan; Yuzhang Shang; Yue Song; Dawei Yang; Qiang Wu; Yan Yan; Guangyu Sun. [ASVD: Activation-aware Singular Value Decomposition for Compressing Large Language Models](https://arxiv.org/abs/2312.05821v5).** 2025-08-28, arXiv v5; first submitted 2023-12-10.

## Status

The results apply to the stated datasets and controls. Further experiments described here are proposals unless accompanied by a recorded result.

[Research index](../../README.md)
