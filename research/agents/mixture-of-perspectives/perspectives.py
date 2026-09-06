"""Explicit hard constraints, value weights and sensitivity on fictional cases."""

import json
import math


def evaluate(actions, weights, constraints):
    if len({a['id'] for a in actions}) != len(actions):
        raise ValueError("unique action IDs required")
    if any(not math.isfinite(v) for v in constraints.values()):
        raise ValueError("finite constraint ceilings required")
    if (
        not weights
        or any(not math.isfinite(w) or w < 0 for w in weights.values())
        or sum(weights.values()) <= 0
    ):
        raise ValueError("nonnegative finite weights with positive total required")
    results = []
    for action in actions:
        if any(not math.isfinite(action['facts'][name]) for name in constraints):
            raise ValueError("finite constrained facts required")
        values = action["scores"]
        if set(values) != set(weights) or any(
            not math.isfinite(v) or not 0 <= v <= 1 for v in values.values()
        ):
            raise ValueError("shared [0,1] score rubric required")
        failed = [
            name
            for name, ceiling in constraints.items()
            if action["facts"][name] > ceiling
        ]
        results.append(
            dict(
                id=action["id"],
                feasible=not failed,
                failed_constraints=failed,
                utility=sum(weights[k] * values[k] for k in weights)
                / sum(weights.values()),
            )
        )
    feasible = [r for r in results if r["feasible"]]
    best = max((r["utility"] for r in feasible), default=None)
    winners = [
        r["id"] for r in feasible if math.isclose(r["utility"], best, abs_tol=1e-12)
    ]
    pareto = [
        a["id"]
        for a in actions
        if next(r for r in results if r["id"] == a["id"])["feasible"]
        and not any(
            b["id"] != a["id"]
            and next(r for r in results if r["id"] == b["id"])["feasible"]
            and all(b["scores"][k] >= a["scores"][k] for k in weights)
            and any(b["scores"][k] > a["scores"][k] for k in weights)
            for b in actions
        )
    ]
    return dict(results=results, winners=winners, pareto=pareto)


def cases():
    rows = []
    for i in range(40):
        actions = [
            dict(id="fast", scores=dict(speed=0.9, cost=0.3), facts=dict(spend=80 + i)),
            dict(id="cheap", scores=dict(speed=0.4, cost=0.9), facts=dict(spend=40)),
        ]
        outcomes = {
            name: evaluate(actions, weights, dict(spend=100))
            for name, weights in [
                ("speed-first", dict(speed=0.8, cost=0.2)),
                ("cost-first", dict(speed=0.2, cost=0.8)),
            ]
        }
        shifted = evaluate(actions, dict(speed=0.8, cost=0.2), dict(spend=70))
        rows.append(
            dict(
                id=i,
                split="development" if i < 20 else "held-out",
                actions=actions,
                perspectives=outcomes,
                factual_budget_shift=shifted,
            )
        )
    return dict(
        rubric="scores fixed in [0,1]; speed and cost are fictional utilities, not ethical ground truth",
        cases=rows,
    )


if __name__ == "__main__":
    print(json.dumps(cases(), indent=2))
