# OpenAbstract: correction, evidence and the public reading view

OpenAbstract studies how a knowledge platform should preserve history while changing what readers see after a correction.

[Read the study](open-abstract-knowledge-governance.md)

## Included implementation

The correction ledger now separates immutable claim versions, append-only review events and the default reading pointer. Challenges and appeals suspend an affected default; appeals identify an earlier decision. Missing support defers rather than manufacturing corroboration.

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
python3 governance.py
```

The equal-permission fixture retains rejected and deferred versions. Duplicate evidence IDs do not become additional votes. A workflow decision is distinct from evidence being true.

## Files

- [governance.py](governance.py) — Runnable implementation.
- [open-abstract-knowledge-governance.md](open-abstract-knowledge-governance.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [test_governance.py](test_governance.py) — Local regression checks.

## Remaining work

Forty replay histories exercise a repeated fixture pattern, not a held-out governance benchmark. The evidence rule consumes explicit external support labels; majority voting, independent-source weighting, persistence and adversarial dispute families remain unimplemented.

[Topic index](../README.md) · [Research index](../../README.md)
