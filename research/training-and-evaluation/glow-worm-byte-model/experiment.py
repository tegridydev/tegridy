"""Small causal byte Transformer with document-local windows and byte-only loss."""

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


class ByteModel(nn.Module):
    def __init__(self, width=128, layers=4):
        super().__init__()
        self.width = width
        self.layers = layers
        self.embedding = nn.Embedding(257, width)
        self.position = nn.Embedding(256, width)
        self.blocks = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                width, 4, width * 4, dropout=0, batch_first=True
            ),
            layers,
            enable_nested_tensor=False,
        )
        self.head = nn.Linear(width, 257)

    def forward(self, x):
        if x.shape[1] > 256:
            raise ValueError("context exceeds 256 bytes")
        t = x.shape[1]
        mask = torch.triu(torch.ones(t, t, dtype=torch.bool, device=x.device), 1)
        return self.head(
            self.blocks(
                self.embedding(x) + self.position(torch.arange(t, device=x.device)),
                mask=mask,
            )
        )


def windows(documents, length=32):
    rows = []
    for raw in documents:
        values = list(raw) + [256]
        for start in range(0, len(values) - length, length):
            row = values[start : start + length + 1]
            rows.append((row[:-1], row[1:]))
    if not rows:
        raise ValueError("no complete document-local windows")
    return torch.tensor([x for x, y in rows]), torch.tensor([y for x, y in rows])


def run(seed, steps, training_documents=None, evaluation_documents=None):
    import hashlib

    training_documents = training_documents or [
        ("A small byte model reads this training document. " * 12).encode()
    ]
    evaluation_documents = evaluation_documents or [
        ("This separate evaluation text includes café and a seed 🌱. " * 6).encode()
    ]
    train_hashes = [hashlib.sha256(d).hexdigest() for d in training_documents]
    test_hashes = [hashlib.sha256(d).hexdigest() for d in evaluation_documents]
    if set(train_hashes) & set(test_hashes):
        raise ValueError("identical documents cross train/evaluation boundary")
    train = windows(training_documents)
    test = windows(evaluation_documents)
    model = ByteModel()
    opt = torch.optim.Adam(model.parameters(), lr=0.001)
    for step in range(steps):
        idx = torch.arange(step * 8, step * 8 + 8) % len(train[0])
        opt.zero_grad()
        logits = model(train[0][idx])
        loss = F.cross_entropy(logits.reshape(-1, 257), train[1][idx].reshape(-1))
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        losses = F.cross_entropy(
            model(test[0]).transpose(1, 2), test[1], reduction="none"
        )
        byte_mask = test[1] < 256
        bpb = (losses[byte_mask].mean() / torch.log(torch.tensor(2.0))).item()
    return {
        "held_out_bits_per_byte": bpb,
        "evaluation_bytes": int(byte_mask.sum()),
        "last_training_loss": loss.item(),
        "reload_equal": reload_equal(model, ByteModel(), test[0][:2]),
        "training_document_hashes": train_hashes,
        "evaluation_document_hashes": test_hashes,
        "training_windows": len(train[0]),
        "evaluation_windows": len(test[0]),
        "window_policy": "32-token nonoverlapping document-local windows; incomplete tails excluded; input first token is context only",
    }


def main():
    import argparse, json, platform

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=40)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--training-documents", type=Path, nargs="+")
    parser.add_argument("--evaluation-documents", type=Path, nargs="+")
    args = parser.parse_args()
    if bool(args.training_documents) != bool(args.evaluation_documents):
        parser.error("supply both training and evaluation documents")
    if args.steps < 1:
        parser.error("--steps must be positive")
    torch.set_num_threads(2)
    torch.manual_seed(args.seed)
    result = run(
        args.seed,
        args.steps,
        [p.read_bytes() for p in args.training_documents]
        if args.training_documents
        else None,
        [p.read_bytes() for p in args.evaluation_documents]
        if args.evaluation_documents
        else None,
    )
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
