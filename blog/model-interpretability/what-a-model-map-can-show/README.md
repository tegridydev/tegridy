# what am I actually looking at in a model map?

The interface I want is easy to picture.

[Read the post](what-a-model-map-can-show.md)

## Included implementation

A standalone browser viewer now reads activation JSON, verifies occurrence identities and representation manifests, and displays raw signed values on one shared colour scale. Null is missing; numeric zero is an observation. It refuses incompatible overlays and labels truncation after 2,000 displayed records.

## Run locally

Open the supplied HTML file directly. No install or build step is needed.

Open `viewer.html` and choose `fixture.json`, or a schema-1 export from the research capture module. The page and its script stay local and make no network requests. Run `node test_viewer.cjs` for the data-contract checks.

## Files

- [fixture.json](fixture.json) — Project-local support file.
- [test_viewer.cjs](test_viewer.cjs) — Local regression checks.
- [viewer.html](viewer.html) — Runnable implementation.
- [viewer.js](viewer.js) — Project-local support file.
- [what-a-model-map-can-show.md](what-a-model-map-can-show.md) — Article.

## Remaining work

The included fixture is synthetic data, not a mapped model. The viewer does not infer circuits, perform semantic token alignment or load a model. JavaScript contract checks pass; graphical interaction was not exercised in a browser.

[Topic index](../README.md) · [Blog index](../../README.md)
