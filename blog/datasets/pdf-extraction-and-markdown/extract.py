"""Page-scoped native PDF extraction; empty/scanned pages remain explicit gaps."""

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
import pypdf


def extract(path, output):
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
                    record["status"] = "needs-ocr-or-review"
                    record["warnings"].append("No native text; no OCR engine was run.")
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
    return (
        hashlib.sha256((output / "extracted.md").read_bytes()).hexdigest()
        == manifest["output_sha256"]
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    print(json.dumps(extract(a.input, a.output), indent=2))


if __name__ == "__main__":
    main()
