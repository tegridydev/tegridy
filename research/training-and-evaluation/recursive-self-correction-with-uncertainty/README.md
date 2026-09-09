# LLM Self Correction: Evaluation and Stopping

RSCU tests whether critique changes an answer for a good reason and whether the system selects the right next action: answer, obtain evidence, clarify or acknowledge an unresolved question.

[Read the study](recursive-self-correction-with-uncertainty.md)

## Implementation

The evaluator now consumes externally scored before/after records, freezes a confidence threshold on development data, rejects overlapping split groups and accounts for one critique round, retrieval evidence and declared cost. Harmful edits stay in net change and selective risk results.

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
uv run --no-project --python .venv/bin/python python evaluate.py development.jsonl heldout.jsonl
```

The earlier standard library references have their own self tests:

```bash
uv run --no-project --python .venv/bin/python python metrics_reference.py
```

Each row needs `id`, `group`, Boolean `before`/`after`, `confidence`, `rounds: 1`, nonnegative `cost` and `action`. A retrieval action also needs a nonempty `evidence` ledger. No qualifying development threshold produces explicit abstention.

## Scope and limitations

The bounded CPU adapter generates answers with a pinned GPT Neo checkpoint and scores arithmetic responses with exact labels. Its strict prompt/stopping setup failed the baseline; a suitable competent model intervention dataset remains necessary. The evaluator cannot establish that a confidence estimate is calibrated or that self critique caused an improvement.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study recursive-self-correction-with-uncertainty --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
