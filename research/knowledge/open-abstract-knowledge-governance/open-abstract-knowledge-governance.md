+++
title = "OpenAbstract: Versioned Claims and Corrections"
date = "2026"
description = "Follow a claim correction without erasing its history, separating replay correctness, support labels and the rules for the default reading view."
draft = false
id = "research/open-abstract-knowledge-governance"
type = "research-note"
author = "tegridydev"
topic = "retrieval-evidence"
related = ["research/autoresearch-web-researcher", "research/graph-memory-with-a-paper-trail"]
status = "implemented"
updated = "2026-09-09"
+++

# OpenAbstract: Versioned Claims and Corrections

*research design*

OpenAbstract started from a fairly simple idea: preserve public knowledge and its history without pretending that permanence makes the content correct. The research question I care about now is narrower: **how should a system change what readers see after a correction while keeping the original claim, evidence and review history inspectable?**

That separates four things that are easy to blur together: integrity, provenance, truth and moderation.

## Recorded findings

The command journal replayed 100 synthetic cases per seed with zero replay errors. Support labels were supplied explicitly, so this demonstrates persistent state transitions rather than independent evidence assessment or better human governance.

Synthetic command journal crash/replay with explicit support labels; no independent source voting or human governance advantage claim.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| cases | 100 | 0 |
| replay errors | 0 | 0 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.

## change the reading view without erasing the dispute

The [governance fixture](test_governance.py) keeps immutable claim versions and appends decisions separately. An accepted correction can change the default reading pointer; a challenge or appeal can suspend the affected default while keeping its earlier version available.

Missing support leads to deferral, not invented corroboration. Duplicate evidence IDs do not create additional votes. The forty replay histories repeat a fixture pattern: they test the state transitions, not the truth of externally supplied support labels or the fairness of a real moderation process.

## What a permanent record can and cannot promise

A content hash can tell me whether the object I retrieved matches the object that was recorded. It cannot tell me whether the claim is true. Provenance tells me who or what created a claim and which evidence it points to; that still does not guarantee the evidence is good.

Moderation adds another question: which version should readers see by default? I want immutable claim versions plus a **mutable default view pointer**. A correction can become the recommended reading without deleting the earlier version or rewriting history.

A minimum claim record therefore has a claim ID, version ID, statement, applicability, evidence links, author identity, creation time and workflow status. Corrections link to the previous version and explain the change. Disputes identify the contested span and the evidence on each side.

Applicability matters here too. A ten second timeout in one software release and thirty seconds in another are not automatically contradictory. Governance should not resolve missing context with a majority vote.

## Governance needs a rule people can see

Who can submit, challenge, accept, change the default view and appeal? Token ownership, reputation and subject expertise are different signals. I do not want one of them quietly standing in for all three.

The first model is deliberately plain: reviewers have equal permissions and every decision keeps a reason. More elaborate weighting can be tested later as separate conditions. Review events are append only, and an appeal points back to the decision being challenged.

For an evidence weighted baseline, use explicit support, applicability and source family independence rather than an unexplained “evidence quality = 0.83”. Ten duplicate submissions based on one source are repeated claims, not ten independent pieces of corroboration.

## A small governance experiment

Create 40 fictional histories containing correct additions, genuine corrections, version differences, unsupported claims and coordinated duplicates. Compare:

- a simple editorial queue;
- majority voting;
- an evidence weighted rule with a fixed rubric.

Measure acceptance of supported claims, rejection or deferral of unsupported claims, correction delay and the effort required to find the decisive evidence. Correlated voters should be simulated separately from independent reviewers. Keep some dispute families held out so the policy is not evaluated only on the examples that shaped it.

An unresolved outcome is allowed. Sometimes “the available evidence does not decide this” is the correct state.

**What would weaken the idea:** if a simpler editorial queue produces the same correction accuracy and auditability with less coordination cost, that is probably the better public workflow. Distributed storage, tokens or reputation systems should only be added if they solve a measured problem.

The practical target is a reader facing history that answers: **why is this version currently preferred, what evidence supports it, what was challenged and what could change the decision?** Permanence is useful, but it is only one part of that answer.

## Implementation

The correction ledger now separates immutable claim versions, append only review events and the default reading pointer. Challenges and appeals suspend an affected default; appeals identify an earlier decision. Missing support defers rather than manufacturing corroboration.

See [governance.py](governance.py); the [module README](README.md) describes usage and dependencies.

The equal permission fixture retains rejected and deferred versions. Duplicate evidence IDs do not become additional votes. A workflow decision is distinct from evidence being true.

[Research index](../../README.md)
