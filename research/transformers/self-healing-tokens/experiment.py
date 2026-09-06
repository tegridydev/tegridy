"""Train a detector-gated denoiser on grouped synthetic repeated records."""

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


from repair_reference import repair, POSITIONS


class Denoiser(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Embedding(18, 64)
        self.position = nn.Parameter(torch.zeros(18, 64))
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(64, 4, 128, dropout=0, batch_first=True),
            2,
            enable_nested_tensor=False,
        )
        self.recover = nn.Linear(64, 16)
        self.detect = nn.Linear(64, 1)

    def forward(self, x):
        h = self.encoder(self.embed(x) + self.position)
        return self.recover(h)[:, POSITIONS, :], self.detect(h)[:, POSITIONS, 0]


def records(seed, count=512, prob=0.15):
    g = torch.Generator().manual_seed(seed)
    codes = torch.randperm(16**5, generator=g)[:count]
    base = torch.stack([(codes // (16**j)) % 16 for j in range(5)], 1)
    clean = torch.cat(
        [
            base,
            torch.full((count, 1), 16),
            base,
            torch.full((count, 1), 16),
            base,
            base.sum(1, keepdim=True) % 16,
        ],
        1,
    )
    noisy = clean.clone()
    mask = torch.rand((count, 15), generator=g) < prob
    replace = (
        clean[:, POSITIONS] + torch.randint(1, 16, (count, 15), generator=g)
    ) % 16
    replace = torch.where(torch.rand((count, 15), generator=g) < 0.5, 17, replace)
    noisy[:, POSITIONS] = torch.where(mask, replace, clean[:, POSITIONS])
    return clean, noisy, mask


def output(model, noisy, threshold):
    logits, detector = model(noisy)
    guess = logits.argmax(-1)
    return torch.where(detector.sigmoid() >= threshold, guess, noisy[:, POSITIONS])


def measure(pred, target, bad):
    return {
        "corrupt_recovery": (pred[bad] == target[bad]).float().mean().item()
        if bad.any()
        else None,
        "clean_false_edit": (pred[~bad] != target[~bad]).float().mean().item()
        if (~bad).any()
        else None,
        "whole_record_accuracy": (pred == target).all(1).float().mean().item(),
    }


def run(seed, steps):
    clean, noisy, mask = records(seed)
    dev = slice(384, 448)
    test = slice(448, 512)
    target = clean[test][:, POSITIONS]
    bad = mask[test]
    majority = []
    for row in noisy[test].tolist():
        record = [
            "SEP" if value == 16 else None if value == 17 else value for value in row
        ]
        repaired, _, _ = repair(record)
        majority.append([17 if repaired[i] is None else repaired[i] for i in POSITIONS])
    result = {
        "identity": measure(noisy[test][:, POSITIONS], target, bad),
        "majority": measure(torch.tensor(majority), target, bad),
    }
    for condition in ["ordinary", "gated"]:
        torch.manual_seed(seed)
        model = Denoiser()
        opt = torch.optim.Adam(model.parameters(), lr=0.001)
        for step in range(steps):
            idx = torch.arange(step * 64, step * 64 + 64) % 384
            opt.zero_grad()
            r, d = model(noisy[idx])
            loss = F.cross_entropy(r.transpose(1, 2), clean[idx][:, POSITIONS])
            if condition == "gated":
                loss = loss + F.binary_cross_entropy_with_logits(d, mask[idx].float())
            loss.backward()
            opt.step()
        model.eval()
        threshold = 1.1
        best = -1
        with torch.no_grad():
            if condition == "gated":
                for candidate in [i / 20 for i in range(21)]:
                    metrics = measure(
                        output(model, noisy[dev], candidate),
                        clean[dev][:, POSITIONS],
                        mask[dev],
                    )
                    if (
                        metrics["clean_false_edit"] <= 0.01
                        and metrics["corrupt_recovery"] > best
                    ):
                        threshold = candidate
                        best = metrics["corrupt_recovery"]
                pred = output(model, noisy[test], threshold)
            else:
                pred = model(noisy[test])[0].argmax(-1)
            result[condition] = measure(pred, target, bad)
            result[condition].update(
                last_training_loss=loss.item(),
                reload_equal=reload_equal(model, Denoiser(), noisy[:2]),
            )
            if condition == "gated":
                result[condition].update(
                    threshold=threshold,
                    threshold_status="abstain"
                    if threshold > 1
                    else "development-selected",
                )
    return {
        "conditions": result,
        "split_clean_records": [384, 64, 64],
        "selection": "threshold chosen on development records only",
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
