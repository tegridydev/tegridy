# Synthetic Datasets with Independent Validation

Generating another thousand examples is the easy part.

[Read the post](synthetic-data-generation-and-quality.md)

## Implementation

The inventory generator now creates deterministic source states, two wording templates and minimally changed shipment counterfactuals. An independent parser reconstructs the arithmetic and rejects mismatched answers, changed state or unsupported wording. Parent families are split before variants; overlapping counterfactual states merge into one split group.

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
uv run --no-project --python .venv/bin/python python generate.py inventory.jsonl --count 300 --seed 1729
```

`--count` counts source states, not final rows. Most states produce four rows. Each row keeps parent identity, split, template revision, seed, source state and verifier outcome. The output file must be new.

## Scope and limitations

Free form model rewrites, six rule families, judge comparisons and fine tuning remain separate experiments. The verifier accepts its explicit grammar; it does not certify arbitrary natural language explanations.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study synthetic-data-generation-and-quality --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
