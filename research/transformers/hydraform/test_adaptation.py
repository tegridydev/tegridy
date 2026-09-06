import io
import pytest
import torch
from adaptation import AdaptiveAttention


def test_mutation_coverage_gradient_roundtrip():
    model = AdaptiveAttention()
    x = torch.randn(2, 5, 64)
    for width in [20, 12]:
        opt, event = model.mutate(0, width, 20000)
        assert {id(p) for g in opt.param_groups for p in g["params"]} == {
            id(p) for p in model.parameters()
        }
        before = model.heads[0].q.weight.detach().clone()
        opt.zero_grad()
        model(x).square().mean().backward()
        opt.step()
        assert not before.equal(model.heads[0].q.weight)
        buffer = io.BytesIO()
        torch.save(model.checkpoint(), buffer)
        buffer.seek(0)
        clone = AdaptiveAttention.restore(torch.load(buffer, weights_only=True))
        assert torch.allclose(model(x), clone(x))
    with pytest.raises(ValueError):
        model.mutate(0, 100, 20000)


def test_padding_and_empty_context():
    model = AdaptiveAttention()
    x = torch.randn(2, 5, 64)
    changed = x.clone()
    changed[:, 3:] += 100
    mask = torch.tensor([[False, False, False, True, True]] * 2)
    assert torch.allclose(model(x, mask)[:, :3], model(changed, mask)[:, :3], atol=1e-6)
    assert model(x, torch.ones(2, 5, dtype=torch.bool)).count_nonzero() == 0
