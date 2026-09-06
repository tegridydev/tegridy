from experiment import *


def test_dimensions_and_parameters():
    assert sum(p.numel() for p in FaceMixer().parameters()) == 4420
    assert FaceMixer()(torch.randn(3, 64)).shape == (3, 64)
    x, y = dataset()[0]
    assert x.shape == (3072, 8)
    assert y.min() >= 0 and y.max() < 32


def test_gradient_and_reload():
    model = Model()
    x, y = dataset()[0]
    loss = F.cross_entropy(model(x[:4]), y[:4])
    loss.backward()
    assert model.adapter.gates[0].weight.grad.abs().sum() > 0
    assert reload_equal(model, Model(), x[:4])
