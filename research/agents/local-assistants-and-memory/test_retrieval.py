from retrieval import histories, Memory, Item


def test_correction_historical_owner_and_recording_time():
    data = histories()
    assert len(data) == 30 and sum(h["split"] == "development" for h in data) == 10
    for history in data:
        assert history["current"]["selected"] == ["new"]
        assert (
            history["historical"]["selected"]
            == history["known_then"]["selected"]
            == ["old"]
        )
        assert (
            next(r for r in history["current"]["candidates"] if r["id"] == "other")[
                "reason"
            ]
            == "other-owner"
        )


def test_exact_budget_and_no_overlap():
    memory = Memory([Item("a", "owner", "key", "two words", "event", 0, 0)])
    assert not memory.retrieve("owner", "words", 1, 1, budget=1)["selected"]
    assert not memory.retrieve("owner", "different", 1, 1)["selected"]
