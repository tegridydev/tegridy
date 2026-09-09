# Swarm Sequence Generation: Neighbour Coupling Tests

Neighbour influence is a design choice, not a single learning algorithm.

[Read the study](swarm-and-collective-agent-concepts.md)

## Implementation

SW-01 now has a finite grammar, exact legal sequence enumeration, ordered transition counts, fixed smoothing and four agents with neighbour reweighting. Five seeds compare zero coupling with strength two at exactly 2,000 generated tokens per condition.

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
uv run --no-project --python .venv/bin/python python grammar.py
```

Likelihood uses occurrence counts, including duplicate sequences; coverage uses distinct legal sequences. The report evaluates a uniform distribution over the four legal sequences, not a natural language corpus.

## Scope and limitations

The four sequence grammar is deliberately tiny and can saturate coverage. A changed grammar, topology sweep and downstream training remain necessary before interpreting coupling as useful. SW-02, SW-03 and SW-04 remain distinct proposals.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study swarm-and-collective-agent-concepts --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
