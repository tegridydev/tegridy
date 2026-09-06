import pytest
import torch
from torch import nn
from capture import capture, straightness, fit_projection, project


def test_one_forward_repeated_tokens_zero_and_cleanup():
    model = nn.Sequential(nn.Embedding(10, 4), nn.Linear(4, 4, bias=False))
    model[1].weight.data.zero_()
    tokens = torch.tensor([[2, 3, 2]])
    result = capture(model, tokens, ["0", "1"], "fixture-v1", "integer-tokens-v1")
    assert (
        len(result["records"]) == 24
        and len({r["position"] for r in result["records"] if r["token_id"] == 2}) == 2
    )
    assert all(r["value"] == 0 for r in result["records"] if r["component"] == "1")
    assert not model[0]._forward_hooks and model.training
    with pytest.raises(ValueError):
        capture(model, tokens, ["0"], "v1", "t1", max_values=1)
    assert not model[0]._forward_hooks


def test_path_zero_and_shared_basis():
    assert straightness([[0, 0], [0, 0]]) is None
    assert straightness([[0, 0], [1, 0], [2, 0]]) == 1
    x = torch.tensor([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]])
    projection = fit_projection(x, 1)
    assert project(x, projection).shape == (3, 1)
