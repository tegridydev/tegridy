# Autoresearch: Citation Tracking for Research Agents

A web research agent has two jobs that can fail independently: finding useful material and preserving what that material supports while an answer is revised.

[Read the study](autoresearch-web-researcher.md)

## Implementation

An immutable local source store now retains exact passages across an initial answer and two revisions. Citation validation distinguishes current, historical, missing and mismatched source spans without retroactively changing the saved status of an earlier answer.

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
uv run --no-project --python .venv/bin/python python evidence.py
```

The `Research` API accepts captured source text and explicitly supplied claims. A changed source version marks an old citation historical; it does not destroy a valid quotation from the retained earlier snapshot.

## Scope and limitations

The fixture validates trace preservation, not entailment or improved writing. Automatic page discovery, fetching, answer generation and independent claim support judging remain separate adapters and studies.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study autoresearch-web-researcher --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
