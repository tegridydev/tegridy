"""Float-preserving clone and explicitly separate STE ternary-weight simulation."""

import copy
import torch
from torch import nn
from torch.nn import functional as F


def ternary(weight):
    scale = weight.detach().abs().mean()
    if scale == 0:
        return torch.zeros_like(weight), scale
    symbols = (weight / scale).round().clamp(-1, 1)
    return symbols * scale, scale


class TernaryLinear(nn.Linear):
    def forward(self, x):
        quantized, _ = ternary(self.weight)
        straight_through = self.weight + (quantized - self.weight).detach()
        return F.linear(x, straight_through, self.bias)


def convert(model, quantized=False):
    clone = copy.deepcopy(model)
    if not quantized:
        return clone
    seen = {}

    def visit(module):
        if id(module) in seen:
            return seen[id(module)]
        if isinstance(module, nn.Linear):
            new = TernaryLinear(
                module.in_features, module.out_features, bias=module.bias is not None
            ).to(device=module.weight.device, dtype=module.weight.dtype)
            # Reuse cloned Parameters to retain ties with other projections/embeddings.
            new.weight = module.weight
            new.bias = module.bias
            new.train(module.training)
            seen[id(module)] = new
            return new
        seen[id(module)] = module
        for name, child in list(module._modules.items()):
            if child is not None:
                module._modules[name] = visit(child)
        return module

    return visit(clone)
