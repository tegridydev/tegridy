import torch
from torch import nn
from quantization import convert, ternary, TernaryLinear


def test_float_equivalence_ties_and_no_architecture_change():
    model = nn.Sequential(nn.Linear(4, 4), nn.Linear(4, 4))
    model[1].weight = model[0].weight
    x = torch.randn(3, 4)
    clone = convert(model)
    assert clone[0].weight is clone[1].weight
    assert torch.equal(model(x), clone(x)) and clone[0].weight is not model[0].weight
    quantized = convert(model, True)
    assert quantized[0].weight is quantized[1].weight
    assert isinstance(quantized[0], TernaryLinear)


def test_zero_guard_ste_and_training():
    q, scale = ternary(torch.zeros(3, 4))
    assert q.count_nonzero() == 0 and scale == 0
    model = TernaryLinear(4, 2)
    x = torch.randn(16, 4)
    loss = model(x).square().mean()
    loss.backward()
    assert torch.isfinite(model.weight.grad).all() and model.weight.grad.abs().sum() > 0
    before = model.weight.detach().clone()
    torch.optim.SGD(model.parameters(), lr=0.01).step()
    assert not before.equal(model.weight)
