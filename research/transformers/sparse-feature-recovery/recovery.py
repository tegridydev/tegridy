"""Synthetic sparse dictionary learning with one-to-one signed recovery scoring."""

import argparse
import json
import numpy as np
from scipy.optimize import linear_sum_assignment
import torch
from torch import nn
from torch.nn import functional as F


def evaluate(true, learned):
    true = np.asarray(true, dtype=float)
    learned = np.asarray(learned, dtype=float)
    if (
        true.ndim != 2
        or learned.ndim != 2
        or true.shape[0] != learned.shape[0]
        or not np.isfinite(true).all()
        or not np.isfinite(learned).all()
    ):
        raise ValueError("finite compatible dictionaries required")
    true_norm = np.linalg.norm(true, axis=0)
    learned_norm = np.linalg.norm(learned, axis=0)
    if np.any(true_norm == 0):
        raise ValueError("true dictionary contains zero feature")
    a = true / true_norm
    b = np.divide(
        learned, learned_norm, where=learned_norm > 0, out=np.zeros_like(learned)
    )
    similarity = a.T @ b
    rows, columns = linear_sum_assignment(-similarity)
    gram = a.T @ a
    np.fill_diagonal(gram, -np.inf)
    duplicate_pairs = np.argwhere(np.triu(gram > 0.999999, 1)).tolist()
    return dict(
        matched_true=rows.tolist(),
        matched_learned=columns.tolist(),
        signed_cosines=similarity[rows, columns].tolist(),
        dead_learned=np.flatnonzero(learned_norm == 0).tolist(),
        duplicate_true_pairs=duplicate_pairs,
        identifiable=not bool(duplicate_pairs),
    )


class SAE(nn.Module):
    def __init__(self, dimension=30, features=100):
        super().__init__()
        self.encoder = nn.Linear(dimension, features)
        self.decoder = nn.Linear(features, dimension, bias=False)
        self.normalize()

    def normalize(self):
        with torch.no_grad():
            self.decoder.weight.div_(
                self.decoder.weight.norm(dim=0, keepdim=True).clamp_min(1e-12)
            )

    def forward(self, x):
        codes = F.relu(self.encoder(x))
        return self.decoder(codes), codes


def run(seed=17, steps=100):
    torch.manual_seed(seed)
    dictionary = torch.randn(30, 100)
    dictionary /= dictionary.norm(dim=0)
    code = (torch.rand(1024, 100) < 0.05) * (torch.rand(1024, 100) + 0.5)
    x = code @ dictionary.T
    model = SAE()
    opt = torch.optim.Adam(model.parameters(), lr=0.001)
    for step in range(steps):
        idx = torch.arange(step * 64, step * 64 + 64) % 768
        opt.zero_grad()
        reconstruction, activation = model(x[idx])
        loss = F.mse_loss(reconstruction, x[idx]) + 0.01 * activation.mean()
        loss.backward()
        opt.step()
        model.normalize()
    with torch.no_grad():
        prediction, activation = model(x[768:])
        mse = F.mse_loss(prediction, x[768:]).item()
    result = evaluate(dictionary.numpy(), model.decoder.weight.detach().numpy())
    result.update(
        seed=seed,
        steps=steps,
        held_out_mse=mse,
        scope="1024 synthetic rows, 768 train/256 held out; no correlated-feature study",
    )
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=17)
    p.add_argument("--steps", type=int, default=100)
    a = p.parse_args()
    if a.steps < 1:
        p.error("steps must be positive")
    torch.set_num_threads(2)
    print(json.dumps(run(a.seed, a.steps), indent=2))
