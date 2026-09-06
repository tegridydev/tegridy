import numpy as np
import torch
from recovery import evaluate, SAE


def test_permutation_duplicates_and_dead_features():
    dictionary = np.eye(4)
    result = evaluate(dictionary, dictionary[:, [2, 0, 3, 1]])
    assert (
        result["signed_cosines"] == [1.0] * 4
        and len(set(result["matched_learned"])) == 4
    )
    duplicated = np.column_stack([dictionary, dictionary[:, 0]])
    assert not evaluate(duplicated, duplicated)["identifiable"]
    assert evaluate(dictionary, np.zeros((4, 4)))["dead_learned"] == [0, 1, 2, 3]


def test_normalization_and_learning_gradient():
    model = SAE()
    reconstruction, codes = model(torch.randn(8, 30))
    reconstruction.square().mean().backward()
    assert model.encoder.weight.grad.abs().sum() > 0
    torch.optim.Adam(model.parameters()).step()
    model.normalize()
    assert torch.allclose(model.decoder.weight.norm(dim=0), torch.ones(100), atol=1e-6)
