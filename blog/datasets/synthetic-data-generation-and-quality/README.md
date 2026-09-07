# making synthetic data I can actually check

Generating another thousand examples is the easy part.

[Read the post](synthetic-data-generation-and-quality.md)

## Included implementation

The inventory generator now creates deterministic source states, two wording templates and minimally changed shipment counterfactuals. An independent parser reconstructs the arithmetic and rejects mismatched answers, changed state or unsupported wording. Parent families are split before variants; overlapping counterfactual states merge into one split group.

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
uv run --no-project --python .venv/bin/python python generate.py inventory.jsonl --count 300 --seed 1729
```

`--count` counts source states, not final rows. Most states produce four rows. Each row keeps parent identity, split, template revision, seed, source state and verifier outcome. The output file must be new.

## Files

- [generate.py](generate.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [synthetic-data-generation-and-quality.md](synthetic-data-generation-and-quality.md) — Article.
- [test_generate.py](test_generate.py) — Local regression checks.

## Remaining work

Free-form model rewrites, six rule families, judge comparisons and fine-tuning remain separate experiments. The verifier accepts its explicit grammar; it does not certify arbitrary natural-language explanations.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study synthetic-data-generation-and-quality --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The generator produced 40,000 rows from 10,000 parent worlds, rejected 400 deliberately corrupted examples and recorded no split leaks. These checks apply to the explicit inventory-arithmetic grammar; downstream training benefit remains unmeasured.

See the [article](synthetic-data-generation-and-quality.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
