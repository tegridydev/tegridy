+++
title = "CloudVec: Vector Index Freshness with a SQLite Outbox"
date = "2026"
description = "Follow updates, deletion and crash recovery through a SQLite outbox, with freshness and replay checks kept separate from semantic search quality."
draft = false
id = "research/cloudvec-paper-search"
type = "research-note"
author = "tegridydev"
topic = "retrieval-evidence"
related = ["blog/embeddings-need-a-contract", "research/graph-memory-with-a-paper-trail"]
status = "implemented"
updated = "2026-09-09"
+++

# CloudVec: Vector Index Freshness with a SQLite Outbox

CloudVec started as a paper search prototype, but the first problem I want to test is more basic than semantic relevance: **can I prove that the search index actually contains the current version of every paper the metadata store says it contains?**

A paper can exist happily in SQLite while never making it into the vector index. A dashboard can then report the right database count and still return incomplete search results. I want index freshness to be an explicit state I can measure rather than something inferred from a green “total papers” number.

## Recorded findings

Rebuilt and reverse replayed indexes matched across the declared runs after updates, deletions and injected pre acknowledgement crashes. This tests application replay and version freshness, not power loss durability or semantic retrieval quality.

Persistent SQLite crash/replay/version/tombstone comparison; supplied fixture vectors only, no semantic relevance measurement.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| injected crashes | 91 | 0 |
| live documents | 43.4 | 1.9494 |
| rebuild equal | 1 | 0 |
| reverse replay equal | 1 | 0 |
| writes | 1000 | 0 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.

## follow one crash through replay

A useful freshness check is a tiny sequence with an awkward order. The [outbox test](test_outbox.py) does this without a remote vector service:

| Step | Authoritative state | Eligible index state |
| --- | --- | --- |
| Commit paper v1 and its job | v1 exists in SQLite | Delivery still needed |
| Apply v1, crash before acknowledgement | Job remains unacknowledged | v1 may already be present |
| Commit and deliver v2 | v2 is current | v2 |
| Retry the old v1 job | v2 remains current | v2; old delivery cannot roll it back |
| Deliver deletion, then retry v2 | Deleted | Empty; tombstone prevents resurrection |

After [setup](README.md), `python -m pytest -q test_outbox.py` checks the sequence, restarts the store, replays pending jobs and compares it with a rebuild. It also checks that no unacknowledged jobs remain.

A database row count cannot tell me any of that. Freshness depends on identity, version and delivery state. If the in memory index is lost after jobs were acknowledged, replaying only pending jobs is insufficient: rebuild from the database.

This is an application of the [transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html): commit the change and its delivery intent together, then make retries safe. This fixture tests delivery mechanics, not semantic relevance or a production worker service.

## Treat the index as a derivative

The metadata database should be authoritative. Each paper record gets a stable provider ID, version, title, authors, abstract, publication/update times, retrieval time, source URL and metadata hash. Titles remain searchable attributes, not primary identities; two different papers are allowed to have the same title.

Indexing then becomes a versioned job. In the same transaction that inserts or updates metadata, write an outbox row containing the paper version ID, text hash, encoder revision and desired index revision. A worker performs an idempotent upsert and only acknowledges the job after the write contract is verified. Failed jobs stay visible and retryable.

This matters because an outbox gives **at least once delivery**, not magical exactly once execution. The index key has to be deterministic, and a delayed retry for version 1 must not overwrite a newer version 2. Deletions need tombstones or explicit removal jobs for the same reason.

The query API should return structured records containing paper ID, metadata version, source text, retrieval score, index revision and any enrichment IDs. Presentation happens afterwards. Database rows, pending jobs, indexed versions and failed jobs become separate dashboard values.

Summaries and named entities are derived annotations, not original evidence. They need their own model revision and input hash, and an updated abstract must not quietly inherit an old summary. I would keep annotation retrieval separate from original abstract retrieval so the interface can show which channel actually surfaced a result.

## First test: can the system recover from boring failures?

Use 50 self authored paper like records, including changed abstracts, duplicate titles and repeated retrievals. Inject failures before metadata commit, after commit, during the index write and just before acknowledgement. An in memory index is enough for this; remote credentials add noise before the state machine is correct.

Compare three policies:

1. direct indexing;
2. rebuilding the complete index;
3. outbox replay.

The main invariant is exact equality between expected and indexed eligible IDs after recovery. Also measure duplicate keys, stale versions, repeated work, recovery time and whether every failure appears in the outcome ledger. A full rebuild is an important baseline because for a small corpus it may simply be the better design.

**What would weaken the idea:** if replay cannot converge cleanly after out of order retries, or if the extra machinery costs more than rebuilding at the target corpus size, keep the simpler approach.

## Search quality is a separate experiment

Once freshness is trustworthy, retrieval can be evaluated on its own. A small pilot could use 200 permitted abstracts or self authored substitutes and 30 labelled queries, comparing lexical, embedding and hybrid retrieval. Enrichment stays off first, then summaries/entity annotations can be added as a separate condition.

BEIR is useful precedent for keeping lexical retrieval in the comparison. The arXiv API is also a reminder that source identity, timestamps and pagination metadata are separate from the paper text itself. I am not trying to claim novelty in paper search here; the narrower contribution is an ingestion to index lifecycle I can inspect and replay.

Two extensions are worth keeping. A **freshness aware result view** can show whether an abstract and its annotations come from the current source version. A **dual view retriever** can keep original text and annotation channels separate rather than merging generated summaries back into the evidence field.

The key result I want first is much less glamorous: after a crash, **is search missing anything, and can the system tell me exactly why?**

## Implementation

SQLite now commits metadata and outbox jobs together. The in memory index adapter enforces monotonically increasing versions and retains deletion tombstones. Crash before ack, out of order retry, restart, empty store and full rebuild fixtures converge to the same final state.

See [outbox.py](outbox.py); the [module README](README.md) describes usage and dependencies.

Use `Store.write`, `deliver`, `replay` and `rebuild`; the test provides the complete crash/recovery sequence. The database is authoritative; an index lost after jobs were acknowledged requires a rebuild.

[Research index](../../README.md)
