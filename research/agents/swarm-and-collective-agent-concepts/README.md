# Swarm mechanisms: sequence generation, routing and motion

Neighbour influence is a design choice, not a single learning algorithm.

[Read the study](swarm-and-collective-agent-concepts.md)

## Included implementation

SW-01 now has a finite grammar, exact legal-sequence enumeration, ordered transition counts, fixed smoothing and four agents with neighbour reweighting. Five seeds compare zero coupling with strength two at exactly 2,000 generated tokens per condition.

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
python3 grammar.py
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
