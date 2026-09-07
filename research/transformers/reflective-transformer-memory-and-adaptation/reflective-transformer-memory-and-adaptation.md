+++
title = "Reflective transformer: causal memory and bounded adaptation"
date = "2026"
description = "A causal memory fixture checks delayed retrieval, batch isolation and episode reset while keeping adaptation benefits unproven."
draft = false
id = "research/reflective-transformer-memory-and-adaptation"
type = "research-note"
author = "tegridydev"
topic = "architecture-experiments"
related = ["research/local-assistants-and-memory", "research/temporal-attention-that-changes-predictions"]
status = "implemented"
updated = "2026-09-08"
+++

# [td] tegridydev | Reflective transformer: causal memory and bounded adaptation

*design study and proposed evaluation*

“Reflective transformer” is the working name for a model that can retrieve earlier internal information and, later, adapt how strongly different heads use that memory. The important part is not the name; it is keeping **memory retrieval, head specialisation and feedback-driven adaptation** as separate mechanisms until each one works.

The first study is therefore memory plus fixed head behaviour. Performance-driven adaptation comes later with an explicit delayed feedback source.


<!-- cpu-comparison:start -->
## Recorded findings

Attention over all eight written items averaged 97.19% accuracy; four-slot FIFO averaged 35.98% and no memory 7.42%. FIFO was much worse on evicted than retained targets. The capacity difference is intentional, so this is an eligibility/eviction study, not a capacity-matched architecture comparison.

Synthetic eight-write episodic lookup with a learned query projection, no-memory, full-eight-item attention and four-slot FIFO. Capacity difference is explicit; this is not a full reflective Transformer or LRU comparison.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| attention · accuracy | 0.971875 | 0.012628 |
| attention · evicted · accuracy | 0.967491 | 0.013079 |
| attention · retained · accuracy | 0.977293 | 0.012505 |
| fifo · accuracy | 0.359766 | 0.032694 |
| fifo · evicted · accuracy | 0.0402827 | 0.0053589 |
| fifo · retained · accuracy | 0.754585 | 0.077528 |
| none · accuracy | 0.0742188 | 0 |
| none · evicted · accuracy | 0.0742049 | 0 |
| none · retained · accuracy | 0.0742358 | 0 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.
<!-- cpu-comparison:end -->

## a write becomes eligible later

The [memory fixture](test_memory.py) reads an empty store at step 0, writes at step 0, and still reads zero at that same step. The write becomes eligible at step 1. Two batch items retain different values, and resetting item 0 leaves item 1 intact.

Those checks matter more than calling the storage reflective: same-step access would leak information, and a shared reset could erase another episode. The stored values are detached while the retrieval gate receives gradients. This establishes bounded causal storage behaviour, not a benefit from online adaptation.

## Start with a causal memory bank

Use ordinary attention tensors `Q,K,V:[B,H,T,d]` and give each head a bounded bank of keys/values `[B,H,N,d]`. A query produces memory scores `[B,H,T,N]`, invalid entries are masked, and each head retrieves a weighted value sum. Empty banks return zero rather than NaNs.

The bank is part of the experimental state. Entries need episode identity, creation step, last use and any utility metadata. Writes happen at a declared boundary **after** a completed segment, and a prediction can only read entries that were causally available before it. Independent episodes reset memory unless cross-episode learning is explicitly the task.

This sounds basic, but it prevents two ugly shortcuts: batch elements reading each other’s memory and targets being written before the model is asked to predict them.

Start with FIFO/LRU-style policies before anything learned. Access frequency alone can over-reward common memories and discard rare-but-important ones. If a utility policy is later added, define utility through controlled removal effects or external task outcomes rather than a similarity score calling itself usefulness.

## A delayed-reuse task

Generate episodes that introduce random symbol/value associations, add distractors and later ask for values after the original evidence has fallen outside the ordinary context window. Some episodes change an association partway through so stale-memory behaviour is measurable.

Compare a 2×2 factorial first:

1. ordinary attention;
2. memory only;
3. fixed head specialisation only;
4. memory + specialisation.

Train under equal token budgets and count the memory bank in total storage. Also compare with simply extending the normal context at a similar storage budget; external memory should have to beat “remember more input” before earning architectural complexity.

Measure query accuracy by delay, stale-answer rate, rare-association accuracy, bank turnover, useful-hit rate and resource use. A “useful hit” should mean that removing the retrieved item causes a measurable task effect, not that its cosine similarity happened to be high.

Use empty-memory and shuffled-memory controls. If they perform equally well, the model may be ignoring the bank.

## Adaptation needs a real feedback channel

The model does not magically know whether its last answer was correct. In the first adaptation experiment, supervised labels can provide delayed external feedback **after** prediction. A deployment-oriented version would need delayed verified feedback or a clearly labelled proxy.

Self-confidence is not correctness. Any adaptation rule needs to state who provides the signal, when it arrives and how wrong feedback is handled.

I would compare a bounded moving-average update, fixed schedule and no adaptation, with rollback when development performance degrades. Adaptation should also face a fixed learned-gate control: if the dynamic update buys nothing, keep the simpler gate.

**What would weaken the idea:** memory that does not beat a context/storage-matched baseline, utility policies that only help common associations, or adaptation that damages pre-change behaviour without a compensating post-change benefit.

## Two extensions worth keeping

One is a contradiction-aware memory that retains old and new associations with validity intervals rather than immediately overwriting history. That connects temporal validity with memory in a way I can actually query.

The other tests whether apparently specialised heads depend on different memory subsets by removing their most-used entries and comparing with random removals. Shared versus per-head banks need equal **total** capacity so head separation does not secretly multiply memory.

Memorizing Transformers is obvious prior context for retrieving earlier representations. My immediate contribution is much smaller: **a memory state that is causal, episode-isolated, reloadable and cheap enough that its usefulness can be tested against just extending context.**

## Implementation

The memory module now stores episode-isolated `[batch,head,slot,width]` keys/values, performs detached FIFO writes only at increasing completed steps and masks same-step/future entries. Empty banks return zero; per-head gates start at 0.5. Tests check reset, reload and 32/128 total capacities.

Start with [memory.py](memory.py); the [module README](README.md) lists setup, commands and every supporting file.

Use `Memory.write` after processing a segment and query with a later prediction step. A reset is explicit between episodes. The caller remains responsible for not supplying future labels as earlier observations.

## References

- **Yuhuai Wu; Markus N. Rabe; DeLesley Hutchins; Christian Szegedy. [Memorizing Transformers](https://arxiv.org/abs/2203.08913v1).** 2022-03-16, arXiv v1; ICLR 2022.

## Status

The results apply to the stated datasets and controls. Further experiments described here are proposals unless accompanied by a recorded result.

[Research index](../../README.md)
