"""Decode, orient and encode measured image candidates with an explicit receipt."""

import argparse
import hashlib
import io
import json
import warnings
from pathlib import Path
from PIL import Image, ImageOps, features


def convert(
    raw,
    format="PNG",
    bounds=None,
    byte_limit=None,
    qualities=(95, 90, 85, 80, 70, 60, 50),
    first_frame=False,
    background="white",
    preserve_profile=False,
):
    format = format.upper()
    if format not in {"PNG", "JPEG", "WEBP"}:
        raise ValueError("supported formats: PNG, JPEG, WEBP")
    if format == "WEBP" and not features.check("webp"):
        raise ValueError("this Pillow build has no WebP encoder")
    if byte_limit is not None and byte_limit < 1:
        raise ValueError("byte limit must be positive")
    qualities = sorted(set(qualities), reverse=True)
    if (
        not qualities
        or any(type(q) is not int or not 1 <= q <= 100 for q in qualities)
        or len(qualities) > 100
    ):
        raise ValueError("provide 1–100 distinct integer qualities in [1,100]")
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(raw)) as source:
            if source.width * source.height > 25_000_000:
                raise ValueError("input exceeds 25 million pixels")
            frames = getattr(source, "n_frames", 1)
            if frames > 1 and not first_frame:
                raise ValueError("animation requires explicit first-frame export")
            source.load()
            inspected = sorted(source.info)
            profile = source.info.get("icc_profile") if preserve_profile else None
            image = ImageOps.exif_transpose(source).convert("RGBA")
            before = list(image.size)
    if bounds is not None:
        if len(bounds) != 2 or any(type(v) is not int or v <= 0 for v in bounds):
            raise ValueError("bounds must be two positive integers")
        scale = min(1.0, bounds[0] / image.width, bounds[1] / image.height)
        image = image.resize(
            (max(1, int(image.width * scale)), max(1, int(image.height * scale))),
            Image.Resampling.LANCZOS,
        )
    if format == "JPEG":
        canvas = Image.new("RGBA", image.size, background)
        canvas.alpha_composite(image)
        image = canvas.convert("RGB")
    # Construct fresh pixels: none of the input info/EXIF is implicitly forwarded.
    image = Image.frombytes(image.mode, image.size, image.tobytes())
    options = {"icc_profile": profile} if profile else {}
    candidates = []
    for quality in [None] if format == "PNG" else qualities:
        buffer = io.BytesIO()
        image.save(
            buffer,
            format=format,
            **options,
            **({"compress_level": 9} if quality is None else {"quality": quality}),
        )
        candidates.append((quality, buffer.getvalue()))
    fitting = [c for c in candidates if byte_limit is None or len(c[1]) <= byte_limit]
    chosen = fitting[0] if fitting else min(candidates, key=lambda c: len(c[1]))
    quality, encoded = chosen
    with Image.open(io.BytesIO(encoded)) as decoded:
        output_info = sorted(decoded.info)
    receipt = dict(
        format=format,
        dimensions=list(image.size),
        oriented_source_dimensions=before,
        bytes=len(encoded),
        quality=quality,
        target_met=bool(fitting),
        input_frames=frames,
        output_frames=1,
        source_info_keys=inspected,
        output_info_keys=output_info,
        profile_policy="preserve when present" if preserve_profile else "remove",
        source_sha256=hashlib.sha256(raw).hexdigest(),
        output_sha256=hashlib.sha256(encoded).hexdigest(),
        candidates=[dict(quality=q, bytes=len(b)) for q, b in candidates],
    )
    return encoded, receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--format", choices=["PNG", "JPEG", "WEBP"], default="PNG")
    p.add_argument("--bounds", type=int, nargs=2)
    p.add_argument("--byte-limit", type=int)
    p.add_argument("--first-frame", action="store_true")
    p.add_argument("--preserve-profile", action="store_true")
    p.add_argument("--background", default="white")
    a = p.parse_args()
    encoded, receipt = convert(
        a.input.read_bytes(),
        a.format,
        a.bounds,
        a.byte_limit,
        first_frame=a.first_frame,
        background=a.background,
        preserve_profile=a.preserve_profile,
    )
    with a.output.open("xb") as stream:
        stream.write(encoded)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
