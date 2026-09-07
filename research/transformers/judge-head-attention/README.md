# Judge-head attention: measuring contextual influence

Judge-head attention uses one head’s output to gate other heads after they have computed their representations.

[Read the study](judge-head-attention.md)

## Included implementation

The causal recall model now compares ordinary attention, static worker scalars, token-state gates and a reserved judge head. A deterministic key/value oracle checks labels, causal tests check masks and gradient tests confirm the gate alters executed worker contributions.

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
uv run --no-project --python .venv/bin/python python experiment.py --steps 40
```

Every head is computed before gating. Saved results are one seed with a separate seeded evaluation set; they are not an independently held-out combination benchmark.

## Earlier pilot result

The original forty-step run failed to learn useful held-out recall: the ordinary condition scored below 1% and the three gated conditions scored 0%. Passing causal-mask and gradient tests therefore did not establish task competence. This failed smoke result is retained instead of being hidden. A fixed 400-step follow-up produced ordinary 48.4%, static 45.3%, token 39.1%, judge 38.3%. This follow-up investigates learnability on the same small task; it is not a new independent evaluation set or a full architecture benchmark. See [learning-check.json](learning-check.json).

## Files

- [experiment.py](experiment.py) — Runnable implementation.
- [judge-head-attention.md](judge-head-attention.md) — Article.
- [learning-check.json](learning-check.json) — Recorded synthetic run; scope and provenance included.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [smoke-results.json](smoke-results.json) — Recorded synthetic run; scope and provenance included.
- [test_experiment.py](test_experiment.py) — Local regression checks.

## Remaining work

The original smoke task uses twelve tokens and two pairs. The separate CPU comparison now uses 64-token sequences and disjoint key/value associations. Token-MLP parameter counts are reported but not exactly matched. No pruning, skipped work or speed claim follows from these soft gates.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study judge-head-attention --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The judge gate averaged 44.10% accuracy, ordinary attention 43.92% and the token-MLP gate 44.84%. The small mean differences do not establish a judge-specific advantage; parameter counts differ and all heads are still computed.

See the [article](judge-head-attention.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
