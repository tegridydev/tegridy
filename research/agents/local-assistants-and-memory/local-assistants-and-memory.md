# [td] tegridydev | Local assistant memory: retrieval, validity and reuse

*design study and proposed evaluation*

Saving a conversation is easy. The harder problem is deciding which old information is still relevant, still valid and actually belongs in the next prompt. I’m testing whether a small, auditable memory policy can improve cross-session recall over simple recency while using the same context budget.

The intervention is **retrieval**, not “having a transcript”. If one condition gets more useful context than another simply because it receives more tokens, that tells me nothing about memory quality.

## A memory record that can age properly

A `MemoryItem` needs an opaque owner ID, category, text, source event, recorded time, effective interval, fact key and version. Retrieval should log the query, candidate IDs, scores, selected IDs and budget used. Tool requests and tool results stay separate from memory so that a model-generated procedure does not become executable merely because it was saved under a category called `procedural`.

I use four broad memory categories as intent rather than truth: episodic, semantic, procedural and task memory. Moving an item between them is a recorded transformation. Summaries inherit source-turn references and the same ownership/supersession rules as ordinary memories.

The detail I care about most is **valid time**. If a preference changes today, the new record can supersede the old one for present-tense queries without deleting the old answer to “what was the preference last month?”. Supersession therefore needs owner, fact key and effective interval, not just “newest text wins”.

## The bounded comparison

**Question:** does source-linked, query-relevant retrieval improve multi-session recall over recency-only context under an equal token budget?

I’d use 30 synthetic histories containing stable facts, corrections, irrelevant memories, historical questions and separate owners that can share the same display name. Ten histories are for tuning and twenty are held out. A deterministic recorder captures exactly what each policy placed into context.

Compare:

- no memory;
- the last ten messages;
- keyword retrieval;
- source-linked retrieval with supersession and validity filtering.

Keep model revision, generation settings and maximum context tokens fixed. If embeddings are later added, count their computation and index storage and retain keyword retrieval as the cheap baseline. Measure correct recall, stale-fact use, cross-owner leakage, unsupported claims, retrieval precision, total tokens and latency.

A useful counterfactual check is to change **one** memory while holding the request constant. The answer should change where that fact is relevant and stay stable elsewhere. That demonstrates behavioural dependence on a record; it does not reveal the model’s hidden reasoning.

**What would weaken the idea:** if relevant retrieval does not improve answers, either the policy selected the wrong records or the model could not use them. If any gain disappears when context budgets are equalised, the result was extra context rather than better memory.

## Lifecycle matters too

Memory sits inside an assistant runtime, so failed turns and retries need identity. One application service owns the turn, its asynchronous work and shutdown. Partial generations remain error artifacts until deliberately accepted, and a retry links to the failed attempt rather than pretending it never happened. Voice recordings and generated audio need separate retention rules, and an interruption should invalidate queued audio from an earlier turn.

This is deliberately less ambitious than trying to build a human-like memory system. MemGPT is relevant prior architecture for tiered memory; my immediate question is smaller and easier to audit: **can I retrieve the right old fact, from the right owner, for the right point in time, without spending more context?**

The next useful expansion is memory-utility accounting: on labelled offline tasks, record whether each retrieved item was actually needed for the correct answer. That gives me a way to test storage reduction against recall loss without asking the model to grade its own memories.

## What exists locally

The request recorder now filters by opaque owner ID, effective time and recorded time, resolves supersession per fact key, and logs selected and omitted candidates. Thirty synthetic histories cover corrections, historical queries and same-display-name owners.

Start with [retrieval.py](retrieval.py); the [module README](README.md) lists setup, commands and every supporting file.

Relevance and recency policies share the same eligibility logic. The current rule uses term overlap and a fixed budget; no final-history outcome tunes either rule.

## Related public work

[SES-DMA](https://github.com/tegridydev/SES-DMA) explores distributed agents and dynamic memory. Its README includes empirical language, but this article adopts no benchmark result from that wording. The comparison here requires an explicit retrieval trace and independent held-out tasks before claiming that stored interactions improve performance.

## References

- **Charles Packer; Sarah Wooders; Kevin Lin; Vivian Fang; Shishir G. Patil; Ion Stoica; Joseph E. Gonzalez**. [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560). 2024-02-12, arXiv v2.

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
