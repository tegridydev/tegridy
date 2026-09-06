from experiment import *


def test_causality():
    model = ByteModel(32, 1).eval()
    a = torch.tensor([[1, 2, 3, 4]])
    b = torch.tensor([[1, 2, 9, 8]])
    with torch.no_grad():
        assert torch.allclose(model(a)[:, :2], model(b)[:, :2], atol=1e-6)


def test_training_and_roundtrip():
    model = ByteModel(32, 1)
    x, y = windows([b"abcdef" * 8], 8)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    first = F.cross_entropy(model(x).transpose(1, 2), y).item()
    for _ in range(10):
        optimizer.zero_grad()
        loss = F.cross_entropy(model(x).transpose(1, 2), y)
        loss.backward()
        optimizer.step()
    assert loss.item() < first
    assert reload_equal(model, ByteModel(32, 1), x)
