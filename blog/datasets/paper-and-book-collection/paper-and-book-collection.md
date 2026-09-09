+++
title = "Organising Research Papers, Books and Reading Notes"
date = "2026"
description = "Keep selection, acquisition and reading separate in a research collection, with source versions and the question behind each saved paper or book."
draft = false
id = "blog/paper-and-book-collection"
type = "article"
author = "tegridydev"
topic = "document-dataset-reliability"
related = ["blog/pdf-extraction-and-markdown", "research/autoresearch-web-researcher"]
updated = "2026-09-09"
+++

# Organising Research Papers, Books and Reading Notes

I can build a reading queue much faster than I can read it.

That part is easy :)

The harder bit is coming back later and remembering **why I saved something**, especially when the same paper appeared under three searches.

I want the queue to remember the question behind the download.

## selected is not acquired, and acquired is not read

For a small illustrative queue, keep these states separate:

| Record | What it establishes |
| --- | --- |
| Work selected to check a claim | Why the work entered the queue |
| Edition v1 with its source and rights note | Which version could be acquired; not proof of a completed download |
| Reading event: v1, pages 2 to 3 | What was actually recorded as read |
| Edition v2 added later | Another version exists; it does not inherit v1's reading event |

The [restart test](test_reading_queue.py) retains two editions and a reading event attached only to v1. It rejects reading an unknown edition and an empty reading scope. Acquisition receipts still need their own evidence: a URL in SQLite is not a successful download receipt.

## a download isn't a reading history

Discovery, selection, download, conversion and reading are separate events.

A failed download doesn't erase a good selection reason. A successful Markdown conversion doesn't mean I read the paper. Having a PDF in a folder definitely doesn't mean I checked it closely enough to cite it.

Books make identity messier. A chapter, edition and complete book can overlap without being interchangeable.

```json
{
  "work_id": "fictional-memory-handbook",
  "edition": "2",
  "part": "chapter-4",
  "question": "How are stale records replaced?",
  "selection_reason": "Compare the replacement rule with FIFO",
  "acquisition": "pending",
  "reading": "metadata-only"
}
```

Real entries need resolvable bibliographic information, URLs and whatever verification I've actually done. Matching a title alone isn't enough.

## let failed files fail honestly

If a download dies halfway through, I don't want `paper.pdf` sitting there looking complete.

Write to staging first. Record the expected revision, bytes, hash and outcome. Only publish the completed file after validation.

The selection reason survives even when the transfer doesn't. The [PDF conversion post](../pdf-extraction-and-markdown/pdf-extraction-and-markdown.md) covers what happens after the file arrives.

[OAI PMH](https://www.openarchives.org/OAI/openarchivesprotocol.html) is useful for metadata harvesting, but finding metadata and having permission to redistribute a file are separate questions.

## organise around the question

A dashboard saying I have 842 papers mostly tells me I should stop downloading papers.

What I actually want is:

```text
question
├── candidate references
├── evidence checked
├── contradictory source
└── still missing
```

One short selection reason and a reading state is probably enough. Too much friction and I'll just stop using the tool.

## Implementation checks and recorded findings

The fixture retained 100 selected items, 50 acquisition records and 25 reading records as separate states. Acquisition did not imply that an item had been read. The check validates the state model and persistence, not discovery quality or permission to redistribute a real document.

Local synthetic selection/acquisition/read state persistence; no automatic rights determination or claim of reading real papers.

| Recorded metric | Value |
| --- | ---: |
| acquired | 50 |
| reading records | 25 |
| selected | 100 |

The [comparison record](comparison-results.json) includes the 1 recorded run, measured values, source hashes and dependency versions. This is a single fixed evaluation; no across seed uncertainty is estimated.

## what I built from this

The local SQLite queue separates works, editions, acquisition receipts and page/section reading notes.

Stable IDs replace title matching. Foreign keys reject notes for unknown editions and local files receive SHA 256 receipts. Reading one edition doesn't mark every edition read.

See [reading_queue.py](reading_queue.py) or the [module README](README.md).

```sh
python3 reading_queue.py reading.sqlite edition cedar-v1 cedar 1 https://example.org/manual "self-authored fixture" --file manual.pdf
python3 reading_queue.py reading.sqlite read cedar-v1 "pages 2-3" "checked timeout"
```

`export` writes the queue as JSON.

The [acquisition helper](acquire.py) downloads an explicitly selected HTTPS file against a pinned hash and byte limit. Provider discovery and rights verification remain outside scope. A rights description in the database is supplied metadata, not a legal determination.

For now I mostly want the queue to remember the thing I apparently trusted past me to remember manually.

That strategy has not been going amazingly :)

[Blog index](../../README.md)
