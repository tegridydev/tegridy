import math
from grammar import counts, generate, legal_sequences, likelihood, compare


def test_order_counts_validity_and_budget():
    sequence = ("A", "C", "E", "END")
    tally = counts([sequence, sequence])
    assert (
        tally["START", "A"] == 2 and tally["C", "E"] == 2 and tally["A", "START"] == 0
    )
    legal = set(legal_sequences())
    assert len(legal) == 4
    for row in compare():
        assert row["tokens"] == 2000 and sum(row["sequence_counts"].values()) == 500
    assert set(generate(17, 2)) <= legal
    assert math.isfinite(likelihood([], legal))
