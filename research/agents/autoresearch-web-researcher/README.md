# Autoresearch: evidence that survives revision

A web-research agent has two jobs that can fail independently: finding useful material and preserving what that material supports while an answer is revised.

[Read the study](autoresearch-web-researcher.md)

## Included implementation

An immutable local source store now retains exact passages across an initial answer and two revisions. Citation validation distinguishes current, historical, missing and mismatched source spans without retroactively changing the saved status of an earlier answer.

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
python3 evidence.py
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
