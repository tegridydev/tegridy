# Hyper Matrix Lattice: adaptive summaries and interval search

This note separates two related data-structure questions: how to allocate detail in a multidimensional summary tree, and how to locate an exact interval in an ordered array.

[Read the study](hyper-matrix-lattice-and-numerical-search.md)

## Included implementation

A self-contained variance-refined 4D tree now complements the sorted interval reference. A fixed variance threshold controls subdivision; raw observations preserve exact answers even when a coarse leaf crosses a query boundary. Tests compare coarse/refined trees on original and shifted queries.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

Run the tool or experiment after setup:

```bash
python3 adaptive_tree.py
```

The earlier standard-library references have their own self-tests:

```bash
python3 interval_reference.py
```

The same half-open count/sum convention is implemented locally in this module. Changing refinement affects traversal/storage; it does not license approximate partial-leaf answers.

## Files

- [adaptive_tree.py](adaptive_tree.py) — Runnable implementation.
- [hyper-matrix-lattice-and-numerical-search.md](hyper-matrix-lattice-and-numerical-search.md) — Article.
- [interval_reference.py](interval_reference.py) — Project-local support file.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_adaptive_tree.py](test_adaptive_tree.py) — Local regression checks.

## Remaining work

The threshold is supplied, not learned. Workload-driven threshold selection, numerically robust high-dynamic-range variance merging and storage/latency evaluation remain unfinished. The current two-pass variance is intended for small finite fixtures.

[Topic index](../README.md) · [Research index](../../README.md)
