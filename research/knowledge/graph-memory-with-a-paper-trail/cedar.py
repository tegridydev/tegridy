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


def retrieve(sources,edges,query,filters=None,budget=100,initial_limit=3,max_hops=2):
    """Budgeted lexical candidates plus reviewed graph expansion.

    Applicability is checked for every graph target, not just initial candidates.
    Edges are supplied judgements; this function does not certify their truth.
    """
    import re
    if any(type(v) is not int or v<0 for v in [budget,initial_limit,max_hops]):raise ValueError('nonnegative integer limits required')
    filters=filters or {};terms=set(re.findall(r'\w+',query.casefold()))
    eligible={k:v for k,v in sources.items() if all(v.get(field)==value for field,value in filters.items())}
    for edge in edges:
        if edge['source'] not in sources or edge['target'] not in sources:raise ValueError('edge references missing source')
        if edge.get('reviewed') and not edge.get('reason'):raise ValueError('reviewed edge requires reason')
    scores={k:len(terms&set(re.findall(r'\w+',v['text'].casefold()))) for k,v in eligible.items()}
    initial=sorted((k for k in eligible if scores[k]>0),key=lambda k:(-scores[k],k))[:initial_limit]
    queue=[(k,0,'lexical') for k in initial];seen=set();selected=[];trace=[];used=0
    while queue:
        identity,depth,reason=queue.pop(0)
        if identity in seen:continue
        seen.add(identity)
        if identity not in eligible:
            trace.append(dict(id=identity,reason='inapplicable'));continue
        cost=len(eligible[identity]['text'].split())
        if used+cost>budget:
            trace.append(dict(id=identity,reason='budget'));continue
        selected.append(identity);used+=cost;trace.append(dict(id=identity,reason=reason,depth=depth,cost=cost))
        if depth<max_hops:
            queue.extend((edge['target'],depth+1,'reviewed-edge') for edge in edges if edge['source']==identity and edge.get('reviewed'))
    return dict(selected=selected,trace=trace,words=used,initial=initial)
