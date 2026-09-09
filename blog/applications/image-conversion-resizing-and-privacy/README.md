# Image Resizing: File Size, Formats and Metadata

“Make this image smaller” sounds like a lovely small feature.

[Read the post](image-conversion-resizing-and-privacy.md)

## Implementation

The Pillow backend now decodes, applies EXIF orientation, fits without upscaling, handles JPEG alpha against a chosen background, and measures the exact encoded candidates. It selects the highest tested quality meeting the byte limit, or reports an unmet target. Fresh pixel images strip source metadata; ICC preservation is explicit. A local browser form returns the same bytes used in its receipt.

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
uv run --no-project --python .venv/bin/python python app.py
```

Open http://127.0.0.1:5051. CLI example: `python3 convert.py input.png output.jpg --format JPEG --bounds 400 400 --byte-limit 50000`. The receipt reports input/output metadata keys, hashes, frames, dimensions and all measured candidates. The upload limit is 25 MB and decoded input limit is 25 million pixels.

## Scope and limitations

Animation export is explicitly first frame only. The batch CLI now records per file outcomes; crop editing and colour space conversion remain outside scope. WebP depends on the installed Pillow build. Browser routes are exercised with Flask’s test client; a graphical browser was not available.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study image-conversion-resizing-and-privacy --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
