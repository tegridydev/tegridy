import numpy as np
import torch
from signal_experiment import generate, SequenceModel, statistical


def test_energy_nuisance_pairing_and_session_splits():
    x, y, meta = generate()
    assert x.shape == (3000, 2, 256) and y.sum() == 1500
    for a, b in zip(meta[::2], meta[1::2]):
        assert (
            a["snr"] == b["snr"]
            and a["offset"] == b["offset"]
            and a["split"] == b["split"]
        )
        assert abs(a["clean_energy"] - 1) < 1e-12 and abs(b["clean_energy"] - 1) < 1e-12
    groups = {
        s: {r["session"] for r in meta if r["split"] == s}
        for s in ["train", "development", "test"]
    }
    assert not groups["train"] & groups["test"] and len(groups["development"]) == 5
    assert np.isfinite(statistical(x)).all()


def test_classifier_gradient_and_shift():
    x, y, meta = generate(17, True, sessions=1, pairs=2)
    assert all(0.02 <= abs(r["offset"]) <= 0.04 for r in meta)
    model = SequenceModel()
    loss = model(torch.tensor(x)).square().mean()
    loss.backward()
    assert model.net[0].weight.grad.abs().sum() > 0
