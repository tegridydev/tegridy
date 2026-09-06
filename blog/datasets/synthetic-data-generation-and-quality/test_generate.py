from generate import generate, verify


def test_verification_counterfactual_and_split():
    records = generate(300)
    assert records == generate(300)
    assert all(r["verification"]["valid"] for r in records)
    states = {}
    parents = {}
    for r in records:
        states.setdefault(tuple(r["state"]), set()).add(r["split"])
        parents.setdefault(r["parent_id"], set()).add(r["split"])
    assert all(len(v) == 1 for v in list(states.values()) + list(parents.values()))
    bad = dict(records[0], answer=records[0]["answer"] + 1)
    assert not verify(bad)["valid"]
    assert not verify(dict(records[0], question="A polished unsupported question"))[
        "valid"
    ]
