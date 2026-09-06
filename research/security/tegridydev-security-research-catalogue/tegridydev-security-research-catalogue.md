# [td] tegridydev | Security research: evidence, evaluation and open leads

*defensive research overview*

These are separate security-research leads that happen to share one useful principle: **an observation should not quietly become a stronger claim as it moves through a tool**. A parser result is not attribution, a static code feature is not malicious intent, and a dashboard count is not automatically the underlying truth.

I use one small evidence record across the leads—source identity/revision, exact span or event range, collection method, transformation history and unresolved questions—while keeping each threat model and label definition separate. PROV-DM is useful vocabulary for provenance without requiring a ledger or standards-conformance claim.

## SEC-01 — evidence-linked incident review

Give a single analyst and an analyst/reviewer pair the same fictional logs, inventory and conflicting notes. Compare supported findings, missed decisive evidence, invented actions and review time under matched total input/output budgets. Add a deterministic checklist and a single-model second-pass baseline so “another reasoning round” is not mistaken for an agent benefit.

The artifact I want is a report where every factual finding opens the exact event that supports it. This is the strongest next study because fictional incident packets give me a clean answer key without touching real organisations.

## SEC-02 — contract context and false alarms

Static features can appear in legitimate privileged administration and abusive behaviour. Keep vulnerable code, malicious intent, misleading promotion and unexpected administration as different labels. Use inert contract/event fixtures grouped by project family and compare rules, static-analysis features and context-aware classification at matched recall.

Slither is relevant static-analysis prior work; it is not a fraud oracle. The useful result would be fewer false positives on legitimate administration without hiding known malicious fixtures.

## SEC-03 — local-model safety evaluation

Interesting failure examples are cases, not prevalence estimates. Build matched benign and bounded problematic contexts, declare the intended response behaviour before generation and measure both inappropriate assistance and unnecessary refusal. Paraphrase/order controls should survive before making a general claim.

A model judge can help with annotation, but disputed examples and reviewer disagreement stay visible rather than becoming one unquestioned score.

## SEC-04 and SEC-05 — identity and bounded processing

For public-source identity work, every provider result needs query, retrieval time, parser revision, entity, source and error state. “Adapter unavailable” must not become “searched successfully, found nothing”. The first success criterion is fewer wrong entity merges, not a bigger table.

For asynchronous domain processing, use synthetic addresses and resolver fixtures. Compare sequential and bounded concurrency, retain retry state across restart and measure wall time, peak tasks and missing/misclassified records. Syntax validity still does not prove mailbox existence or identity, and there is no need to send mail or probe live mailboxes to test the scheduler.

## SEC-06/07 — unresolved source identities

`inst4.py` and `Butcher.py` stay as source-recovery leads until their actual revisions can be recovered and compared. A filename or vague description is not enough to merge a project into another one.

If a future file-carving study emerges from that recovery, it should use synthetic images with known bytes and offsets, comparing header-only candidates with format validation. Count complete/partial recovery, false positives and offset error. That is an evaluation target, not a claim that the missing tool already implements it.

## SEC-08 — indexer information quality

Use fictional event ledgers with labelled relevant activity and noise. Compare raw counts, deduplicated counts and contextual summaries, measuring metric distortion and whether a reviewer can trace a displayed number back to its source events. A misleading dashboard does not imply a broken append-only history; aggregation quality is its own problem.

## What I’d actually work on next

SEC-01 is the cleanest next experiment because the evidence can be hand-labelled and every correction can propagate through a report without involving live targets. The existing resource-budget and signal-detection studies stay separate because their units, threat models and falsifiers are different.

The common infrastructure can be provenance. The conclusions cannot. That boundary is probably the most useful thing this catalogue contributes right now.

## Current implementation map

The [resource-budget simulator](../internet-protocol-amplification-research/README.md) now checks finite graph and byte-accounting invariants. The [signal study](../sigint-spectrum-analysis-and-covert-channel-concepts/README.md) includes an executable generator, classifiers and a saved synthetic result showing poor CNN shift transfer. Neither is a deployed vulnerability finding. Incident-correction fixtures and the unresolved inst4/Butcher source identities remain open; no identity or evidence has been invented to fill those gaps.

[Research index](../../README.md)

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
