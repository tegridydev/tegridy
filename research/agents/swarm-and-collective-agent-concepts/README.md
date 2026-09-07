# Swarm mechanisms: sequence generation, routing and motion

Neighbour influence is a design choice, not a single learning algorithm.

[Read the study](swarm-and-collective-agent-concepts.md)

## Included implementation

SW-01 now has a finite grammar, exact legal-sequence enumeration, ordered transition counts, fixed smoothing and four agents with neighbour reweighting. Five seeds compare zero coupling with strength two at exactly 2,000 generated tokens per condition.

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
uv run --no-project --python .venv/bin/python python grammar.py
```

Likelihood uses occurrence counts, including duplicate sequences; coverage uses distinct legal sequences. The report evaluates a uniform distribution over the four legal sequences, not a natural-language corpus.

## Files

- [grammar.py](grammar.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [swarm-and-collective-agent-concepts.md](swarm-and-collective-agent-concepts.md) — Article.
- [test_grammar.py](test_grammar.py) — Local regression checks.

## Remaining work

The four-sequence grammar is deliberately tiny and can saturate coverage. A changed grammar, topology sweep and downstream training remain necessary before interpreting coupling as useful. SW-02, SW-03 and SW-04 remain distinct proposals.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study swarm-and-collective-agent-concepts --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

Ring coupling covered 99.75% of the changed grammar versus 99.51% for independent generation, but the other grammars showed complete coverage for both. This small fixture-specific difference does not establish a consistent benefit from coupling or useful downstream training data.

See the [article](swarm-and-collective-agent-concepts.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
