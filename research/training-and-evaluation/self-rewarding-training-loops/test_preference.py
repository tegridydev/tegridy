import torch
from preference import dpo, sequence_logprob, judge_audit


def test_loss_direction_and_reference_frozen():
    preferred = torch.tensor([-2.0, -3.0], requires_grad=True)
    rejected = torch.tensor([-4.0, -2.0], requires_grad=True)
    reference = torch.tensor([-3.0, -3.0], requires_grad=True)
    initial = dpo(preferred, rejected, reference, reference)
    assert dpo(preferred + 1, rejected, reference, reference) < initial
    assert dpo(preferred, rejected + 1, reference, reference) > initial
    initial.backward()
    assert (
        reference.grad is None
        and (preferred.grad < 0).all()
        and (rejected.grad > 0).all()
    )


def test_mask_and_actual_parameter_step():
    model = torch.nn.Linear(4, 3)
    x = torch.randn(2, 4, 4)
    targets = torch.zeros(2, 4, dtype=torch.long)
    mask = torch.tensor([[False, False, True, True]] * 2)
    logits = model(x)
    a = sequence_logprob(logits, targets, mask)
    modified = logits.detach().clone()
    modified[:, :2] += torch.randn_like(modified[:, :2]) * 100
    assert torch.allclose(a, sequence_logprob(modified, targets, mask))
    rejected = sequence_logprob(logits, torch.ones_like(targets), mask)
    loss = dpo(a, rejected, a.detach(), rejected.detach())
    before = model.weight.detach().clone()
    loss.backward()
    torch.optim.SGD(model.parameters(), lr=0.1).step()
    assert not before.equal(model.weight)


def test_style_biased_judge_fails():
    pairs = [
        dict(
            id="short-correct",
            correct="13",
            incorrect="A polished long explanation says 14.",
        )
    ]
    assert not judge_audit(pairs, lambda a, b: "left" if len(a) > len(b) else "right")[
        "passed"
    ]
