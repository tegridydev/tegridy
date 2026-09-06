"""One-forward-pass activation capture keyed by token occurrence and hook."""

import hashlib
import json
import torch


def capture(
    model, token_ids, hooks, model_revision, tokenizer_revision, max_values=100000
):
    if token_ids.ndim != 2 or not hooks or len(set(hooks)) != len(hooks):
        raise ValueError("batch token matrix and unique hooks required")
    if not model_revision or not tokenizer_revision:
        raise ValueError("model/tokenizer revisions required")
    modules = dict(model.named_modules())
    handles = []
    recorded = {}
    was_training = model.training

    def hook(name):
        def receive(module, inputs, output):
            tensor = output[0] if isinstance(output, tuple) else output
            if (
                not isinstance(tensor, torch.Tensor)
                or tensor.ndim != 3
                or tuple(tensor.shape[:2]) != tuple(token_ids.shape)
            ):
                raise ValueError("hook must return [batch,position,feature]")
            if name in recorded:
                raise ValueError(
                    "selected module executed more than once; invocation identity required"
                )
            if sum(t.numel() for t in recorded.values()) + tensor.numel() > max_values:
                raise ValueError("capture budget exceeded")
            if not torch.isfinite(tensor).all():
                raise ValueError("nonfinite activation")
            recorded[name] = tensor.detach().cpu().clone()

        return receive

    try:
        for name in hooks:
            handles.append(modules[name].register_forward_hook(hook(name)))
        model.eval()
        with torch.no_grad():
            model(token_ids)
    finally:
        for handle in handles:
            handle.remove()
        model.train(was_training)
    if set(recorded) != set(hooks):
        raise ValueError("one or more hooks did not execute")
    records = []
    for sample, row in enumerate(token_ids.tolist()):
        digest = hashlib.sha256(json.dumps(row).encode()).hexdigest()
        for position, token in enumerate(row):
            for name, tensor in recorded.items():
                for feature, value in enumerate(tensor[sample, position].tolist()):
                    records.append(
                        dict(
                            sample=sample,
                            prompt_hash=digest,
                            token_id=token,
                            position=position,
                            component=name,
                            feature=feature,
                            value=value,
                        )
                    )
    return dict(
        schema=1,
        manifest=dict(
            model_revision=model_revision,
            tokenizer_revision=tokenizer_revision,
            measurement="module-output",
            mode="evaluation",
            tokens=token_ids.tolist(),
        ),
        records=records,
    )


def straightness(path):
    path = torch.as_tensor(path, dtype=torch.float64)
    if path.ndim != 2 or len(path) < 2 or not torch.isfinite(path).all():
        raise ValueError("finite path with two or more positions required")
    length = torch.linalg.vector_norm(path[1:] - path[:-1], dim=-1).sum().item()
    return (
        min(1.0, torch.linalg.vector_norm(path[-1] - path[0]).item() / length)
        if length
        else None
    )


def fit_projection(discovery, dimensions=2):
    x = torch.as_tensor(discovery, dtype=torch.float64)
    if (
        x.ndim != 2
        or not torch.isfinite(x).all()
        or not 1 <= dimensions <= min(x.shape)
    ):
        raise ValueError("invalid discovery matrix or projection width")
    mean = x.mean(0)
    _, _, vh = torch.linalg.svd(x - mean, full_matrices=False)
    return mean, vh[:dimensions].T


def project(values, projection):
    mean, basis = projection
    return (torch.as_tensor(values, dtype=torch.float64) - mean) @ basis
