# 4D Range Queries with Sparse Summary Trees

A sparse four dimensional tree can reuse regional summaries for spatial and time interval queries.

[Read the study](four-dimensional-lattice.md)

## Implementation

The sparse sixteen child tree now retains raw leaf observations for exact partial queries and reuses aggregates only for covered nodes. Tests cover all child codes, boundaries, duplicates, empty results and randomized scan comparisons at depths zero, one and three. A 1,000-point pilot records build and query costs.

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
uv run --no-project --python .venv/bin/python python tree.py
```

The API consumes `(x,y,z,t,value)` tuples in finite half open bounds. Duplicate coordinates remain separate observations. `pilot-results.json` records local timings; benchmark break even is conditional on that synthetic workload.

## Earlier pilot result

On this machine's repeated query pilot, the clustered workload amortized construction after approximately 27 queries. The uniform workload had no measured break even because traversal was slower than scanning. These timings depend on two reused query shapes and are too narrow for a general speed claim. Exact counts and sums matched the scan oracle in every timed case.

## Scope and limitations

The saved timing pilot uses only two repeated query shapes across uniform, clustered and identical coordinate distributions. It is not the preregistered 100-distinct query or 10,000-point study, and includes no established index or peak memory comparison.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study four-dimensional-lattice --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
