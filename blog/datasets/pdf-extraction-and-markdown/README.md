# PDF to Markdown: Checking Extraction Fidelity

PDF conversion is one of those jobs where the output can look finished long before I've checked whether it says the same thing.

[Read the post](pdf-extraction-and-markdown.md)

## Implementation

Native PDF extraction now produces page scoped text blocks, explicit empty page/failure outcomes, parser revision and source/output hashes. A staging directory is renamed only after Markdown and its manifest are written. Integrity checking detects changed reading copy bytes. A generated two page fixture verifies a price and an unextracted page.

## Run locally

Run from this directory with Python 3.12.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

Run:

```bash
uv run --no-project --python .venv/bin/python python extract.py source.pdf extraction
```

Output is a new directory containing `extracted.md` and `manifest.json`; existing output directories are refused. `verify(output_path)` checks the reading copy hash. The implementation uses [pypdf native text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html), which does not perform OCR. Encrypted PDFs require a decrypted local copy.

## Scope and limitations

Optional local OCR and a static PDF/text review page are implemented. OCR execution requires pdftoppm and tesseract. Semantic table/equation reconstruction remains unimplemented. “Complete native extraction” means nonempty text on every page, not verified document fidelity. The eighteen layout family study has not run.

[Topic index](../README.md) · [Blog index](../../README.md)
