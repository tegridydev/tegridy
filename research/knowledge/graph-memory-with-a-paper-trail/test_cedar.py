from cedar import fixture, select


def test_five_applicability_cases_and_equal_metadata():
    data = fixture()
    assert [p["id"] for p in data["new"]["selected"]] == ["r2"]
    assert [p["id"] for p in data["upgraded"]["selected"]] == ["migration"]
    assert [p["id"] for p in data["historical"]["selected"]] == ["r1"]
    assert (
        data["unspecified"]["status"] == "needs-scope"
        and data["unsupported"]["status"] == "unsupported"
    )
    assert select(graph=True)["selected"] == select(graph=False)["selected"]
    assert not select(budget=0)["selected"]
