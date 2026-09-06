# [td] tegridydev | image conversion has more edge cases than the button suggests

“Make this image smaller” sounds like a lovely little feature.

Then I have to ask whether smaller means fewer pixels, fewer bytes, a square canvas, or just *please make this thing upload without complaining*.

That's what I like about small utilities. The button looks simple until the implementation has to decide what the user actually meant.

## geometry first

A 1600 × 900 image fitted inside 400 × 400 should become 400 × 225.

If I also want a square, now I need to pad, crop or stretch it. Those are completely different results, so I don't want one generic `resize` option hiding all three.

```python
def fit_inside(width, height, max_width, max_height):
    values = (width, height, max_width, max_height)
    if any(type(v) is not int or v <= 0 for v in values):
        raise ValueError("dimensions must be positive integers")

    scale = min(1.0, max_width / width, max_height / height)
    return max(1, int(width * scale)), max(1, int(height * scale))
```

No upscaling, preserve aspect ratio and stay inside the bounds.

## measure the file you're actually downloading

If I need a JPEG below 50 KB, I don't want to estimate at one quality and then re-encode differently at the end.

```text
decode
→ orient
→ resize
→ resolve transparency
→ encode candidate
→ measure actual bytes
```

Then choose the highest tested quality that meets the byte target.

Encoded size isn't guaranteed to move perfectly with every quality step, so the search stays bounded and measures real outputs. If none fit, say so instead of quietly shrinking the dimensions.

PNG compression effort and JPEG quality also aren't the same thing. [sharp's output documentation](https://sharp.pixelplumbing.com/api-output/) is a good reminder that one universal quality slider can hide real codec differences.

## metadata removal isn't invisibility

Orientation is a good example.

Strip EXIF too early and an upright photo can export sideways. Apply orientation first, then remove the tag if that's the selected policy.

Metadata removal can drop GPS and descriptive fields, but it cannot remove a street address visible in the pixels. I prefer saying exactly what was stripped rather than calling the result “anonymous”.

Transparency and animation need the same honesty. JPEG requires a chosen background for alpha. Animated input either needs a supported animation path or an explicit first-frame export.

Silent behaviour is the thing I'm trying to avoid.

## give the output a receipt

For each result I want final format, dimensions, encoded bytes, frame count, metadata policy and whether the requested limit was actually met.

The fixture set covers alpha, grayscale, EXIF rotation, text metadata, animation, truncated files, repeated names and impossible size targets.

## what I built from this

The Pillow backend now decodes input, applies EXIF orientation, fits without upscaling, handles JPEG transparency against a chosen background and measures exact encoded candidates.

It selects the highest tested quality meeting the limit or reports that the target wasn't met. Fresh pixel images strip source metadata; ICC preservation is explicit. The browser form returns the same bytes described in its receipt.

Start with [convert.py](convert.py) or the [module README](README.md).

```sh
python3 convert.py input.png output.jpg --format JPEG --bounds 400 400 --byte-limit 50000
```

The local form runs at `http://127.0.0.1:5051`. Uploads are capped at 25 MB and decoded input at 25 million pixels.

Animation is intentionally first-frame only. There is no crop editor, colour-space conversion or batch UI yet, and WebP depends on the installed Pillow build.

For such a tiny tool, there are already enough decisions hiding behind “make image smaller” to keep me entertained :)

[Blog index](../../README.md)
