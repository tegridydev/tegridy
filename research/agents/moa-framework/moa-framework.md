+++
title = "Multi Agent Orchestration: Streaming, Failures and Replay"
date = "2026"
description = "Trace streamed output, cancellation and injected failures through a replayable orchestration fixture before evaluating real model answer quality."
draft = false
id = "research/moa-framework"
type = "research-note"
author = "tegridydev"
topic = "agent-systems"
related = ["blog/botsim-local-community", "research/mixture-of-perspectives"]
status = "implemented"
updated = "2026-09-09"
+++

# Multi Agent Orchestration: Streaming, Failures and Replay

Multi agent systems are very easy to make look clever while quietly losing track of which worker said what. Before asking whether a committee improves answer quality, I want the boring plumbing to be correct: every request, stream, failure, retry and aggregation step should be replayable and attributable.

The question here is therefore orchestration first, intelligence second.

## Recorded findings

The 100 requests produced 50 completions and 50 deliberately injected failure outcomes. The latter are expected fault handling cases, not an observed 50% production failure rate. The fixture also exercises persistent cache expiry; live providers and answer quality were not evaluated.

Deterministic provider fixtures, explicit fault deadlines and persistent cache expiry; no live SDK, token spend or answer quality claim. Seed repeats are identical protocol replays, not independent task families.

| Recorded metric | Value |
| --- | ---: |
| completed | 50 |
| failed | 50 |
| requests | 100 |

The [comparison record](comparison-results.json) includes the 1 recorded run, measured values, source hashes and dependency versions. This is a single fixed evaluation; no across seed uncertainty is estimated.

## keep the failed provider's words attached to it

The [stream fixture](test_orchestrator.py) runs ordinary, empty delta and timeout providers. Ordinary and empty delta finish with `first second`; timeout ends with text `first`, status `failed`, and appears in `excluded`.

The partial text remains inspectable under the failed provider. It does not become a successful aggregate or get attributed to the provider that finished. A cancelled stream also ignores a later completion event, while a missing sequence number is an error. These are fake providers: the fixture tests event handling, not remote model reliability.

## A request/event contract I can actually replay

A request needs a stable ID, prompt, system instructions, conversation, tools, provider/model revision, generation settings, budget and deadline. A router returns selected provider IDs plus a reason. “Run every configured provider” is a perfectly valid fixed policy; it just should not be described as adaptive routing.

Each provider adapter yields typed events such as `started`, `text_delta`, `usage`, `completed`, `failed` and `cancelled`, all carrying request ID, provider ID, attempt ID and sequence number. Empty text is still a text event, not an implicit end of stream marker. Partial output from a failed worker can be retained for debugging without silently becoming a completed vote.

Aggregation then has to say what it actually did. Concatenating labelled responses, selecting one existing answer and synthesising a new answer are three different operations. If the implementation concatenates strings, I’m happy to call it aggregation as long as the article does not pretend that means voting, verification or learned mixture routing.

Cache keys should digest the canonical request, including instructions, model/settings, retrieval inputs and aggregation policy. A cached empty answer is different from a cache miss. Rate limits need unique attempt identities and a stated unit, starts, tokens or concurrency, and the accounting should include retries and synthesis.

## The first experiment needs no real model

**Question:** can typed request/event records reduce corrupted or misattributed outputs under provider failure compared with untyped chunk interleaving?

Use three fake asynchronous providers: one normal, one that yields an empty chunk then continues, and one that times out after partial output. Add requests with identical prompt text but different system instructions, models or generation parameters. Inject same second starts, cancellation and a configuration update during an active request.

Run 100 deterministic synthetic requests under a fixed five second deadline. Measure reconstructed output, provider attribution, lost chunks, cache isolation, duplicate work, deadline enforcement, cancellation cleanup and resource growth over repeated runs. Preserve the exact event log and expected outcome for every injected fault.

**Falsifier:** if typed events still lose partial output, leave workers alive or allow semantically different requests to share cache entries, the contract is incomplete. I would not move on to answer quality claims until those invariants pass.

A replayable trace is probably more useful than adding another provider. Scheduling decisions should be stored separately from model text so the same failure can be reproduced against fake adapters. Later, an adaptive router can start with one provider and escalate only when a task specific validator fails, compared with always all routing under a matched maximum budget.

## Comparing actual multi agent quality later

When the plumbing works, the fair quality comparison is direct single model output versus repeated independent samples with a fixed selector, structured roles without interaction and the proposed coordination mechanism. Base models, task information and generation settings stay controlled. Count input/output tokens, retries, selection and synthesis rather than treating a larger committee as free compute.

Keep development and final evaluation separated by task family, freeze scoring before final runs and retain incomplete cases. A worker that emits text and then fails remains a failed attempt unless the aggregation policy explicitly allows partial inputs.

Mixture of Agents is direct related architecture for layered model response sharing. The contribution I’m testing here is deliberately less glamorous: **can I tell exactly what happened when the committee breaks?** That seems like a good prerequisite for believing it when the committee succeeds.

## Implementation

Three asynchronous fake providers now exercise normal text, empty deltas and timeout after partial output. The reducer enforces contiguous sequence numbers, detects conflicting duplicates and keeps the first terminal outcome. Aggregation excludes failed partial streams, and canonical cache keys include the complete supplied request.

See [orchestrator.py](orchestrator.py); the [module README](README.md) describes usage and dependencies.

The demo prints exact per attempt events, reconstructed streams, excluded workers and labelled completed output. Retry callers must assign a new attempt ID; the reducer does not merge attempts.

## References

- **Junlin Wang; Jue Wang; Ben Athiwaratkun; Ce Zhang; James Zou**. [Mixture-of-Agents Enhances Large Language Model Capabilities](https://arxiv.org/abs/2406.04692). 2024-06-07, arXiv v1.

[Research index](../../README.md)
