import pytest
import torch
from torch import nn
from intervene import boundary, answer_logprob


class Tiny(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(8, 4)
        self.head = nn.Linear(4, 8)

    def forward(self, x):
        return self.head(self.embedding(x).cumsum(1))


def test_complete_answer_and_intervention_cleanup():
    torch.manual_seed(17)
    model = Tiny()
    tokens = torch.tensor([[1, 2, 3, 4]])
    expected = (
        model(tokens)[:, 1:-1]
        .log_softmax(-1)
        .gather(-1, tokens[:, 2:, None])
        .sum()
        .item()
    )
    assert answer_logprob(model, tokens, 2) == expected
    altered = answer_logprob(model, tokens, 2, model.embedding, [0, 1, 2, 3])
    assert altered != expected
    assert not model.embedding._forward_hooks and model.training


def test_token_boundary_rejection():
    assert boundary(lambda s: list(s), "a", "bc") == (["a"], ["a", "b", "c"])
    with pytest.raises(ValueError):
        boundary(lambda s: [s], "a", "b")
