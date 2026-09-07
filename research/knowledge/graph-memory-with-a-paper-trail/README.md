# Graph memory with source versions and applicability

This study asks whether explicit relationships between claims, passages and source versions reduce wrong-version answers beyond ordinary retrieval with the same metadata.

[Read the study](graph-memory-with-a-paper-trail.md)

## Included implementation

The three Cedar sources and five scoped questions are now executable. Retrieval preserves release/deployment metadata, explicit exclusions, a word budget and reviewed edge traversal capped at two hops and forty records. The test confirms that graph and metadata-only retrieval select the same evidence on this small fixture.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

Run the tool or experiment after setup:

```bash
uv run --no-project --python .venv/bin/python python cedar.py
```

An unspecified question returns conditional evidence with `needs-scope`; release 3 is unsupported. An upgrade record cannot silently replace a new-deployment default.

## Files

- [cedar.py](cedar.py) — Runnable implementation.
- [graph-memory-with-a-paper-trail.md](graph-memory-with-a-paper-trail.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_cedar.py](test_cedar.py) — Local regression checks.

## Remaining work

This fixture cannot establish a graph advantage: every applicable source is already in the initial candidate set. The sixty-document comparison, support judgements and annotation-cost measurements remain necessary.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study graph-memory-with-a-paper-trail --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Graph expansion recovered the intended support, but the metadata-only control recovered it too. This purpose-built fixture therefore does not establish an advantage for graph structure over the available metadata.

See the [article](graph-memory-with-a-paper-trail.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
