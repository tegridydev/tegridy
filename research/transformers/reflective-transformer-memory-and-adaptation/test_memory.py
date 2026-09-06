import io
import pytest
import torch
from memory import Memory


def test_empty_delayed_isolated_and_reload():
    model = Memory(2)
    q = torch.ones(2, 4, 16, requires_grad=True)
    assert model(q, 0).equal(torch.zeros_like(q))
    values = torch.stack([torch.ones(4, 16), torch.full((4, 16), 7.0)])
    model.write(q, values, 0)
    assert model(q, 0).equal(torch.zeros_like(q))
    answer = model(q, 1)
    assert torch.allclose(answer[0], torch.full((4, 16), 0.5))
    assert torch.allclose(answer[1], torch.full((4, 16), 3.5))
    answer.sum().backward()
    assert model.gate.grad.abs().sum() > 0
    assert not model.values.requires_grad
    b = io.BytesIO()
    torch.save(model.state_dict(), b)
    b.seek(0)
    clone = Memory(2)
    clone.load_state_dict(torch.load(b, weights_only=True))
    assert clone(q, 1).equal(model(q, 1))
    model.reset(0)
    assert model(q, 1)[0].count_nonzero() == 0 and model(q, 1)[1].count_nonzero() > 0
    with pytest.raises(ValueError):
        model.write(q, values, 0)


def test_capacity_and_fifo():
    for total in [32, 128]:
        model = Memory(total_capacity=total)
        q = torch.ones(1, 4, 16)
        for step in range(total // 4 + 1):
            model.write(q, q * step, step)
        assert model.created.numel() == total and model.created.min() == 1


def test_invalid_dimensions_and_fractional_steps_are_rejected():
    import pytest
    for kwargs in [{'heads': 0}, {'width': 0}, {'batch_size': 0}, {'total_capacity': 1.5}]:
        with pytest.raises(ValueError):
            Memory(**kwargs)
    memory = Memory(batch_size=1, heads=1, width=2, total_capacity=2)
    values = torch.ones(1, 1, 2)
    with pytest.raises(ValueError):
        memory.write(values, values, 0.5)
    with pytest.raises(ValueError):
        memory(values, float('nan'))
