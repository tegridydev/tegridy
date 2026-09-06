# image conversion has more edge cases than the button suggests

“Make this image smaller” sounds like a lovely small feature.

[Read the post](image-conversion-resizing-and-privacy.md)

## Included implementation

The Pillow backend now decodes, applies EXIF orientation, fits without upscaling, handles JPEG alpha against a chosen background, and measures the exact encoded candidates. It selects the highest tested quality meeting the byte limit, or reports an unmet target. Fresh pixel images strip source metadata; ICC preservation is explicit. A local browser form returns the same bytes used in its receipt.

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
python3 app.py
```

Open http://127.0.0.1:5051. CLI example: `python3 convert.py input.png output.jpg --format JPEG --bounds 400 400 --byte-limit 50000`. The receipt reports input/output metadata keys, hashes, frames, dimensions and all measured candidates. The upload limit is 25 MB and decoded input limit is 25 million pixels.

## Files

- [app.py](app.py) — Project-local support file.
- [convert.py](convert.py) — Runnable implementation.
- [image-conversion-resizing-and-privacy.md](image-conversion-resizing-and-privacy.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_app.py](test_app.py) — Local regression checks.
- [test_convert.py](test_convert.py) — Local regression checks.

## Remaining work

Animation export is explicitly first-frame only. There is no crop editor, colour-space conversion or batch interface. WebP depends on the installed Pillow build. Browser routes are exercised with Flask’s test client; a graphical browser was not available.

[Topic index](../README.md) · [Blog index](../../README.md)
