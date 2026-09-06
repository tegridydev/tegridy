import itertools, random, math
import pytest
from tree import Tree, child_code, summary, inside


def test_codes_and_partial_leaf():
    points = [
        tuple(p) + (float(i),)
        for i, p in enumerate(itertools.product([0.25, 0.75], repeat=4))
    ]
    assert {child_code(p[:4], [0.5] * 4) for p in points} == set(range(16))
    tree = Tree([(0.2, 0.2, 0.2, 0.2, 2.0), (0.8, 0.2, 0.2, 0.2, 10.0)], capacity=16)
    assert tree.query(((0.0, 0.5), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0))).mean == 2
    assert Tree([]).query(((0.0, 1.0),) * 4).mean is None
    with pytest.raises(ValueError):
        Tree([(1.0, 0.0, 0.0, 0.0, 2.0)])


def test_random_scan_oracle_and_depths():
    rng = random.Random(17)
    points = [tuple(rng.random() for _ in range(5)) for _ in range(300)]
    for depth in [0, 1, 3]:
        tree = Tree(points, capacity=4, max_depth=depth)
        for _ in range(50):
            bounds = tuple(
                tuple(sorted([rng.random(), rng.random()])) for _ in range(4)
            )
            a = tree.query(bounds)
            b = summary(p for p in points if inside(p[:4], bounds))
            assert a.count == b.count and math.isclose(a.total, b.total, abs_tol=1e-10)
    assert Tree([(0.5, 0.5, 0.5, 0.5, 1.0)] * 100).aggregate.count == 100
