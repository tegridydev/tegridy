from experiment import *


def test_mask_and_gate():
    model = JudgeAttention().eval()
    a = torch.randn(2, 5, 64)
    b = a.clone()
    b[:, 3:] += 100
    assert torch.allclose(model(a)[:, :3], model(b)[:, :3], atol=1e-6)
    loss = model(a).square().mean()
    loss.backward()
    assert model.gate.weight.grad.abs().sum() > 0


def test_oracle():
    x, y = data(17, 32)
    for row, target in zip(x, y):
        lookup = {int(row[0]): int(row[1]) - 32, int(row[4]): int(row[5]) - 32}
        assert lookup[int(row[-1])] == int(target)
