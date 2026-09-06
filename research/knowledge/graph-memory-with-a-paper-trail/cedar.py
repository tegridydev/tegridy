"""Cedar applicability fixture with bounded, reviewed graph traversal."""

import json

SOURCES = {
    "r1": dict(
        text="Cedar release 1 defaults to a 30-second request timeout.",
        release="1",
        deployment="new",
    ),
    "r2": dict(
        text="New Cedar release 2 deployments default to a 10-second request timeout.",
        release="2",
        deployment="new",
    ),
    "migration": dict(
        text="Cedar release 2 upgrades retain the previously configured timeout.",
        release="2",
        deployment="upgraded",
    ),
}
EDGES = [
    dict(
        source="r2",
        target="migration",
        kind="qualified_by",
        reviewed=True,
        reason="Different deployment conditions require separate answers.",
    )
]


def select(release=None, deployment=None, graph=True, budget=100):
    if budget < 0:
        raise ValueError("nonnegative word budget required")
    candidates = []
    excluded = []
    for identity, record in SOURCES.items():
        reason = (
            "release"
            if release is not None and record["release"] != release
            else "deployment"
            if deployment is not None and record["deployment"] != deployment
            else None
        )
        if reason:
            excluded.append(dict(id=identity, reason=reason))
        else:
            candidates.append(identity)
    selected = []
    trace = []
    visited = set()
    queue = [(identity, 0) for identity in candidates]
    used = 0
    while queue and len(visited) < 40:
        identity, depth = queue.pop(0)
        if identity in visited:
            continue
        visited.add(identity)
        if identity not in candidates:
            continue
        record = SOURCES[identity]
        cost = len(record["text"].split())
        if used + cost <= budget:
            selected.append(dict(id=identity, **record))
            used += cost
        else:
            excluded.append(dict(id=identity, reason="budget"))
        if graph and depth < 2:
            for edge in EDGES:
                if edge["source"] == identity and edge["reviewed"]:
                    trace.append(edge)
                    queue.append((edge["target"], depth + 1))
    return dict(
        status="unsupported"
        if not candidates
        else "needs-scope"
        if len(candidates) > 1
        else "scoped",
        selected=selected,
        excluded=excluded,
        traversed=trace,
        words=used,
    )


def fixture():
    return {
        name: select(**query)
        for name, query in [
            ("new", dict(release="2", deployment="new")),
            ("upgraded", dict(release="2", deployment="upgraded")),
            ("historical", dict(release="1", deployment="new")),
            ("unspecified", {}),
            ("unsupported", dict(release="3")),
        ]
    }


if __name__ == "__main__":
    print(json.dumps(fixture(), indent=2))
