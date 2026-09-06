# making synthetic data I can actually check

Generating another thousand examples is the easy part.

[Read the post](synthetic-data-generation-and-quality.md)

## Included implementation

The inventory generator now creates deterministic source states, two wording templates and minimally changed shipment counterfactuals. An independent parser reconstructs the arithmetic and rejects mismatched answers, changed state or unsupported wording. Parent families are split before variants; overlapping counterfactual states merge into one split group.

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
python3 generate.py inventory.jsonl --count 300 --seed 1729
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
