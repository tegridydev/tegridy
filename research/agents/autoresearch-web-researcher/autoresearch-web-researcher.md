+++
title = "Autoresearch: evidence that survives revision"
date = "2026"
description = "A local evidence fixture follows claims and exact citations through source revisions without rewriting earlier answers."
draft = false
id = "research/autoresearch-web-researcher"
type = "research-note"
author = "tegridydev"
topic = "retrieval-evidence"
related = ["research/graph-memory-with-a-paper-trail", "blog/research-without-losing-the-question"]
status = "implemented"
updated = "2026-09-08"
+++

# [td] tegridydev | Autoresearch: evidence that survives revision

*design study and proposed evaluation*

A web-research agent can fail in two separate places: it can find bad material, or it can find good material and then lose what that material actually supported while rewriting the answer. I’m isolating the second problem first. Before live search, ranking or fancy planning, I want a boring local fixture where every claim can be traced back to the exact passage that justified it.

The closest mental model is less “autonomous researcher” and more **lab notebook with a search assistant attached**. The useful output is not just an answer. It is the answer plus a record of what was searched, what was retrieved, which source version was used and which passages support or contradict each factual claim.



<!-- cpu-comparison:start -->
## Recorded findings

The 100 synthetic histories per seed retained their version-specific citations across answer revisions. The measured result is citation preservation; whether each citation supports its associated claim requires a separate entailment evaluation.

Synthetic source-version and answer-revision traces; exact citations do not establish entailment or web research quality.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| histories | 100 | 0 |
| retained historical citations | 344.8 | 15.834 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.
<!-- cpu-comparison:end -->

## the same citation after two revisions

The [evidence fixture](test_evidence.py) retains three answer versions and two source versions. A citation that was `current` in the first answer becomes `historical-version` when checked against the later source state; its original answer record still retains the status recorded at that time.

The last answer can contain both a historical passage and a current passage. That is useful when explaining a correction, provided each claim says which version it relies on. Replacing all old citations with the newest URL would destroy that explanation. Invalid or fabricated spans are rejected separately as `span-mismatch`.

## The evidence contract

A run gets a stable ID, question, scope, time bounds, search budget and configuration revision. Search adapters return one common record containing provider, query, rank, URL, title, snippet, provider timestamp and retrieval status. Missing fields stay missing; I do not want fake normalised scores appearing just because another provider happened to return one.

Fetched evidence keeps the original and final URL, retrieval time, content hash, extraction version and selected passages with offsets. If a page changes at the same URL, that is a new source version rather than an invisible overwrite. A claim then points to one or more evidence records with a relation such as `supports`, `contradicts` or `background`.

That distinction matters during revision. The writer can change wording, merge ideas or propose a hypothesis, but a revision should not silently upgrade “this source suggests X” into “X is established”. If a search fails, the result can still say what was checked and what remains unresolved instead of filling the gap with fluent guesswork.

Runtime ownership is part of the same design. One controller owns workers, cancellation, retry budgets and checkpoints. It may only stop processes it actually started and can identify. Credentials stay outside prompts and evidence exports. For fetching, redirects and destination validation need explicit handling because an evidence collector is still a network client, not a magical safe browser.

## The first fair test

**Question:** does keeping claim-to-passage records through collection and revision reduce unsupported factual statements compared with URL-only notes?

I’d start with 12 frozen page fixtures containing duplicate URLs, changed pages, contradictory dates, extraction failures, missing metadata and instruction-like hostile text. Eight factual questions get hand-labelled claim-to-passage answer keys. Half can be used while building the mechanism and half stay locked for the smoke evaluation.

The comparison is deliberately narrow:

1. URL-only notes;
2. passage-linked notes;
3. passage-linked notes with an explicit contradiction field.

Every condition receives the **same selected source material**, model, context budget and two revision rounds. The URL-only baseline is allowed to see the passages while collecting; it simply does not retain the passage links through revision. Otherwise I would be testing “less evidence versus more evidence”, which is not the question.

Measure supported factual claims, required-fact coverage, citations to the wrong source version, contradiction handling, valid abstention, token cost, wall time and recovery after interruption. When an answer contains no factual claims, support rate is undefined; report abstention and required-fact coverage rather than awarding a perfect score for saying nothing.

**What would weaken the idea:** if passage provenance does not survive revision or does not improve support at comparable coverage, the mechanism is not earning its extra bookkeeping. If hostile fixture text can change application permissions or execution policy, the failure is earlier and more serious: stop at the input boundary.

## Two extensions worth testing later

The first is **evidence expiry** for unstable claims such as software API behaviour. A record can remain historically valid while no longer being acceptable as evidence for “current” behaviour. The trade-off is stale-answer reduction versus unnecessary re-fetching.

The second is **disagreement-first follow-up**. Spend the final search on a claim with conflicting sources rather than whichever topic currently has the smoothest summary. If that resolves more contradictions at the same search budget, it is a useful policy; if not, keep the simpler planner.

This sits beside citation-quality work such as ALCE rather than replacing it. The contribution I’m testing is much narrower: **can the evidence trail survive the messy middle of research, including failures and revisions?**

## Implementation

An immutable local source store now retains exact passages across an initial answer and two revisions. Citation validation distinguishes current, historical, missing and mismatched source spans without retroactively changing the saved status of an earlier answer.

Start with [evidence.py](evidence.py); the [module README](README.md) lists setup, commands and every supporting file.

The `Research` API accepts captured source text and explicitly supplied claims. A changed source version marks an old citation historical; it does not destroy a valid quotation from the retained earlier snapshot.

## References

- **OWASP Cheat Sheet Series contributors**. [Server Side Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html). Living documentation retrieved 2026-09-05.
- **Tianyu Gao; Howard Yen; Jiatong Yu; Danqi Chen**. [Enabling Large Language Models to Generate Text with Citations](https://arxiv.org/abs/2305.14627). 2023-10-31, arXiv v2; record states accepted EMNLP 2023.

## Status

The results apply to the stated datasets and controls. Further experiments described here are proposals unless accompanied by a recorded result.

[Research index](../../README.md)
