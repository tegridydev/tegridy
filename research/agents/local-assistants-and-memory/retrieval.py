"""Valid-time, owner-scoped retrieval with complete candidate disposition traces."""

from dataclasses import dataclass, asdict
import json
import re


@dataclass(frozen=True)
class Item:
    id: str
    owner: str
    fact_key: str
    text: str
    source_event: str
    effective: int
    recorded: int


class Memory:
    def __init__(self, items=()):
        self.items = []
        for item in items:
            self.add(item)

    def add(self, item):
        if not all(
            isinstance(getattr(item, k), str) and getattr(item, k)
            for k in ["id", "owner", "fact_key", "text", "source_event"]
        ):
            raise ValueError("complete memory provenance required")
        if any(
            old.id == item.id
            or (old.owner, old.fact_key, old.effective)
            == (item.owner, item.fact_key, item.effective)
            for old in self.items
        ):
            raise ValueError("duplicate identity or ambiguous effective time")
        self.items.append(item)

    def retrieve(self, owner, query, as_of, known_at, budget=100, policy="relevant"):
        if budget < 0 or policy not in {"relevant", "recent"}:
            raise ValueError("invalid retrieval policy")
        terms = set(re.findall(r"\w+", query.casefold()))
        trace = []
        eligible = []
        visible = [
            item
            for item in self.items
            if item.owner == owner
            and item.recorded <= known_at
            and item.effective <= as_of
        ]
        current = {}
        for item in visible:
            if (
                item.fact_key not in current
                or current[item.fact_key].effective < item.effective
            ):
                current[item.fact_key] = item
        for item in self.items:
            reason = "candidate"
            if item.owner != owner:
                reason = "other-owner"
            elif item.recorded > known_at:
                reason = "not-yet-recorded"
            elif item.effective > as_of:
                reason = "not-yet-effective"
            elif current.get(item.fact_key) != item:
                reason = "superseded-at-query-time"
            score = len(terms & set(re.findall(r"\w+", item.text.casefold())))
            entry = dict(
                id=item.id,
                reason=reason,
                score=score,
                cost=len(item.text.split()),
                record=asdict(item),
            )
            trace.append(entry)
            if reason == "candidate":
                eligible.append(entry)
        eligible.sort(
            key=lambda e: (
                -e["score"] if policy == "relevant" else 0,
                -e["record"]["effective"],
                e["id"],
            )
        )
        used = 0
        selected = []
        for entry in eligible:
            if policy == "relevant" and entry["score"] == 0:
                entry["reason"] = "no-term-overlap"
            elif used + entry["cost"] > budget:
                entry["reason"] = "budget"
            else:
                entry["reason"] = "selected"
                selected.append(entry["id"])
                used += entry["cost"]
        return dict(
            owner=owner,
            query=query,
            as_of=as_of,
            known_at=known_at,
            policy=policy,
            budget=budget,
            budget_unit="whitespace words, not model tokens",
            used=used,
            selected=selected,
            candidates=trace,
        )


def histories():
    result = []
    for i in range(30):
        owner = f"owner-{i}"
        memory = Memory(
            [
                Item("old", owner, "drink", "drink tea", "event-1", 1, 1),
                Item("new", owner, "drink", "drink coffee", "event-2", 3, 4),
                Item(
                    "other", "other-" + owner, "drink", "drink juice", "event-3", 1, 1
                ),
            ]
        )
        result.append(
            dict(
                history=i,
                split="development" if i < 10 else "held-out",
                display_names={owner: "Alex", "other-" + owner: "Alex"},
                current=memory.retrieve(owner, "drink", 5, 5),
                historical=memory.retrieve(owner, "drink", 2, 5),
                known_then=memory.retrieve(owner, "drink", 3, 3),
            )
        )
    return result


if __name__ == "__main__":
    print(json.dumps(histories(), indent=2))
