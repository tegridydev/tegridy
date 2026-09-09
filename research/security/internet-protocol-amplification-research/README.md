# Protocol Resource Limits and Amplification Modelling

This research models how accepted inputs consume response bytes, processing work and unfinished state.

[Read the study](internet-protocol-amplification-research.md)

## Implementation

The finite job graph simulator now charges work before enqueueing, records every admitted/rejected job and measures peak queue occupancy. Chain, cycle and branching fixtures verify hand counts. A separate unvalidated byte object enforces the three to one accounting invariant.

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
uv run --no-project --python .venv/bin/python python budgets.py
```

Depth, cycle detection and a global work budget are separate controls. The QUIC inspired accounting fixture checks byte totals only; it makes no vulnerability or CPU cost claim.

## Scope and limitations

There are no sockets or deployed protocol measurements. HTTP/2 incomplete state lifetimes, deadline cleanup and the 100-workload study remain extensions. Graph work units are one per admitted job, not measured CPU cycles.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study internet-protocol-amplification-research --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
