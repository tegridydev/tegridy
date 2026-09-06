from perspectives import cases


def test_constraints_precede_weights_and_distinct_sensitivity():
    report = cases()
    assert len(report["cases"]) == 40
    first = report["cases"][0]
    assert first["perspectives"]["speed-first"]["winners"] == ["fast"]
    assert first["perspectives"]["cost-first"]["winners"] == ["cheap"]
    assert first["factual_budget_shift"]["winners"] == ["cheap"]
    assert first["perspectives"]["speed-first"]["pareto"] == ["fast", "cheap"]
    assert report["cases"][-1]["perspectives"]["speed-first"]["winners"] == ["cheap"]


def test_nan_cannot_bypass_hard_constraints_and_ids_are_unique():
    import pytest
    from perspectives import evaluate
    action = dict(id='a', scores={'speed': 1.0}, facts={'spend': float('nan')})
    with pytest.raises(ValueError):
        evaluate([action], {'speed': 1.0}, {'spend': 100})
    action['facts']['spend'] = 1
    with pytest.raises(ValueError):
        evaluate([action], {'speed': 1.0}, {'spend': float('nan')})
    with pytest.raises(ValueError):
        evaluate([action, action], {'speed': 1.0}, {'spend': 100})
