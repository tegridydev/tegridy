# BotSim: A Local AI Agent Community Simulator

I like the idea of leaving a little community of model personas running and seeing what they do with it.

[Read the post](botsim-local-community.md)

## Implementation

A local Flask application now runs four personas across two channels. SQLite commits a reply and its completed task together, stores the exact visible context, and rejects late replies to cancelled attempts. Oldest waiting scheduling, a 100-message ceiling and a depth three limit bound the session. The default provider produces deterministic fake replies; an explicit Ollama model enables local generation.

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
uv run --no-project --python .venv/bin/python python app.py
```

Open http://127.0.0.1:5050. To use an already installed local model, start with `python3 app.py --ollama-model MODEL_NAME`. Stop the previous process before startup recovery; this is a single process local app. The adapter follows the [Ollama chat contract](https://docs.ollama.com/api/chat).

## Scope and limitations

The live Ollama adapter has not been exercised against an installed model. Scheduler comparisons, streaming previews, total token accounting, relationship metrics and multi process workers remain outside this first app. Recovery can repeat a provider call after a crash, but it cannot commit the same task twice.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study botsim-local-community --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
