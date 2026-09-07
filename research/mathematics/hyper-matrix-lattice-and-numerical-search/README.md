# Hyper Matrix Lattice: adaptive summaries and interval search

This note separates two related data-structure questions: how to allocate detail in a multidimensional summary tree, and how to locate an exact interval in an ordered array.

[Read the study](hyper-matrix-lattice-and-numerical-search.md)

## Included implementation

A self-contained variance-refined 4D tree now complements the sorted interval reference. A fixed variance threshold controls subdivision; raw observations preserve exact answers even when a coarse leaf crosses a query boundary. Tests compare coarse/refined trees on original and shifted queries.

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
uv run --no-project --python .venv/bin/python python adaptive_tree.py
```

The earlier standard-library references have their own self-tests:

```bash
uv run --no-project --python .venv/bin/python python interval_reference.py
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

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study hyper-matrix-lattice-and-numerical-search --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Adaptive summaries answered the clustered query workload in about 7.3 ms versus 297.6 ms for Python scanning, with about 112 ms of construction. Separately, standard sorted lookup answered the million-value uniform workload in about 0.34 ms versus 215 ms scanning after about 108 ms of sorting. These are distinct algorithms and baselines; sorting benefits are not evidence for a new lattice mechanism.

See the [article](hyper-matrix-lattice-and-numerical-search.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
