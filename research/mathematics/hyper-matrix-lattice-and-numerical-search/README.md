# Adaptive Range Summaries and Interval Search

This note separates two related data structure questions: how to allocate detail in a multidimensional summary tree, and how to locate an exact interval in an ordered array.

[Read the study](hyper-matrix-lattice-and-numerical-search.md)

## Implementation

A self contained variance refined 4D tree now complements the sorted interval reference. A fixed variance threshold controls subdivision; raw observations preserve exact answers even when a coarse leaf crosses a query boundary. Tests compare coarse/refined trees on original and shifted queries.

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
uv run --no-project --python .venv/bin/python python adaptive_tree.py
```

The earlier standard library references have their own self tests:

```bash
uv run --no-project --python .venv/bin/python python interval_reference.py
```

The same half open count/sum convention is implemented locally in this module. Changing refinement affects traversal/storage; it does not license approximate partial leaf answers.

## Scope and limitations

The threshold is supplied, not learned. Workload driven threshold selection, numerically robust high dynamic range variance merging and storage/latency evaluation remain unfinished. The current two pass variance is intended for small finite fixtures.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study hyper-matrix-lattice-and-numerical-search --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
