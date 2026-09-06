"""Train FBAC and its dense/static/base controls on held-out operand pairs."""

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


class FaceMixer(nn.Module):
    def __init__(self, static=False):
        super().__init__()
        self.static = static
        self.projections = nn.ModuleList(
            nn.Linear(16, 64, bias=False) for _ in range(4)
        )
        if static:
            self.logits = nn.Parameter(torch.zeros(4))
        else:
            self.gates = nn.ModuleList(nn.Linear(80, 1) for _ in range(4))

    def forward(self, x, permutation=None):
        faces = x.split(16, dim=-1)
        logits = (
            self.logits.expand(*x.shape[:-1], 4)
            if self.static
            else torch.cat(
                [g(torch.cat([x, f], -1)) for g, f in zip(self.gates, faces)], -1
            )
        )
        weights = logits.softmax(-1)
        if permutation is not None:
            weights = weights[permutation]
        updates = torch.stack(
            [F.gelu(p(f)) for p, f in zip(self.projections, faces)], -2
        )
        return x + (weights.unsqueeze(-1) * updates).sum(-2)


class Model(nn.Module):
    def __init__(self, mode="fbac"):
        super().__init__()
        self.mode = mode
        self.embed = nn.Embedding(40, 64)
        self.position = nn.Parameter(torch.zeros(8, 64))
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(64, 4, 256, dropout=0, batch_first=True),
            2,
            enable_nested_tensor=False,
        )
        self.adapter = (
            FaceMixer()
            if mode == "fbac"
            else FaceMixer(True)
            if mode == "static"
            else nn.Sequential(nn.Linear(64, 34), nn.GELU(), nn.Linear(34, 64))
            if mode == "dense"
            else nn.Identity()
        )
        self.head = nn.Linear(64, 32)

    def forward(self, x, permutation=None):
        h = self.encoder(self.embed(x) + self.position)
        h = h[:, -1]
        h = (
            h + self.adapter(h)
            if self.mode == "dense"
            else self.adapter(h, permutation)
            if self.mode == "fbac"
            else self.adapter(h)
        )
        return self.head(h)


def dataset(seed=1729):
    g = torch.Generator().manual_seed(seed)
    pairs = torch.cartesian_prod(torch.arange(32), torch.arange(32))
    pairs = pairs[torch.randperm(1024, generator=g)]
    result = []
    for subset in [pairs[:768], pairs[768:896], pairs[896:]]:
        a, b = subset[:, 0].repeat_interleave(4), subset[:, 1].repeat_interleave(4)
        modes = torch.arange(4).repeat(len(subset))
        noise = torch.randint(32, (len(a),), generator=g)
        x = torch.stack(
            [
                32 + modes,
                torch.full_like(a, 36),
                a,
                torch.full_like(a, 37),
                b,
                torch.full_like(a, 38),
                noise,
                torch.full_like(a, 39),
            ],
            1,
        )
        y = torch.where(
            modes == 0,
            a,
            torch.where(
                modes == 1,
                b,
                torch.where(modes == 2, torch.maximum(a, b), torch.minimum(a, b)),
            ),
        )
        result.append((x, y))
    return result


def run(seed, steps):
    train, dev, test = dataset(seed)
    out = {}
    for mode in ["base", "dense", "static", "fbac"]:
        torch.manual_seed(seed)
        model = Model(mode)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        for step in range(steps):
            idx = torch.arange(step * 64, step * 64 + 64) % len(train[0])
            optimizer.zero_grad()
            loss = F.cross_entropy(model(train[0][idx]), train[1][idx])
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            accuracy = (model(test[0]).argmax(-1) == test[1]).float().mean().item()
        out[mode] = {
            "final_accuracy": accuracy,
            "last_training_loss": loss.item(),
            "parameters": sum(p.numel() for p in model.parameters()),
            "reload_equal": reload_equal(model, Model(mode), test[0][:4]),
        }
        if mode == "fbac":
            within = torch.arange(len(test[0]))
            modes = test[0][:, 0]
            for task in modes.unique():
                idx = torch.where(modes == task)[0]
                within[idx] = idx.roll(1)
            cross = torch.arange(len(test[0])).roll(1)
            with torch.no_grad():
                out[mode]["within_mode_gate_swap_accuracy"] = (
                    (model(test[0], within).argmax(-1) == test[1]).float().mean().item()
                )
                out[mode]["cross_mode_gate_swap_accuracy"] = (
                    (model(test[0], cross).argmax(-1) == test[1]).float().mean().item()
                )
    return {
        "conditions": out,
        "split_pairs": [768, 128, 128],
        "fbac_parameters": sum(p.numel() for p in FaceMixer().parameters()),
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
