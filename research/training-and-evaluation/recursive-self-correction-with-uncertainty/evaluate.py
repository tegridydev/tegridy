"""Evaluate externally scored one-round revisions with development-only selection."""

import argparse
import json
from pathlib import Path
from metrics_reference import revision_metrics, selective_risk


def evaluate(development, held_out, max_risk=0.1):
    if not development or not held_out or not 0 <= max_risk <= 1:
        raise ValueError("nonempty partitions and valid risk limit required")
    for rows in [development, held_out]:
        if len({r["id"] for r in rows}) != len(rows):
            raise ValueError("duplicate case ID")
        for row in rows:
            if row["rounds"] != 1 or row["cost"] < 0:
                raise ValueError("one frozen round and nonnegative cost required")
            if row["action"] == "retrieval" and not row.get("evidence"):
                raise ValueError("retrieval action requires evidence ledger")
    if {r["group"] for r in development} & {r["group"] for r in held_out}:
        raise ValueError("split group leakage")
    selected = None
    best = -1
    for threshold in [i / 100 for i in range(101)]:
        result = selective_risk(
            [r["after"] for r in development],
            [r["confidence"] for r in development],
            threshold,
        )
        if (
            result["risk"] is not None
            and result["risk"] <= max_risk
            and result["coverage"] > best
        ):
            selected = threshold
            best = result["coverage"]
    metrics = revision_metrics(
        [r["before"] for r in held_out], [r["after"] for r in held_out]
    )
    metrics.update(
        threshold=selected,
        selective=dict(coverage=0.0, risk=None)
        if selected is None
        else selective_risk(
            [r["after"] for r in held_out],
            [r["confidence"] for r in held_out],
            selected,
        ),
        total_cost=sum(r["cost"] for r in held_out),
        cases=held_out,
        scope="Externally supplied correctness labels; no generation or judge model is run.",
    )
    return metrics


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("development", type=Path)
    p.add_argument("held_out", type=Path)
    a = p.parse_args()
    print(
        json.dumps(
            evaluate(
                *[
                    [json.loads(line) for line in path.read_text().splitlines()]
                    for path in [a.development, a.held_out]
                ]
            ),
            indent=2,
            allow_nan=False,
        )
    )
