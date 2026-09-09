# Judge Head Attention: Contextual Head Gating

Judge head attention uses one head’s output to gate other heads after they have computed their representations.

[Read the study](judge-head-attention.md)

## Implementation

The causal recall model now compares ordinary attention, static worker scalars, token state gates and a reserved judge head. A deterministic key/value oracle checks labels, causal tests check masks and gradient tests confirm the gate alters executed worker contributions.

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
uv run --no-project --python .venv/bin/python python experiment.py --steps 40
```

Every head is computed before gating. Saved results are one seed with a separate seeded evaluation set; they are not an independently held out combination benchmark.

## Earlier pilot result

The original forty step run failed to learn useful held out recall: the ordinary condition scored below 1% and the three gated conditions scored 0%. Passing causal mask and gradient tests therefore did not establish task competence. This failed smoke result is retained instead of being hidden. A fixed 400-step follow up produced ordinary 48.4%, static 45.3%, token 39.1%, judge 38.3%. This follow up investigates learnability on the same small task; it is not a new independent evaluation set or a full architecture benchmark. See [learning check.json](learning-check.json).

## Scope and limitations

The original smoke task uses twelve tokens and two pairs. The separate CPU comparison now uses 64-token sequences and disjoint key/value associations. Token MLP parameter counts are reported but not exactly matched. No pruning, skipped work or speed claim follows from these soft gates.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study judge-head-attention --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
