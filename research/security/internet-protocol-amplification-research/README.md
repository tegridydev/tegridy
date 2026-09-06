# Protocol resource budgets: bytes, work and retained state

This research models how accepted inputs consume response bytes, processing work and unfinished state.

[Read the study](internet-protocol-amplification-research.md)

## Included implementation

The finite job-graph simulator now charges work before enqueueing, records every admitted/rejected job and measures peak queue occupancy. Chain, cycle and branching fixtures verify hand counts. A separate unvalidated-byte object enforces the three-to-one accounting invariant.

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
python3 budgets.py
```

Depth, cycle detection and a global work budget are separate controls. The QUIC-inspired accounting fixture checks byte totals only; it makes no vulnerability or CPU-cost claim.

## Files

- [budgets.py](budgets.py) — Runnable implementation.
- [internet-protocol-amplification-research.md](internet-protocol-amplification-research.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_budgets.py](test_budgets.py) — Local regression checks.

## Remaining work

There are no sockets or deployed-protocol measurements. HTTP/2 incomplete-state lifetimes, deadline cleanup and the 100-workload study remain extensions. Graph work units are one per admitted job, not measured CPU cycles.

[Topic index](../README.md) · [Research index](../../README.md)
