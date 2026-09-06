"""Episode-isolated FIFO memory with explicitly delayed, detached writes."""

import torch
from torch import nn


class Memory(nn.Module):
    def __init__(self, batch_size=1, total_capacity=32, heads=4, width=16):
        super().__init__()
        if any(type(v) is not int or v < 1 for v in (batch_size, total_capacity, heads, width)) or total_capacity % heads:
            raise ValueError("capacity must divide evenly across heads")
        shape = (batch_size, heads, total_capacity // heads, width)
        self.register_buffer("keys", torch.zeros(shape))
        self.register_buffer("values", torch.zeros(shape))
        self.register_buffer("created", torch.full(shape[:-1], -1, dtype=torch.long))
        self.register_buffer(
            "cursor", torch.zeros((batch_size, heads), dtype=torch.long)
        )
        self.register_buffer(
            "last_write", torch.full((batch_size,), -1, dtype=torch.long)
        )
        self.gate = nn.Parameter(torch.zeros(heads))

    def reset(self, episode=None):
        with torch.no_grad():
            index = slice(None) if episode is None else episode
            self.keys[index] = 0
            self.values[index] = 0
            self.created[index] = -1
            self.cursor[index] = 0
            self.last_write[index] = -1

    def write(self, keys, values, completed_step):
        if (
            keys.shape != self.keys.shape[:2] + self.keys.shape[-1:]
            or values.shape != keys.shape
        ):
            raise ValueError("writes require [batch,head,width]")
        if not torch.isfinite(keys).all() or not torch.isfinite(values).all():
            raise ValueError("nonfinite memory write")
        if type(completed_step) is not int or completed_step < 0 or (self.last_write >= completed_step).any():
            raise ValueError("write steps must increase; reset between episodes")
        with torch.no_grad():
            for batch in range(len(keys)):
                for head in range(keys.shape[1]):
                    slot = int(self.cursor[batch, head])
                    self.keys[batch, head, slot] = keys[batch, head].detach()
                    self.values[batch, head, slot] = values[batch, head].detach()
                    self.created[batch, head, slot] = completed_step
                    self.cursor[batch, head] = (slot + 1) % self.keys.shape[2]
            self.last_write.fill_(completed_step)

    def forward(self, query, prediction_step):
        if type(prediction_step) is not int or prediction_step < 0 or not torch.isfinite(query).all():
            raise ValueError("finite query and nonnegative integer prediction step required")
        if query.shape != self.keys.shape[:2] + self.keys.shape[-1:]:
            raise ValueError("query requires [batch,head,width]")
        eligible = (self.created >= 0) & (self.created < prediction_step)
        scores = (query.unsqueeze(-2) * self.keys).sum(-1) / query.shape[-1] ** 0.5
        scores = scores.masked_fill(~eligible, float("-inf"))
        has = eligible.any(-1, keepdim=True)
        scores = torch.where(has, scores, torch.zeros_like(scores))
        weights = scores.softmax(-1) * eligible
        return (weights.unsqueeze(-1) * self.values).sum(-2) * self.gate.sigmoid()[
            None, :, None
        ]
