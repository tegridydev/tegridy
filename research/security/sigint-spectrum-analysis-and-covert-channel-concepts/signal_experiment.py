"""Synthetic envelope detection with paired nuisances and whole-session splits."""

import argparse
import json
import numpy as np
from scipy.stats import rankdata
import torch
from torch import nn
from torch.nn import functional as F


def generate(seed=17, shifted=False, sessions=30, pairs=50):
    samples = []
    labels = []
    metadata = []
    n = np.arange(256)
    for session in range(sessions):
        rng = np.random.default_rng(
            np.random.SeedSequence([seed, session, int(shifted)])
        )
        offset = (
            rng.choice([-1.0, 1.0]) * rng.uniform(0.02, 0.04)
            if shifted
            else rng.uniform(-0.01, 0.01)
        )
        for pair in range(pairs):
            phase = rng.uniform(0, 2 * np.pi)
            snr = int(rng.choice([10, 20, 30]))
            base = np.exp(1j * (2 * np.pi * (0.08 + offset) * n + phase))
            for label in [0, 1]:
                clean = base * (1 + 0.25 * np.sin(2 * np.pi * n / 32) if label else 1)
                clean = clean / np.sqrt(np.mean(np.abs(clean) ** 2))
                noise = (rng.normal(size=256) + 1j * rng.normal(size=256)) * np.sqrt(
                    10 ** (-snr / 10) / 2
                )
                signal = clean + noise
                samples.append(np.stack([signal.real, signal.imag]))
                labels.append(label)
                metadata.append(
                    dict(
                        session=session,
                        pair=pair,
                        label=label,
                        snr=snr,
                        offset=float(offset),
                        clean_energy=float(np.mean(np.abs(clean) ** 2)),
                        split="shift"
                        if shifted
                        else "train"
                        if session < 20
                        else "development"
                        if session < 25
                        else "test",
                    )
                )
    return (
        np.asarray(samples, dtype=np.float32),
        np.asarray(labels, dtype=np.float32),
        metadata,
    )


def statistical(x):
    amplitude = np.sqrt((x * x).sum(1))
    power = amplitude**2
    return np.stack(
        [
            power.mean(1),
            power.std(1),
            amplitude.std(1),
            np.mean((amplitude[:, 1:] - amplitude[:, :-1]) ** 2, axis=1),
        ],
        1,
    )


class SequenceModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(2, 16, 9, padding=4),
            nn.ReLU(),
            nn.Conv1d(16, 16, 9, padding=4),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(16, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def metrics(probabilities, labels, threshold, metadata):
    positive = labels == 1
    negative = ~positive
    auc = (
        rankdata(probabilities)[positive].sum()
        - positive.sum() * (positive.sum() + 1) / 2
    ) / (positive.sum() * negative.sum())
    per_session = []
    for session in sorted({r["session"] for r in metadata}):
        mask = np.array([r["session"] == session for r in metadata])
        per_session.append(
            dict(
                session=session,
                detection=float((probabilities[mask & positive] >= threshold).mean()),
                false_alarm=float((probabilities[mask & negative] >= threshold).mean()),
            )
        )
    rng = np.random.default_rng(91)
    values = np.array([r["detection"] for r in per_session])
    boot = values[rng.integers(len(values), size=(1000, len(values)))].mean(1)
    return dict(
        auroc=float(auc),
        detection=float((probabilities[positive] >= threshold).mean()),
        false_alarm=float((probabilities[negative] >= threshold).mean()),
        brier=float(np.mean((probabilities - labels) ** 2)),
        session_detection_interval=np.quantile(boot, [0.025, 0.975]).tolist(),
        sessions=per_session,
    )


def run(seed=17, steps=100, output=None):
    x, y, meta = generate(seed)
    shift_x, shift_y, shift_meta = generate(seed, True, sessions=5)
    splits = {
        name: np.array([r["split"] == name for r in meta])
        for name in ["train", "development", "test"]
    }
    results = {}
    for condition in ["statistics", "sequence"]:
        torch.manual_seed(seed)
        if condition == "statistics":
            data = statistical(x)
            shift = statistical(shift_x)
            mean = data[splits["train"]].mean(0)
            std = data[splits["train"]].std(0).clip(1e-6)
            data = (data - mean) / std
            shift = (shift - mean) / std
            model = nn.Sequential(nn.Linear(4, 1), nn.Flatten(0))
        else:
            data = x
            shift = shift_x
            model = SequenceModel()
        data = torch.tensor(data, dtype=torch.float32)
        shift = torch.tensor(shift, dtype=torch.float32)
        labels = torch.tensor(y)
        indices = np.flatnonzero(splits["train"])
        optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
        for step in range(steps):
            idx = indices[np.arange(step * 64, step * 64 + 64) % len(indices)]
            optimizer.zero_grad()
            loss = F.binary_cross_entropy_with_logits(model(data[idx]), labels[idx])
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            prob = model(data).sigmoid().numpy()
            shift_prob = model(shift).sigmoid().numpy()
        dev = splits["development"]
        dev_neg = dev & (y == 0)
        dev_pos = dev & (y == 1)
        candidates = [
            float(t)
            for t in np.unique(np.r_[prob[dev], np.nextafter(1.0, 2.0)])
            if (prob[dev_neg] >= t).mean() <= 0.05
        ]
        threshold = max(candidates, key=lambda t: ((prob[dev_pos] >= t).mean(), -t))
        if output is not None:
            from pathlib import Path
            destination = Path(output)
            np.savez_compressed(destination / (condition + '-predictions.npz'), probabilities=prob, labels=y, shift_probabilities=shift_prob, shift_labels=shift_y, threshold=threshold)
            torch.save(model.state_dict(), destination / (condition + '.pt'))
            (destination / 'sessions.json').write_text(json.dumps(dict(original=meta, shifted=shift_meta), indent=2) + '\n')
        test = splits["test"]
        results[condition] = dict(
            threshold=threshold,
            final=metrics(
                prob[test],
                y[test],
                threshold,
                [r for r, keep in zip(meta, test) if keep],
            ),
            shifted=metrics(shift_prob, shift_y, threshold, shift_meta),
        )
    return dict(
        seed=seed,
        steps=steps,
        sequences=len(x),
        sessions=dict(train=20, development=5, test=5, shifted=5),
        conditions=results,
        scope="one-seed synthetic pilot; bootstrap resamples five final sessions, not real RF recordings",
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=17)
    p.add_argument("--steps", type=int, default=100)
    a = p.parse_args()
    if a.steps < 1:
        p.error("steps must be positive")
    torch.set_num_threads(2)
    print(json.dumps(run(a.seed, a.steps), indent=2, allow_nan=False))
