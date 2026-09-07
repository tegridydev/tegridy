# botsim: letting the locals talk

I like the idea of leaving a little community of model personas running and seeing what they do with it.

[Read the post](botsim-local-community.md)

## Included implementation

A local Flask application now runs four personas across two channels. SQLite commits a reply and its completed task together, stores the exact visible context, and rejects late replies to cancelled attempts. Oldest-waiting scheduling, a 100-message ceiling and a depth-three limit bound the session. The default provider produces deterministic fake replies; an explicit Ollama model enables local generation.

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
uv run --no-project --python .venv/bin/python python app.py
```

Open http://127.0.0.1:5050. To use an already installed local model, start with `python3 app.py --ollama-model MODEL_NAME`. Stop the previous process before startup recovery; this is a single-process local app. The adapter follows the [Ollama chat contract](https://docs.ollama.com/api/chat).

## Files

- [app.py](app.py) — Runnable implementation.
- [botsim-local-community.md](botsim-local-community.md) — Article.
- [interface.html](interface.html) — Project-local support file.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_app.py](test_app.py) — Local regression checks.

## Remaining work

The live Ollama adapter has not been exercised against an installed model. Scheduler comparisons, streaming previews, total token accounting, relationship metrics and multi-process workers remain outside this first app. Recovery can repeat a provider call after a crash, but it cannot commit the same task twice.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study botsim-local-community --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The deterministic provider produced 200 messages across 180 tasks and 13 storage reopens. This demonstrates restartable scheduling for the supplied conversation fixture; live Ollama behaviour and the realism of the simulated community were not evaluated.

See the [article](botsim-local-community.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
