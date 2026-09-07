"""Causal key/value recall with post-computation head gating and controls."""

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


class JudgeAttention(nn.Module):
    def __init__(self, mode="judge"):
        super().__init__()
        self.mode = mode
        self.qkv = nn.Linear(64, 192)
        self.out = nn.Linear(64, 64)
        self.gate = (
            nn.Linear(16, 3)
            if mode == "judge"
            else nn.Linear(64, 3)
            if mode == "token"
            else None
        )
        self.static = nn.Parameter(torch.zeros(3)) if mode == "static" else None

    def forward(self, x):
        b, t, _ = x.shape
        q, k, v = self.qkv(x).reshape(b, t, 3, 4, 16).permute(2, 0, 3, 1, 4)
        scores = q @ k.transpose(-1, -2) / 4
        scores = scores.masked_fill(
            torch.triu(torch.ones(t, t, device=x.device, dtype=torch.bool), 1),
            float("-inf"),
        )
        workers = (scores.softmax(-1) @ v).transpose(1, 2)
        gates = (
            self.gate(workers[:, :, 3])
            if self.mode == "judge"
            else self.gate(x)
            if self.mode == "token"
            else self.static.expand(b, t, 3)
            if self.mode == "static"
            else None
        )
        if gates is not None:
            workers = torch.cat(
                [workers[:, :, :3] * gates.sigmoid().unsqueeze(-1), workers[:, :, 3:]],
                2,
            )
        return self.out(workers.reshape(b, t, 64))


class RecallModel(nn.Module):
    def __init__(self, mode="judge", sequence_length=12):
        super().__init__()
        self.embed = nn.Embedding(70, 64)
        self.position = nn.Parameter(torch.zeros(sequence_length, 64))
        self.attention = JudgeAttention(mode)
        self.head = nn.Linear(64, 32)

    def forward(self, x):
        return self.head(self.attention(self.embed(x) + self.position)[:, -1])


def data(seed, count):
    g = torch.Generator().manual_seed(seed)
    x = torch.full((count, 12), 69)
    keys = torch.stack([torch.randperm(32, generator=g)[:2] for _ in range(count)])
    values = torch.randint(32, (count, 2), generator=g)
    choice = torch.randint(2, (count,), generator=g)
    x[:, 0] = keys[:, 0]
    x[:, 1] = 32 + values[:, 0]
    x[:, 4] = keys[:, 1]
    x[:, 5] = 32 + values[:, 1]
    x[:, -1] = keys[torch.arange(count), choice]
    return x, values[torch.arange(count), choice]


def run(seed, steps):
    train = data(seed, 512)
    test = data(seed + 1, 128)
    out = {}
    for mode in ["ordinary", "static", "token", "judge"]:
        torch.manual_seed(seed)
        model = RecallModel(mode)
        opt = torch.optim.Adam(model.parameters(), lr=0.001)
        for step in range(steps):
            idx = torch.arange(step * 32, step * 32 + 32) % 512
            opt.zero_grad()
            loss = F.cross_entropy(model(train[0][idx]), train[1][idx])
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            accuracy = (model(test[0]).argmax(-1) == test[1]).float().mean().item()
        out[mode] = {
            "accuracy": accuracy,
            "parameters": sum(p.numel() for p in model.parameters()),
            "reload_equal": reload_equal(model, RecallModel(mode), test[0][:2]),
        }
    return {
        "conditions": out,
        "task": "12-token two-pair smoke fixture; separate seeded episodes, not disjoint-combination full study",
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
