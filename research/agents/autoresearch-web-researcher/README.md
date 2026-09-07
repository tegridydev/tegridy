# Autoresearch: evidence that survives revision

A web-research agent has two jobs that can fail independently: finding useful material and preserving what that material supports while an answer is revised.

[Read the study](autoresearch-web-researcher.md)

## Included implementation

An immutable local source store now retains exact passages across an initial answer and two revisions. Citation validation distinguishes current, historical, missing and mismatched source spans without retroactively changing the saved status of an earlier answer.

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
uv run --no-project --python .venv/bin/python python evidence.py
```

The `Research` API accepts captured source text and explicitly supplied claims. A changed source version marks an old citation historical; it does not destroy a valid quotation from the retained earlier snapshot.

## Files

- [autoresearch-web-researcher.md](autoresearch-web-researcher.md) — Article.
- [evidence.py](evidence.py) — Runnable implementation.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_evidence.py](test_evidence.py) — Local regression checks.

## Remaining work

The fixture validates trace preservation, not entailment or improved writing. Automatic page discovery, fetching, answer generation and independent claim-support judging remain separate adapters and studies.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study autoresearch-web-researcher --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The 100 synthetic histories per seed retained their version-specific citations across answer revisions. The measured result is citation preservation; whether each citation supports its associated claim requires a separate entailment evaluation.

See the [article](autoresearch-web-researcher.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
