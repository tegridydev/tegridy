from adaptive_tree import AdaptiveTree


def test_refinement_changes_storage_not_exact_partial_result():
    points = [(0.2, 0.2, 0.2, 0.2, 2.0), (0.8, 0.2, 0.2, 0.2, 10.0)]
    query = ((0.0, 0.5), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0))
    coarse = AdaptiveTree(points, capacity=1, variance_threshold=100)
    refined = AdaptiveTree(points, capacity=1, variance_threshold=0)
    assert not coarse.children and refined.children
    assert coarse.query(query) == refined.query(query) and coarse.query(query).mean == 2
    shifted = ((0.5, 1.0), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0))
    assert coarse.query(shifted).mean == refined.query(shifted).mean == 10


def test_large_finite_variation_does_not_overflow_square():
    tree=AdaptiveTree([(0.1,)*4+(1e200,),(.9,)*4+(-1e200,)],capacity=1,variance_threshold=1e200)
    assert tree.query(((0.,.5),)*4).count==1
