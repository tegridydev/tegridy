# Graph Based Research Memory with Source Provenance

This study asks whether explicit relationships between claims, passages and source versions reduce wrong version answers beyond ordinary retrieval with the same metadata.

[Read the study](graph-memory-with-a-paper-trail.md)

## Implementation

The three Cedar sources and five scoped questions are now executable. Retrieval preserves release/deployment metadata, explicit exclusions, a word budget and reviewed edge traversal capped at two hops and forty records. The test confirms that graph and metadata only retrieval select the same evidence on this small fixture.

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
uv run --no-project --python .venv/bin/python python cedar.py
```

An unspecified question returns conditional evidence with `needs-scope`; release 3 is unsupported. An upgrade record cannot silently replace a new deployment default.

## Scope and limitations

This fixture cannot establish a graph advantage: every applicable source is already in the initial candidate set. The sixty document comparison, support judgements and annotation cost measurements remain necessary.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study graph-memory-with-a-paper-trail --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
