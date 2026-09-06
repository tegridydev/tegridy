"""Offline paginated message ingestion with edit history and partial-run receipts."""

import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime


def time_key(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps require explicit timezone")
    return parsed.timestamp()


def collect(pages):
    messages = {}
    errors = []
    complete = False
    seen_cursors = set()
    expected = None
    consumed = 0
    for number, page in enumerate(pages):
        if complete:
            errors.append(dict(page=number, reason="page after terminal marker"))
            complete = False
            break
        if not isinstance(page, dict) or not isinstance(page.get("messages"), list):
            errors.append(dict(page=number, reason="malformed page"))
            break
        cursor = page.get("cursor")
        if cursor is not None and not isinstance(cursor, str):
            errors.append(dict(page=number, reason="cursor must be a string or null"))
            break
        if cursor != expected or cursor in seen_cursors:
            errors.append(dict(page=number, reason="cursor gap or loop"))
            break
        seen_cursors.add(cursor)
        consumed += 1
        for position, row in enumerate(page["messages"]):
            try:
                if (
                    not isinstance(row, dict)
                    or any(
                        not isinstance(row.get(k), str)
                        for k in [
                            "id",
                            "author_id",
                            "channel_id",
                            "timestamp",
                            "content",
                        ]
                    )
                    or not all(row[k] for k in ["id", "author_id", "channel_id"])
                ):
                    raise ValueError("required string field absent")
                time_key(row["timestamp"])
                revision = time_key(row.get("edited_timestamp") or row["timestamp"])
                if revision < time_key(row["timestamp"]):
                    raise ValueError("edit precedes creation")
                identity = (row["channel_id"], row["id"])
                entry = messages.setdefault(identity, dict(current=row, revisions=[]))
                if any(
                    entry["current"][k] != row[k] for k in ["author_id", "timestamp"]
                ):
                    raise ValueError("identity fields changed")
                matching = [
                    old
                    for old in entry["revisions"]
                    if time_key(old.get("edited_timestamp") or old["timestamp"])
                    == revision
                ]
                if matching and matching[0] != row:
                    raise ValueError("conflicting content at identical revision")
                if row not in entry["revisions"]:
                    entry["revisions"].append(row)
                oldtime = time_key(
                    entry["current"].get("edited_timestamp")
                    or entry["current"]["timestamp"]
                )
                if revision > oldtime:
                    entry["current"] = row
            except (ValueError, TypeError) as error:
                errors.append(dict(page=number, position=position, reason=str(error)))
        expected = page.get("next_cursor")
        if expected is not None and not isinstance(expected, str):
            errors.append(dict(page=number, reason="next_cursor must be a string or null"))
            break
        complete = expected is None
    records = sorted(
        messages.values(),
        key=lambda m: (
            time_key(m["current"]["timestamp"]),
            m["current"]["channel_id"],
            m["current"]["id"],
        ),
    )
    return dict(
        status="complete" if complete and not errors else "partial",
        pages_consumed=consumed,
        next_cursor=expected,
        messages=records,
        errors=errors,
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pages", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    result = collect(json.loads(a.pages.read_text()))
    result["source_sha256"] = hashlib.sha256(a.pages.read_bytes()).hexdigest()
    with a.output.open("x") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
