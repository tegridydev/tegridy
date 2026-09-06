"""Independent head-width mutation fixture; not a recovered upstream revision."""

import torch
from torch import nn


class Head(nn.Module):
    def __init__(self, width, dimension=64):
        super().__init__()
        self.width = width
        self.q = nn.Linear(dimension, width, bias=False)
        self.k = nn.Linear(dimension, width, bias=False)
        self.v = nn.Linear(dimension, width, bias=False)
        self.output = nn.Linear(width, dimension, bias=False)

    def forward(self, x, padding=None):
        scores = self.q(x) @ self.k(x).transpose(-1, -2) / self.width**0.5
        if padding is not None:
            valid = ~padding[:, None, :]
            scores = scores.masked_fill(~valid, float("-inf"))
            scores = torch.where(
                valid.any(-1, keepdim=True), scores, torch.zeros_like(scores)
            )
            weights = scores.softmax(-1) * valid
        else:
            weights = scores.softmax(-1)
        return self.output(weights @ self.v(x))


class AdaptiveAttention(nn.Module):
    def __init__(self, widths=(16, 16, 16, 16)):
        super().__init__()
        if not widths or any(type(w) is not int or w < 1 for w in widths):
            raise ValueError("positive head widths required")
        self.heads = nn.ModuleList(Head(w) for w in widths)

    def forward(self, x, padding=None):
        return sum(head(x, padding) for head in self.heads)

    def architecture(self):
        return [h.width for h in self.heads]

    def mutate(self, index, width, parameter_budget):
        if type(width) is not int or width < 1:
            raise ValueError("positive width required")
        old = self.heads[index]
        before = {n: id(p) for n, p in self.named_parameters()}
        proposed = (
            sum(p.numel() for p in self.parameters()) + (width - old.width) * 64 * 4
        )
        if proposed > parameter_budget:
            raise ValueError("parameter budget exceeded")
        new = Head(width).to(device=old.q.weight.device, dtype=old.q.weight.dtype)
        with torch.no_grad():
            overlap = min(width, old.width)
            for name in ["q", "k", "v"]:
                getattr(new, name).weight[:overlap].copy_(
                    getattr(old, name).weight[:overlap]
                )
            new.output.weight[:, :overlap].copy_(old.output.weight[:, :overlap])
        self.heads[index] = new
        # Reset all moments. Comparison controls must reset at the same boundary.
        optimizer = torch.optim.Adam(self.parameters(), lr=0.001)
        return optimizer, dict(
            operation="widen" if width > old.width else "narrow",
            head=index,
            old_width=old.width,
            new_width=width,
            parameters=proposed,
            old_parameter_ids=before,
            new_parameter_ids={n: id(p) for n, p in self.named_parameters()},
            optimizer_policy="reset-all-moments",
        )

    def checkpoint(self):
        return dict(widths=self.architecture(), state=self.state_dict())

    @classmethod
    def restore(cls, checkpoint):
        model = cls(checkpoint["widths"])
        model.load_state_dict(checkpoint["state"])
        return model
