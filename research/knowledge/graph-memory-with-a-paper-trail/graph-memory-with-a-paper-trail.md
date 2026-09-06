# [td] tegridydev | Graph memory with source versions and applicability

*system design and evaluation plan*

I want a research memory that can answer two questions at once: **what does this say?** and **what is this statement based on, under which version and conditions?** The proposal is ordinary passage retrieval plus a small graph connecting source versions, passages and claims.

The graph is an index for following evidence. It cannot turn an unsupported statement into a true one, and I do not want graph complexity getting credit for metadata that a flat retriever could have used just as well.

## The minimum graph

Keep three records distinct:

| Record | What it represents | Minimum useful fields |
| --- | --- | --- |
| Source version | An immutable captured document | ID, hash, title, capture/publication time, version label, locator |
| Passage | A span inside one source version | ID, source-version ID, text, heading/page, offsets, extraction method |
| Claim | A statement derived from passages | ID, statement, subject, applicability, support IDs, review status |

Edges such as `derived_from`, `supports`, `contradicts`, `supersedes` and `applies_to` keep their creator, time and evidence. Automatically inferred edges stay labelled as inferred. W3C PROV is useful terminology for provenance, but a JSON or relational store is enough for the first implementation; a graph database is not the research contribution.

Applicability is the important bit. Suppose a fictional service, Cedar, defaults to a 30-second timeout in release 1 and 10 seconds for new release-2 deployments, while an upgrade note says existing deployments retain their configured value. Those statements are not automatically contradictory. The query “what is Cedar’s timeout?” is underspecified unless release/deployment context is known.

`supersedes` also should not erase history. A newer manual can become the current default source while the old version remains valid evidence for a historical question.

## Retrieval should explain what it followed

Ingest sources as immutable snapshots. A changed file becomes a new version. Passage extraction retains span locations and overlap, and candidate claims must resolve back to exact supporting text. Capture time, publication time and effective time stay separate; unknown dates remain unknown.

A bounded retriever can start with lexical/embedding passage search, apply explicit release or as-of filters, then follow reviewed graph edges for at most two hops under a fixed context budget. Every included and excluded record is logged. If the query lacks a condition that changes the answer, return alternatives or ask for scope instead of resolving the ambiguity with confident prose.

Citation resolution is mechanical: does the citation point to a passage that was supplied? Whether that passage actually supports the sentence is a separate support judgement.

## Does the graph buy anything?

Build 60 short fictional documents across several services and releases, including migration rules and conflicting sources. Write 30 questions before testing—10 development, 20 final—with lookups, version-sensitive cases, conflicts and insufficient-evidence cases.

Compare:

1. flat passage retrieval;
2. flat retrieval with the **same version/applicability metadata**;
3. metadata plus graph expansion.

All three use the same generator and final context budget. That metadata-only baseline is crucial: if version filtering solves the problem, graph traversal should not take the credit.

Measure answer correctness, version correctness, supported-claim rate, evidence recall, latency, records visited and human annotation time. Report unanswered cases separately so abstention cannot game support rate.

**What would weaken the idea:** if good flat retrieval with explicit metadata matches the graph, I would keep the simpler system. A graph can spread extraction errors, over-amplify high-degree nodes and make duplicated sources look like independent agreement, so extra structure has to earn its maintenance cost.

The current Cedar fixture is intentionally small enough that every useful source is already easy to retrieve. That makes it good for checking semantics—especially applicability and historical versions—but not for claiming a graph advantage. The real test is whether graph expansion recovers useful qualifications that a metadata-matched flat baseline misses.

## What exists locally

The three Cedar sources and five scoped questions are now executable. Retrieval preserves release/deployment metadata, explicit exclusions, a word budget and reviewed edge traversal capped at two hops and forty records. The test confirms that graph and metadata-only retrieval select the same evidence on this small fixture.

Start with [cedar.py](cedar.py); the [module README](README.md) lists setup, commands and every supporting file.

An unspecified question returns conditional evidence with `needs-scope`; release 3 is unsupported. An upgrade record cannot silently replace a new-deployment default.

## References

1. Paul Groth and Luc Moreau, editors. *PROV-Overview: An Overview of the PROV Family of Documents*. W3C Working Group Note, 30 April 2013. [W3C document](https://www.w3.org/TR/prov-overview/).
2. Darren Edge and colleagues. *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*. 2024, revised 2025. [arXiv:2404.16130, version 2](https://arxiv.org/abs/2404.16130v2).

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
