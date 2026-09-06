# [td] tegridydev | a readable PDF export can still be wrong

PDF conversion is one of those jobs where the output can look finished long before I've checked whether it is actually right.

A two-column paper can become one readable paragraph with the columns mixed together. A table can lose its headers. An equation can lose one minus sign and still look completely normal.

So I'm less interested in **getting text out of a PDF** than keeping enough information around to notice when the conversion changed the meaning.

## keep the page attached

The page is a useful first boundary.

Inside it, paragraphs, headings, tables and equations should stay distinguishable where the parser supports that. Each block keeps its page, reading order, parser revision and warnings.

```json
{
  "source_id": "fixture-pricing-v1",
  "page": 2,
  "block_id": "table-1",
  "kind": "table",
  "columns": ["item", "price"],
  "rows": [["example part", "12.50"]],
  "warnings": ["currency absent from source header"]
}
```

If the source doesn't say whether `12.50` is dollars, pounds or bottle caps, the converter shouldn't helpfully decide for me.

Page/block identity also gives the UI somewhere useful to go when I click a suspicious value.

## use the expensive path when it earns it

Native text extraction, layout-aware parsing and OCR solve different problems.

[Docling's technical report](https://arxiv.org/abs/2408.09869v5) is useful related work around layout and table-aware conversion. It doesn't mean every document needs the heaviest pipeline.

I'd start cheap and explicit. If native extraction works, use it. If a page has no usable text, mark it for another path rather than calling it a successful empty page.

If two extractors disagree on numbers, that disagreement itself is a useful review queue.

## keep the faithful copy before making it convenient

A readable extraction and a training-ready chunk set are different products.

First preserve the closest faithful copy I can. Then treat heading cleanup, chunking and summarisation as later transformations.

Every run should retain source hash, parser/model revision, settings, page count and a clear outcome:

```text
complete | partial | unsupported | timed-out | cancelled | failed
```

Downloading, converting and reading are also separate states.

A directory full of Markdown papers should never accidentally become a claim that I read every one lol.

## test whether the evidence survived

The fixture I'd want is deliberately annoying: plain text, columns, tables, equations, scans and mixed pages.

Then ask questions whose answers depend on those structures.

The first check isn't whether an LLM answers correctly. It's whether the needed evidence survived conversion. Otherwise model knowledge can hide a dropped table.

I'd keep reading-order errors, missing symbols and table/header mistakes separate rather than collapse everything into one score.

## what I built from this

The local extractor now creates page-scoped native text blocks with explicit empty-page/failure outcomes, parser revision and source/output hashes.

It writes to staging and only renames the directory after `extracted.md` and `manifest.json` are complete. Integrity checking catches later changes.

A generated two-page fixture verifies one known price and one page with no native extractable text.

Start with [extract.py](extract.py) or the [module README](README.md). It uses [pypdf native text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html), so it **does not perform OCR**.

`verify(output_path)` checks the stored reading-copy hash.

OCR, semantic table/equation reconstruction and a comparison UI are still missing. The larger layout-family study hasn't run.

And `complete native extraction` only means every page returned non-empty native text.

It does **not** mean the document survived faithfully.

That's basically the whole lesson: a nice Markdown file is an output format, not a fidelity certificate.

[Blog index](../../README.md)
