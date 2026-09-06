import numpy as np
import pytest
from compress import factorize, report


def test_exact_low_rank_and_break_even():
    rng = np.random.default_rng(17)
    w = rng.normal(size=(64, 8)) @ rng.normal(size=(8, 64))
    x = rng.normal(size=(12, 64))
    result = report(w, x, x + 1, 8)
    assert result["held_out"]["mse"] < 1e-20 and result["reload_equal"]
    assert result["factor_parameters"] == 1024
    assert report(w, x, x, 32)["factor_parameters"] == w.size


def test_functional_error_depends_on_inputs():
    w = np.diag([10.0, 1.0])
    r = report(w, np.array([[1.0, 0.0]]), np.array([[0.0, 100.0]]), 1)
    assert r["calibration"]["mse"] == 0 and r["held_out"]["mse"] == 5000
    with pytest.raises(ValueError):
        factorize(w, 0)
