# [td] tegridydev | sorting old notes without rewriting history

A research folder can become an archaeological site surprisingly quickly.

There are originals, cleaned versions, exports of cleaned versions, generated summaries and a file called `final` that is somehow older than all of them.

I've been dealing with enough of that lately that I now think less about:

> which file should I keep?

and more about:

> what relationship do these files have?

I want a clean reading copy **without deleting the trail that explains where it came from**.

## “duplicate” can mean a few things

These shouldn't share one delete button.

| relationship | meaning |
|---|---|
| byte-identical | every stored byte matches |
| same body | content matches under an explicit rule |
| revision | something actually changed |
| related topic | they discuss similar things |

A hash proves two byte sequences match. It doesn't tell me why both copies exist.

One might be a backup. One might belong inside another project's reproducibility bundle. Deleting it can break context even if the bytes exist elsewhere.

Normalisation gets sneaky too. Ignore metadata and I might miss changed attribution. Ignore whitespace and I might miss meaningful Python indentation.

The comparison rule belongs beside the result.

## separate the file from the content

I like three small objects:

```text
occurrence
content version
transformation
```

An occurrence says where something was found. A content version identifies the bytes and hash. A transformation says how one version became another.

```json
{
  "operation": "normalise-headings",
  "input_version": "note-v1",
  "output_version": "note-v2",
  "allowed_changes": ["markdown-heading-levels"],
  "review_status": "pending"
}
```

The operation name isn't proof that only headings changed.

The diff is still the check.

W3C PROV already provides useful language for entities, activities and derivation, so I don't need to invent Tegridy Provenance Protocol v7 just because I enjoy naming things. [Groth and Moreau, 2013](https://www.w3.org/TR/prov-overview/).

## prettier can still be worse

This is the annoying part.

A converter can produce cleaner Markdown while damaging source-like text.

```python
class Note:
    def title(self):
        return "Untitled"
```

A bad converter might decide `class Note:` or `def title` looks like a heading. A table parser can lose a minus sign and still return a lovely table.

The output becomes easier to read and less correct.

A link checker only proves the target resolves. A Python parser can catch invalid syntax, but valid code can still behave differently.

Every validator needs a scope.

## sort without touching the originals first

My preferred first pass is boring:

1. inventory paths, sizes and hashes,
2. group exact matches,
3. classify obvious writing, references, generated drafts, code and data,
4. leave the raw files alone.

Only then do I choose a reading copy.

`canonical for reading` doesn't mean `the only true version`. It just means this is what the current index points to.

Transformations happen one at a time in a new output directory. Heading cleanup, summarisation and code repair are separate operations because they're allowed to change different things.

## make a tiny evil fixture first

Before bulk conversion I'd make a few annoying files containing nested fences, equations, tables, Unicode, relative links, metadata differences and intentionally interrupted writes.

Then define exactly what the conversion may change.

If the task is heading cleanup, code bodies should survive exactly. If I'm repairing code, keep the original and test behaviour separately.

I'd also kill a write halfway through on purpose.

An incomplete output should never replace the previous readable version.

A clean exit code is nice.

Recoverability is nicer.

## attribution survives cleanup too

A paper I downloaded remains someone else's paper after I reorganise it.

A generated explanation remains generated until I review it.

An old contents list mentioning a project doesn't prove I built the implementation it describes.

So original author/source metadata stays separate from collection ownership. If authorship is unclear, `unknown` beats guessing.

For public writing, the front door can still stay clean. Publish the finished article with the references it needs and keep the raw archive separately.

I also prefer supporting files beside the project they belong to. A post with screenshots, tests or fixtures is easier to understand when those files travel together.

That's basically the rule:

> make the current collection nicer to use without forcing future-me to trust that the cleanup was perfect.

Given how many folders I've apparently named `final`, future-me deserves the help :)

## reference

Paul Groth and Luc Moreau, editors. **PROV-Overview: An Overview of the PROV Family of Documents.** W3C Working Group Note, 30 April 2013. [Full document](https://www.w3.org/TR/prov-overview/).

[Blog index](../../README.md)
