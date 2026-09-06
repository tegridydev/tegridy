"""Apply an explicit, non-executable recipe to CSV, JSON or JSONL records."""

import argparse
import csv
import hashlib
import json
from pathlib import Path


def load(path):
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as stream:
            return list(csv.DictReader(stream))
    if path.suffix.lower() == ".json":
        value = json.loads(path.read_text())
        if not isinstance(value, list):
            raise ValueError("JSON input must be an array")
        return value
    rows = []
    for line in path.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append(None)
    return rows


def prepare(rows, recipe, seed=1729):
    if recipe.get("duplicate_key_policy") != "quarantine-conflicts":
        raise ValueError("supported duplicate policy: quarantine-conflicts")
    if recipe.get("missing_value_policy") != "preserve-null":
        raise ValueError("supported missing policy: preserve-null")
    key = recipe["id_field"]
    trim = recipe.get("trim_outer_whitespace", [])
    protected = set(recipe.get("protected_fields", [])) | {key}
    if protected.intersection(trim):
        raise ValueError("cannot transform protected fields")
    rejected, groups = [], {}
    for index, row in enumerate(rows):
        if (
            not isinstance(row, dict)
            or not isinstance(row.get(key), str)
            or not row[key]
        ):
            rejected.append(
                {
                    "source_row": index,
                    "reason": "object with nonempty string ID required",
                    "input": row,
                }
            )
            continue
        entry = {"source_row": index, "input": row, "output": dict(row), "changes": []}
        for field in trim:
            value = row.get(field)
            if isinstance(value, str) and value.strip() != value:
                entry["output"][field] = value.strip()
                entry["changes"].append(
                    {"field": field, "before": value, "after": value.strip()}
                )
        groups.setdefault(row[key], []).append(entry)
    accepted, quarantined, duplicates = [], [], []
    for identity, entries in groups.items():
        # Compare originals: normalisation must not conceal a disagreement.
        variants = {
            json.dumps(e["input"], sort_keys=True, ensure_ascii=False) for e in entries
        }
        if len(variants) > 1:
            quarantined.extend(
                dict(e, reason="conflicting duplicate ID") for e in entries
            )
            continue
        entry = entries[0]
        group = entry["input"].get(recipe.get("group_field", key))
        if not isinstance(group, str) or not group:
            rejected.extend(
                dict(e, reason="nonempty string split group required") for e in entries
            )
            continue
        bucket = int(hashlib.sha256(f"{seed}\0{group}".encode()).hexdigest(), 16) % 100
        entry["split"] = (
            "train" if bucket < 80 else "development" if bucket < 90 else "test"
        )
        accepted.append(entry)
        duplicates.extend(
            dict(
                e,
                reason="identical duplicate",
                canonical_source_row=entry["source_row"],
            )
            for e in entries[1:]
        )
    result = dict(
        accepted=accepted,
        quarantined=quarantined,
        rejected=rejected,
        duplicates=duplicates,
    )
    result["counts"] = {k: len(v) for k, v in result.items()}
    assert sum(result["counts"].values()) == len(rows)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("recipe", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--seed", type=int, default=1729)
    args = parser.parse_args()
    result = prepare(load(args.input), json.loads(args.recipe.read_text()), args.seed)
    result["source_sha256"] = hashlib.sha256(args.input.read_bytes()).hexdigest()
    result["recipe"] = json.loads(args.recipe.read_text())
    result["seed"] = args.seed
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)


if __name__ == "__main__":
    main()
