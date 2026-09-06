# a readable PDF export can still be wrong

PDF conversion is one of those jobs where the output can look finished long before I've checked whether it says the same thing.

[Read the post](pdf-extraction-and-markdown.md)

## Included implementation

Native PDF extraction now produces page-scoped text blocks, explicit empty-page/failure outcomes, parser revision and source/output hashes. A staging directory is renamed only after Markdown and its manifest are written. Integrity checking detects changed reading-copy bytes. A generated two-page fixture verifies a price and an unextracted page.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

Run the tool or experiment after setup:

```bash
python3 extract.py source.pdf extraction
```

Output is a new directory containing `extracted.md` and `manifest.json`; existing output directories are refused. `verify(output_path)` checks the reading-copy hash. The implementation uses [pypdf native text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html), which does not perform OCR. Encrypted PDFs require a decrypted local copy.

## Files

- [extract.py](extract.py) — Runnable implementation.
- [pdf-extraction-and-markdown.md](pdf-extraction-and-markdown.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_extract.py](test_extract.py) — Local regression checks.

## Remaining work

OCR, semantic table/equation reconstruction and a page comparison UI remain unimplemented. “Complete native extraction” means nonempty text on every page, not verified document fidelity. The eighteen-layout-family study has not run.

[Topic index](../README.md) · [Blog index](../../README.md)
