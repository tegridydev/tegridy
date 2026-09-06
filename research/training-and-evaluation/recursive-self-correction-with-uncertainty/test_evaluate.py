import pytest
from evaluate import evaluate


def case(i, group, before, after, confidence):
    return dict(
        id=i,
        group=group,
        before=before,
        after=after,
        confidence=confidence,
        rounds=1,
        cost=2,
        action="critique",
    )


def test_frozen_selection_damage_and_evidence():
    dev = [case("d1", "d", False, True, 0.9), case("d2", "d", True, False, 0.2)]
    final = [case("t1", "t", False, True, 0.8), case("t2", "t", True, False, 0.9)]
    result = evaluate(dev, final)
    assert (
        result["threshold"] == 0.21
        and result["repaired"] == result["damaged"] == 1
        and result["selective"]["risk"] == 0.5
    )
    with pytest.raises(ValueError):
        evaluate(dev, [dict(final[0], group="d")])
    with pytest.raises(ValueError):
        evaluate(dev, [dict(final[0], action="retrieval")])
