import io
from PIL import Image
from app import create_app


def test_actual_browser_response_and_invalid_upload():
    client = create_app().test_client()
    data = io.BytesIO()
    Image.new("RGB", (8, 4), "red").save(data, format="PNG")
    data.seek(0)
    response = client.post(
        "/",
        data={
            "image": (data, "image.png"),
            "width": "4",
            "height": "4",
            "format": "PNG",
        },
    )
    assert (
        response.status_code == 200
        and "data:image/png;base64," in response.text
        and "target_met" in response.text
    )
    assert (
        client.post(
            "/",
            data={
                "image": (io.BytesIO(b"broken"), "image.png"),
                "width": "4",
                "height": "4",
            },
        ).status_code
        == 400
    )
