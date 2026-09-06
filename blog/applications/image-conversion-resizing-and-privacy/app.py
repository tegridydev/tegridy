"""Loopback-only browser interface for the local measured image converter."""

import base64
import json
from flask import Flask, request, render_template_string
from convert import convert

PAGE = """<!doctype html><html lang="en"><meta charset="utf-8"><title>Local image tools</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font:16px system-ui;max-width:800px;margin:2rem auto;padding:1rem}label{display:block;margin:1rem 0}img{max-width:100%}pre{white-space:pre-wrap}</style><h1>Local image tools</h1><p>Decode, orient, fit and encode. Processing happens in this local Python app.</p><form method="post" enctype="multipart/form-data"><label>Image <input name="image" type="file" accept="image/*" required></label><label>Format <select name="format"><option>PNG</option><option>JPEG</option><option>WEBP</option></select></label><label>Maximum width <input name="width" type="number" min="1" value="800" required></label><label>Maximum height <input name="height" type="number" min="1" value="800" required></label><label>Byte limit (optional) <input name="limit" type="number" min="1"></label><label><input name="first_frame" type="checkbox"> Export first frame if animated</label><button>Convert</button></form>{% if error %}<p role="alert">{{error}}</p>{% endif %}{% if data %}<h2>Measured output</h2><img src="{{data}}" alt="Converted image preview"><p><a href="{{data}}" download="converted.{{extension}}">Download these exact encoded bytes</a></p><pre>{{receipt}}</pre>{% endif %}</html>"""


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 25_000_000

    @app.before_request
    def local_only():
        from flask import abort

        if request.host.split(":")[0] not in {"127.0.0.1", "localhost"}:
            abort(403)
        if request.headers.get("Origin") not in {None, request.host_url.rstrip("/")}:
            abort(403)

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "GET":
            return render_template_string(PAGE)
        try:
            format = request.form.get("format", "PNG")
            raw = request.files["image"].read()
            bounds = (int(request.form["width"]), int(request.form["height"]))
            limit = int(request.form["limit"]) if request.form.get("limit") else None
            encoded, receipt = convert(
                raw, format, bounds, limit, first_frame="first_frame" in request.form
            )
            mime = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}[
                format
            ]
            return render_template_string(
                PAGE,
                data="data:" + mime + ";base64," + base64.b64encode(encoded).decode(),
                extension=format.lower(),
                receipt=json.dumps(receipt, indent=2),
            )
        except (ValueError, KeyError, OSError) as error:
            return render_template_string(PAGE, error=str(error)), 400

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5051, threaded=False)
