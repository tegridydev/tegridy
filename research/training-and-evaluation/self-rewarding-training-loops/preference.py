"""Response-masked DPO loss; independent correctness labels remain external."""

import torch
from torch.nn import functional as F


def sequence_logprob(logits, targets, response_mask):
    if logits.shape[:-1] != targets.shape or targets.shape != response_mask.shape:
        raise ValueError("shape mismatch")
    if response_mask.dtype != torch.bool or not response_mask.any(-1).all():
        raise ValueError("each response needs at least one scored token")
    selected = logits.log_softmax(-1).gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    return selected.masked_fill(~response_mask, 0).sum(-1)


def dpo(preferred, rejected, reference_preferred, reference_rejected, beta=0.1):
    if beta <= 0:
        raise ValueError("beta must be positive")
    margin = (preferred - rejected) - (
        reference_preferred.detach() - reference_rejected.detach()
    )
    return -F.logsigmoid(beta * margin).mean()


def judge_audit(pairs, judge):
    outcomes = []
    for pair in pairs:
        # left/right outputs must be independent of pair order and presentation style.
        forward = judge(pair["correct"], pair["incorrect"])
        reverse = judge(pair["incorrect"], pair["correct"])
        outcomes.append(
            dict(
                id=pair["id"],
                correct_both_orders=forward == "left" and reverse == "right",
                order_consistent=(forward, reverse)
                in [("left", "right"), ("right", "left")],
            )
        )
    return dict(
        cases=outcomes,
        passed=bool(outcomes) and all(o["correct_both_orders"] for o in outcomes),
    )
