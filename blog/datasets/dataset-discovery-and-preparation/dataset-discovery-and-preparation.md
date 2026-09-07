+++
title = "cleaning a dataset without cleaning away its meaning"
date = "2026"
description = "I want dataset cleanup to remove repetitive work, not quietly decide that IDs are numbers, casing never matters or conflicting duplicates can be thrown away."
draft = false
id = "blog/dataset-discovery-and-preparation"
type = "article"
author = "tegridydev"
topic = "document-dataset-reliability"
related = ["blog/synthetic-data-generation-and-quality", "blog/pdf-extraction-and-markdown"]
updated = "2026-09-08"
+++

# [td] tegridydev | cleaning a dataset without cleaning away its meaning

I want dataset tools to save me repetitive work.

I don't want them deciding that an ID is secretly a number, casing never matters, or two rows with the same key must be interchangeable.

A table can be beautifully clean and still be wrong in some very tidy ways.



<!-- cpu-comparison:start -->
## Recorded findings

The 11,592 input rows were accounted for as 9,411 accepted rows, 941 duplicates, 1,237 quarantined rows, and three rejected rows. The split check found no group leakage. This establishes accounting for the supplied synthetic recipe, not improved downstream model quality.

Synthetic mixed-quality row accounting and grouped splitting; no discovery-provider or downstream-quality claim.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| accepted | 9411 | 0 |
| duplicates | 941 | 0 |
| elapsed seconds | 0.0497992 | 0.0011065 |
| input rows | 11592 | 0 |
| quarantined | 1237 | 0 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.
<!-- cpu-comparison:end -->

## account for every input row

Here is the bounded example in [test_prepare.py](test_prepare.py). The recipe protects `id` and `label`, trims only outer whitespace in `text`, preserves nulls and quarantines conflicting duplicate IDs.

| Input | Outcome | Reason |
| --- | --- | --- |
| `{"id":"0017","text":" A ","label":"X"}` | Accepted as `{"id":"0017","text":"A","label":"X"}` | Only the declared whitespace change |
| `{"id":"0018","text":"a"}` | Quarantined | Conflicts with the next row |
| `{"id":"0018","text":"b"}` | Quarantined | Same identity, different content |
| `null` | Rejected | Not a record |

Four inputs become one accepted, two quarantined and one rejected: nothing quietly disappears. An exact duplicate has its own count; it is different from a conflicting identity.

After [setup](README.md), reproduce the accounting with:

```python
from prepare import prepare
from test_prepare import RECIPE
rows = [{"id":"0017", "text":" A ", "label":"X"},
        {"id":"0018", "text":"a"}, {"id":"0018", "text":"b"}, None]
result = prepare(rows, RECIPE)
assert result["counts"] == {"accepted":1, "quarantined":2, "rejected":1, "duplicates":0}
assert rows[0]["text"] == " A "
```

For related rows, set `group_field` to their shared parent field. The test puts 100 rows with the same parent into one split. That prevents sibling leakage; it does not guarantee a representative evaluation set.

## three rows can already break it

Take:

```text
0017   alpha
0018   beta
0018   gamma
```

Converting IDs to integers turns `0017` into `17`. Keeping the first duplicate makes the disagreement between `beta` and `gamma` disappear. Lowercasing everything could damage code or case-sensitive labels.

My preferred result is boring: keep `0017` as a string and quarantine both conflicting `0018` rows.

One accepted row plus two quarantined rows still accounts for all three inputs.

Nothing mysteriously vanished during “cleanup”.

## make the recipe readable

I prefer a small explicit recipe over one clever automatic cleaner.

```json
{
  "id_field": "record_id",
  "protected_fields": ["record_id", "label"],
  "trim_outer_whitespace": ["description"],
  "duplicate_key_policy": "quarantine-conflicts",
  "missing_value_policy": "preserve-null"
}
```

Discovery tells me which dataset revision I found. Profiling describes it. The recipe says what changes are allowed. Execution writes a new version and records what happened to every row.

A blank field, missing key and failed parse are also different things. They shouldn't all become `""` because it makes the dataframe look nicer.

## split before making more copies

The split should belong to whatever I'm trying to generalise beyond: a person, device, conversation, repository, document or time period.

Chunks and paraphrases inherit their parent's split. Otherwise I can create a shiny “unseen” evaluation row by rewriting something the model already trained on.

A seed only makes the assignment repeatable. It doesn't make the grouping sensible.

[Deduplicating Training Data](https://arxiv.org/abs/2107.06499v2) is useful background on overlap, while [Datasheets for Datasets](https://arxiv.org/abs/1803.09010v8) gives a framework for documenting the resulting collection.

## show me the weird rows

A random preview can miss exactly what a cleaner is likely to damage.

I'd deliberately surface leading-zero IDs, rare labels, malformed rows and duplicate conflicts. The before/after view should say **why** each change happened.

Once I can follow one awkward row all the way through, bulk processing starts feeling useful instead of slightly terrifying.

## what I built from this

The local recipe engine reads CSV, JSON arrays and JSONL without coercing numeric-looking IDs.

It preserves protected fields, logs whitespace edits, quarantines conflicting duplicates, counts identical repeats separately and assigns deterministic group splits. Every input row is accounted for.

Start with [prepare.py](prepare.py) or the [module README](README.md).

The supplied recipe expects string `record_id` values. An optional `group_field` keeps related children together; otherwise the ID becomes the split group. Hash buckets target 80/10/10 without pretending that guarantees exact class balance.

The engine only supports explicit recipe operations. Dataset discovery providers, augmentation and an interactive row-diff UI are still separate work.

Malformed JSONL rows can be rejected individually; malformed whole JSON/CSV files remain file-level errors.

That's the direction I want: make the dataset easier to use without making its history harder to explain.

[Blog index](../../README.md)
