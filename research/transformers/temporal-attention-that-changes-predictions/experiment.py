"""Time-aware binary prediction on independently generated irregular episodes."""

from pathlib import Path
import io
import torch
from torch import nn
from torch.nn import functional as F


def reload_equal(model, clone, inputs):
    buffer = io.BytesIO()
    torch.save(model.state_dict(), buffer)
    buffer.seek(0)
    clone.load_state_dict(torch.load(buffer, weights_only=True))
    model.eval()
    clone.eval()
    with torch.no_grad():
        a, b = model(inputs), clone(inputs)
        if isinstance(a, tuple):
            a, b = a[0], b[0]
        return bool(torch.allclose(a, b, atol=1e-6))


import random, math


def episodes(seed, count, periodic=False, gaps=(1, 5, 20)):
    rng = random.Random(seed)
    features = []
    targets = []
    for _ in range(count):
        phase = rng.randrange(20)
        state = rng.randrange(2)
        time = 0
        observations = []
        for i in range(17):
            gap = rng.choice(gaps)
            for _ in range(gap):
                time += 1
                state = (
                    (time + phase) // 10 % 2
                    if periodic
                    else state ^ (rng.random() < 0.05)
                )
            if i < 16:
                observations.append((time, state ^ (rng.random() < 0.1)))
        features.append(
            [
                [value, (time - t) / 10, math.log1p((time - t) / 10)]
                for t, value in observations
            ]
        )
        targets.append(state)
    return torch.tensor(features, dtype=torch.float32), torch.tensor(
        targets, dtype=torch.float32
    )


class TemporalModel(nn.Module):
    def __init__(self, mode="learned"):
        super().__init__()
        self.mode = mode
        self.input = nn.Linear(3, 64)
        self.position = nn.Parameter(torch.zeros(16, 64))
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(64, 4, 128, dropout=0, batch_first=True),
            2,
            enable_nested_tensor=False,
        )
        self.keys = nn.Linear(64, 64)
        self.values = nn.Linear(64, 64)
        self.query = nn.Parameter(torch.randn(4, 16) * 0.1)
        self.raw_decay = (
            nn.Parameter(torch.full((4,), math.log(math.expm1(1.0))))
            if mode == "learned"
            else None
        )
        self.output = nn.Linear(64, 1)

    def forward(self, x):
        data = x.clone()
        if self.mode == "position":
            data[:, :, 1:] = 0
        h = self.encoder(self.input(data) + self.position)
        keys = self.keys(h).reshape(-1, 16, 4, 16).transpose(1, 2)
        values = self.values(h).reshape(-1, 16, 4, 16).transpose(1, 2)
        scores = (keys * self.query[None, :, None, :]).sum(-1) / 4
        if self.mode in ["fixed", "learned"]:
            decay = (
                F.softplus(self.raw_decay)
                if self.mode == "learned"
                else torch.ones(4, device=x.device)
            )
            scores = scores - decay[None, :, None] * x[:, None, :, 1]
        out = (scores.softmax(-1).unsqueeze(-1) * values).sum(-2).reshape(-1, 64)
        return self.output(out).squeeze(-1)


def run(seed, steps):
    result = {}
    for periodic in [False, True]:
        train = episodes(seed, 256, periodic)
        test = episodes(seed + 1, 128, periodic)
        shift = episodes(seed + 2, 128, periodic, gaps=(19, 37, 83))
        conditions = {}
        for mode in ["position", "features", "fixed", "learned"]:
            torch.manual_seed(seed)
            model = TemporalModel(mode)
            opt = torch.optim.Adam(model.parameters(), lr=0.001)
            for step in range(steps):
                idx = torch.arange(step * 32, step * 32 + 32) % 256
                opt.zero_grad()
                loss = F.binary_cross_entropy_with_logits(
                    model(train[0][idx]), train[1][idx]
                )
                loss.backward()
                opt.step()
            model.eval()
            with torch.no_grad():
                probabilities = model(test[0]).sigmoid()
                conditions[mode] = {
                    "accuracy": ((probabilities >= 0.5) == test[1])
                    .float()
                    .mean()
                    .item(),
                    "brier": ((probabilities - test[1]) ** 2).mean().item(),
                }
                shifted = model(shift[0]).sigmoid()
                conditions[mode]["shifted_accuracy"] = (
                    ((shifted >= 0.5) == shift[1]).float().mean().item()
                )
        conditions["last_observation"] = {
            "accuracy": (test[0][:, -1, 0] == test[1]).float().mean().item(),
            "shifted_accuracy": (shift[0][:, -1, 0] == shift[1]).float().mean().item(),
        }
        result["periodic" if periodic else "switching"] = conditions
    return {
        "conditions": result,
        "train_episodes": 256,
        "test_episodes": 128,
        "selection": "fixed steps; no final-data tuning",
    }


def main():
    import argparse, json, platform

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=40)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.steps < 1:
        parser.error("--steps must be positive")
    torch.set_num_threads(2)
    torch.manual_seed(args.seed)
    result = run(args.seed, args.steps)
    result.update(
        scope="CPU smoke experiment, not the article full benchmark",
        seed=args.seed,
        steps=args.steps,
        torch_version=torch.__version__,
        python=platform.python_version(),
    )
    import hashlib

    result["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
