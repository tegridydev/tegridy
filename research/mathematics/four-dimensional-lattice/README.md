# Four-dimensional summary trees and time-slice queries

A sparse four-dimensional tree can reuse regional summaries for spatial and time-interval queries.

[Read the study](four-dimensional-lattice.md)

## Included implementation

The sparse sixteen-child tree now retains raw leaf observations for exact partial queries and reuses aggregates only for covered nodes. Tests cover all child codes, boundaries, duplicates, empty results and randomized scan comparisons at depths zero, one and three. A 1,000-point pilot records build and query costs.

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
python3 tree.py
```

The API consumes `(x,y,z,t,value)` tuples in finite half-open bounds. Duplicate coordinates remain separate observations. `pilot-results.json` records local timings; benchmark break-even is conditional on that synthetic workload.

## Local result

On this machine's repeated-query pilot, the clustered workload amortized construction after approximately 27 queries. The uniform workload had no measured break-even because traversal was slower than scanning. These timings depend on two reused query shapes and are too narrow for a general speed claim. Exact counts and sums matched the scan oracle in every timed case.

## Files

- [four-dimensional-lattice.md](four-dimensional-lattice.md) — Article.
- [pilot-results.json](pilot-results.json) — Recorded synthetic run; scope and provenance included.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_tree.py](test_tree.py) — Local regression checks.
- [tree.py](tree.py) — Runnable implementation.

## Remaining work

The saved timing pilot uses only two repeated query shapes across uniform, clustered and identical-coordinate distributions. It is not the preregistered 100-distinct-query or 10,000-point study, and includes no established index or peak-memory comparison.

[Topic index](../README.md) · [Research index](../../README.md)
