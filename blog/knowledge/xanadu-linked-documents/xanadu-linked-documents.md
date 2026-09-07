+++
title = "xanadu-2: links that remember what they point to"
date = "2026"
description = "Normal links point somewhere. I'm interested in links that also remember which version and exact passage I meant when I created them."
draft = false
id = "blog/xanadu-linked-documents"
type = "article"
author = "tegridydev"
topic = "retrieval-evidence"
related = ["research/graph-memory-with-a-paper-trail", "research/sl5-and-independent-research-workflows"]
updated = "2026-09-08"
+++

# [td] tegridydev | xanadu-2: links that remember what they point to

A normal link is useful until the thing on the other end changes.

Linking to a passage is better, but only if the system knows **which version of that passage I meant**.

That's the little idea I keep coming back to with [xanadu-2](https://github.com/tegridydev/xanadu-2): what would a local document system look like if links had durable identity and could point to historical content rather than whatever exists today?

The inspiration comes from Project Xanadu, but I'm interested in a pretty small practical slice of that problem.



<!-- cpu-comparison:start -->
## Recorded findings

All 1,000 passage links survived export/import across 1,000 documents and 2,000 versions. This supports the immutable-passage round-trip contract, including Unicode text; it does not establish distributed editing or an upstream repair.

Local immutable Unicode passage storage and transactional round-trip, not a distributed editor or verified upstream repair.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| documents | 1000 | — |
| preserved links | 1000 | — |
| versions | 2000 | — |

The [comparison record](comparison-results.json) includes the 1 recorded run, measured values, source hashes and dependency versions. This is a single fixed evaluation; no across-seed uncertainty is estimated.
<!-- cpu-comparison:end -->

## identity through an actual round trip

The [document test](test_documents.py) stores `a café note`, links characters 2–6 of version 1, then creates a replacement version. Resolving the original link still returns `café`. JSON export/import retains that link ID and its historical target.

A missing version returns `missing-version`; a corrupted quote causes import rollback. Those are different failures and should remain different in the UI.

The upstream defect discussed here is not tied to a verified upstream commit in this collection. Treat it as motivation for this independent local contract, not a claim that an identified current upstream release is broken. A pinned upstream reproduction remains needed before making that stronger claim.

## documents should have history

I'd separate:

```text
document identity
version
passage
link
```

The document is long-lived. A version is immutable content at one point in its history. A passage link points to a specific version and span.

So if note B quotes note A v1, editing A into v2 doesn't silently rewrite what B originally referred to.

The interface can simply say:

> this quote points to an older version; a newer one exists

instead of swapping the text underneath me.

## even the link needs identity

One small bug in the public implementation made this nicely concrete.

`Link.to_dict` serialises a `link_id`, but the corresponding load path created a new `Link` without restoring that ID.

So the visible target could survive save/load while the link itself became a different object.

That looks fine until backlinks or annotations depend on link identity.

The current implementation is here: [link.py](https://github.com/tegridydev/xanadu-2/blob/main/xanadu-2/document/link.py).

A round-trip test should compare IDs, not just displayed text.

## the smallest useful version

I don't need a universal hypertext network to test this.

A useful first model is:

```text
documents
versions
passage selectors
links
```

Each link knows its own ID and exact target version.

If a target disappears, I'd rather retain a tombstone saying what used to be there than show an empty panel that looks like the link never worked.

For edits, use an expected version. If I'm saving against v3 and somebody already created v4, show the conflict instead of silently overwriting it.

Boring database behaviour is what makes the interesting hypertext behaviour trustworthy.

## what I built from this

The local version now has a SQLite document store with immutable versions, optimistic edit preconditions and exact Unicode passage spans.

Links retain IDs through JSON export/import and resolve historical versions after later edits. Missing targets are distinguished from corrupted quotes, and invalid imports roll back as a transaction.

Start with [documents.py](documents.py) or the [module README](README.md).

The core flow is:

```text
Documents.update(document, text, expected_version)
link(document, version, start, end)
resolve(link_id)
```

[link_reference.py](link_reference.py) is a tiny standard-library round-trip example:

```sh
python3 link_reference.py
```

It checks link identity locally without contacting a service.

Authentication, distributed sync and automatic passage relocation are still outside scope. This is a local storage API, not a complete implementation of Xanadu.

For now I'm happy with the smaller question:

> if I link to this sentence today, can the system still tell me exactly which sentence I meant after everything else changes?

A link that remembers yesterday properly already feels more useful than another link that only knows where `latest` points.

[Blog index](../../README.md)
