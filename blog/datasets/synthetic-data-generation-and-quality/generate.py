"""Template inventory questions with independently parsed arithmetic validation."""

import argparse
import hashlib
import json
import random
import re
from pathlib import Path

PATTERNS = [
    re.compile(
        r"^An item starts with (\d+) units, receives (\d+) and ships (\d+)\. How many remain\?$"
    ),
    re.compile(r"^Stock: (\d+)\. Received: (\d+)\. Shipped: (\d+)\. Remaining\?$"),
]


def verify(record):
    matches = [p.fullmatch(record.get("question", "")) for p in PATTERNS]
    match = next((m for m in matches if m), None)
    if match is None:
        return dict(
            valid=False, reason="wording outside independently parseable grammar"
        )
    start, received, shipped = map(int, match.groups())
    if shipped > start + received:
        return dict(valid=False, reason="impossible shipment")
    expected = start + received - shipped
    valid = (
        type(record.get("answer")) is int
        and record["answer"] == expected
        and record.get("state") == [start, received, shipped]
    )
    return dict(
        valid=valid,
        reason="verified" if valid else "state or answer mismatch",
        expected=expected,
    )


def generate(count=100, seed=1729):
    if count < 1 or count > 100000:
        raise ValueError("count must be 1–100000")
    rng = random.Random(seed)
    seen = set()
    records = []
    while len(seen) < count:
        start, received = rng.randrange(1000), rng.randrange(1000)
        shipped = rng.randrange(start + received + 1)
        state = (start, received, shipped)
        if state in seen:
            continue
        seen.add(state)
        identity = hashlib.sha256(json.dumps(state).encode()).hexdigest()
        split = (
            "train"
            if int(identity[:8], 16) % 10 < 8
            else "development"
            if int(identity[:8], 16) % 10 == 8
            else "test"
        )
        # Counterfactual is grouped with its parent before wording variants exist.
        for variant, shipment in [
            ("original", shipped),
            ("counterfactual", shipped - 1 if shipped else 1),
        ]:
            if shipment > start + received:
                continue
            for template in range(2):
                question = (
                    f"An item starts with {start} units, receives {received} and ships {shipment}. How many remain?"
                    if template == 0
                    else f"Stock: {start}. Received: {received}. Shipped: {shipment}. Remaining?"
                )
                record = dict(
                    parent_id=identity,
                    split=split,
                    variant=variant,
                    template_revision=f"inventory-v1-{template}",
                    state=[start, received, shipment],
                    question=question,
                    answer=start + received - shipment,
                    seed=seed,
                )
                record["verification"] = verify(record)
                records.append(record)
    # Independently sampled parents can collide with another parent's counterfactual.
    # Merge all connected worlds into one split so no exact state crosses partitions.
    parent = {r["parent_id"]: r["parent_id"] for r in records}

    def root(key):
        while parent[key] != key:
            key = parent[key]
        return key

    owners = {}
    for r in records:
        state = tuple(r["state"])
        a = root(r["parent_id"])
        if state in owners:
            b = root(owners[state])
            parent[max(a, b)] = min(a, b)
        else:
            owners[state] = a
    for r in records:
        bucket = int(root(r["parent_id"])[:8], 16) % 10
        r["split"] = "train" if bucket < 8 else "development" if bucket == 8 else "test"
    return records


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("output", type=Path)
    p.add_argument("--count", type=int, default=100)
    p.add_argument("--seed", type=int, default=1729)
    a = p.parse_args()
    with a.output.open("x") as stream:
        for record in generate(a.count, a.seed):
            stream.write(json.dumps(record) + "\n")
