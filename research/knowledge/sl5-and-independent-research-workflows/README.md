# SL5: Thread Aware Retrieval and Quote Attribution

SL5 is a proposal for searching technical discussions without losing speaker, quotation and time context.

[Read the study](sl5-and-independent-research-workflows.md)

## Implementation

A ten message thread fixture now resolves nested quotes to the original author/span, retains timestamp correction history and rejects mixed or cyclic quote attribution. Forecast resolution requires a pre outcome interpretation and leaves two vague forecasts unresolvable.

## Run locally

Run from this directory with Python 3.12.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

This module exposes a Python API. Its local tests are complete runnable usage examples, including failure cases.

The `Thread` API stores messages and quote edges; `Forecast` freezes target, deadline and ambiguity. Tests ask five exact span attribution questions and resolve two ambiguous forecasts without hindsight.

## Scope and limitations

No live thread acquisition, semantic retrieval or model answering is included. The larger thread family comparison and human annotation agreement remain experiments.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study sl5-and-independent-research-workflows --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
