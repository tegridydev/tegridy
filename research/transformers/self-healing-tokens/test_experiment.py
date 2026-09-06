from experiment import *


def test_data_and_loss():
    clean, noisy, mask = records(17, 32)
    assert (noisy[:, POSITIONS] != clean[:, POSITIONS]).equal(mask)
    assert len({tuple(row.tolist()) for row in clean}) == 32
    model = Denoiser()
    r, d = model(noisy)
    loss = F.cross_entropy(
        r.transpose(1, 2), clean[:, POSITIONS]
    ) + F.binary_cross_entropy_with_logits(d, mask.float())
    loss.backward()
    assert model.detect.weight.grad is not None
    assert output(model, noisy, 1.1).equal(noisy[:, POSITIONS])
