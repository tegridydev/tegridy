"""Page-scoped native PDF extraction; empty/scanned pages remain explicit gaps."""

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
import pypdf


def extract(path, output, ocr=None, review=False):
    raw = path.read_bytes()
    if not raw.startswith(b"%PDF-"):
        raise ValueError("PDF signature missing")
    if len(raw) > 100_000_000:
        raise ValueError("input exceeds 100 MB limit")
    reader = pypdf.PdfReader(path)
    if reader.is_encrypted:
        raise ValueError("encrypted PDF: supply a decrypted local copy")
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="." + output.name + "-", dir=output.parent))
    pages = []
    chunks = []
    try:
        for number, page in enumerate(reader.pages, 1):
            record = dict(page=number, blocks=[], warnings=[])
            try:
                text = page.extract_text() or ""
                if text.strip():
                    record["blocks"] = [
                        dict(
                            block_id=f"page-{number}-native",
                            kind="native-text",
                            text=text,
                            reading_order=0,
                        )
                    ]
                    record["status"] = "extracted"
                    record["warnings"].append(
                        "Native extraction does not validate layout, tables or equations."
                    )
                else:
                    text = ocr(path, number) if ocr is not None else ""
                    if text.strip():
                        record["blocks"] = [dict(block_id=f"page-{number}-ocr", kind="ocr-text", text=text, reading_order=0)]
                        record["status"] = "ocr-extracted"
                        record["warnings"].append("OCR text requires fidelity and reading-order review.")
                    else:
                        record["status"] = "needs-ocr-or-review"
                        record["warnings"].append("No text returned by OCR." if ocr is not None else "No native text; no OCR engine was run.")
            except Exception as error:
                record["status"] = "failed"
                record["warnings"].append(f"{type(error).__name__}: {error}")
            pages.append(record)
            chunks.append(
                f"## Page {number}\n\n"
                + (
                    "\n\n".join(b["text"] for b in record["blocks"])
                    or "[No text extracted: manual review required.]"
                )
            )
        markdown = "\n\n".join(chunks) + "\n"
        (staging / "extracted.md").write_text(markdown)
        manifest = dict(
            source_name=path.name,
            source_sha256=hashlib.sha256(raw).hexdigest(),
            parser="pypdf",
            parser_version=pypdf.__version__,
            page_count=len(pages),
            status="complete-native-extraction"
            if pages and all(p["status"] == "extracted" for p in pages)
            else "partial",
            pages=pages,
            output_sha256=hashlib.sha256(markdown.encode()).hexdigest(),
        )
        manifest["ocr_engine"] = getattr(ocr, 'engine', 'supplied callback') if ocr is not None else None
        if pages and all(p['status'] in {'extracted', 'ocr-extracted'} for p in pages) and any(p['status'] == 'ocr-extracted' for p in pages):
            manifest['status'] = 'complete-text-extraction-with-ocr'
        if review:
            import html
            (staging / 'source.pdf').write_bytes(raw)
            body = ''.join('<section><h2>Page '+str(p['page'])+'</h2><p>'+html.escape(p['status'])+'</p><pre>'+html.escape('\n\n'.join(b['text'] for b in p['blocks']))+'</pre></section>' for p in pages)
            (staging / 'review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>PDF extraction review</title><style>body{font:16px system-ui;margin:1rem}main{display:grid;grid-template-columns:1fr 1fr;gap:1rem}iframe{width:100%;height:90vh;position:sticky;top:0}pre{white-space:pre-wrap;overflow-wrap:anywhere}@media(max-width:700px){main{display:block}iframe{height:45vh}}</style><h1>PDF extraction review</h1><p>Check reading order, numbers, tables and equations against the original.</p><main><iframe title="Original PDF" src="source.pdf"></iframe><div>'+body+'</div></main></html>')
        manifest['files'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in staging.iterdir() if p.is_file()}
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False)
        )
        # Receipt is committed only with both hashed extraction and page records.
        os.rename(staging, output)
        return manifest
    except BaseException:
        import shutil

        shutil.rmtree(staging)
        raise


def verify(output):
    manifest = json.loads((output / "manifest.json").read_text())
    if hashlib.sha256((output / "extracted.md").read_bytes()).hexdigest() != manifest["output_sha256"]:
        return False
    for name, digest in manifest.get('files', {}).items():
        if name not in {'extracted.md', 'source.pdf', 'review.html'} or not (output / name).is_file() or hashlib.sha256((output / name).read_bytes()).hexdigest() != digest:
            return False
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument('--ocr', action='store_true')
    p.add_argument('--language', default='eng')
    p.add_argument('--review', action='store_true')
    a = p.parse_args()
    from ocr import tesseract
    print(json.dumps(extract(a.input, a.output, tesseract(a.language) if a.ocr else None, a.review), indent=2))


if __name__ == "__main__":
    main()
