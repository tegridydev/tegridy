import io
import pytest
from PIL import Image, PngImagePlugin
from convert import convert


def source():
    b = io.BytesIO()
    meta = PngImagePlugin.PngInfo()
    meta.add_text("private", "location")
    Image.new("RGBA", (160, 90), (255, 0, 0, 0)).save(b, format="PNG", pnginfo=meta)
    return b.getvalue()


def test_geometry_alpha_metadata_and_actual_bytes():
    raw, receipt = convert(source(), "JPEG", (40, 40), background="white")
    with Image.open(io.BytesIO(raw)) as image:
        assert image.size == (40, 22)
        assert min(image.getpixel((0, 0))) > 250
        assert not image.getexif()
    assert "private" not in receipt["output_info_keys"]
    assert receipt["bytes"] == len(raw)


def test_impossible_budget_and_quality():
    raw, receipt = convert(source(), "JPEG", byte_limit=1)
    assert not receipt["target_met"]
    assert receipt["bytes"] == min(c["bytes"] for c in receipt["candidates"])
    raw, receipt = convert(source(), "JPEG", byte_limit=100000)
    assert receipt["quality"] == 95


def test_orientation_animation_and_bad_input():
    b = io.BytesIO()
    exif = Image.Exif()
    exif[274] = 6
    Image.new("RGB", (12, 8)).save(b, format="JPEG", exif=exif)
    _, receipt = convert(b.getvalue())
    assert receipt["dimensions"] == [8, 12]
    b = io.BytesIO()
    Image.new("RGB", (4, 4), "red").save(
        b, format="GIF", save_all=True, append_images=[Image.new("RGB", (4, 4), "blue")]
    )
    with pytest.raises(ValueError):
        convert(b.getvalue())
    assert convert(b.getvalue(), first_frame=True)[1]["input_frames"] == 2
    with pytest.raises(Exception):
        convert(b"not an image")
