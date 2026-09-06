from evidence import fixture, Passage


def test_two_revisions_and_old_version_retained():
    study = fixture()
    data = study.export()
    assert len(data["answers"]) == 3 and len(data["sources"]) == 2
    first = Passage(**data["answers"][0]["claims"][0]["citations"][0])
    assert study.check(first) == "historical-version"
    assert data["answers"][0]["claims"][0]["citation_status"] == ["current"]
    assert data["answers"][2]["claims"][0]["citation_status"] == [
        "historical-version",
        "current",
    ]


def test_forged_empty_and_out_of_bounds_passages_are_rejected():
    study = fixture()
    version = study.latest['manual']
    for start, end, text in [(100, 101, ''), (0, 0, ''), (-1, 34, '.')]:
        assert study.check(Passage('manual', version, start, end, text)) == 'span-mismatch'
