# Protocol resource budgets: bytes, work and retained state

This research models how accepted inputs consume response bytes, processing work and unfinished state.

[Read the study](internet-protocol-amplification-research.md)

## Included implementation

The finite job-graph simulator now charges work before enqueueing, records every admitted/rejected job and measures peak queue occupancy. Chain, cycle and branching fixtures verify hand counts. A separate unvalidated-byte object enforces the three-to-one accounting invariant.

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
uv run --no-project --python .venv/bin/python python budgets.py
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

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study internet-protocol-amplification-research --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Short deadlines reduced peak active work on the slow fixture from 16 to five, but no slow jobs completed under that deadline. Longer deadlines completed all ordinary jobs versus about 80% under the short deadline. The result exposes a resource/completion trade-off in a simulator, not a universally better network policy.

See the [article](internet-protocol-amplification-research.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
