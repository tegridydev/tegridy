from experiment import *


def test_generator_and_gradient():
    a, y = episodes(17, 8)
    b, z = episodes(17, 8)
    assert a.equal(b) and y.equal(z)
    assert (a[:, :, 1] > 0).all()
    assert set(y.tolist()) <= {0.0, 1.0}
    model = TemporalModel()
    loss = F.binary_cross_entropy_with_logits(model(a), y)
    loss.backward()
    assert model.raw_decay.grad is not None
    assert reload_equal(model, TemporalModel(), a)
