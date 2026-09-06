"""Last-prompt-position intervention with complete teacher-forced answer scoring."""

import argparse
import json
from pathlib import Path
import torch


def boundary(tokenize, prompt, answer):
    prefix = tokenize(prompt)
    full = tokenize(prompt + answer)
    if not prefix or full[: len(prefix)] != prefix or len(full) <= len(prefix):
        raise ValueError("answer crosses token boundary or contributes no token")
    return prefix, full


def answer_logprob(
    model, token_ids, prompt_length, module=None, features=(), replacement=0.0
):
    if (
        token_ids.ndim != 2
        or token_ids.shape[0] != 1
        or not 1 <= prompt_length < token_ids.shape[1]
    ):
        raise ValueError("one sequence with nonempty prompt and answer required")
    handle = None
    calls = 0
    was_training = model.training

    def replace(layer, inputs, output):
        nonlocal calls
        calls += 1
        tensor = output[0] if isinstance(output, tuple) else output
        if tensor.ndim != 3 or tensor.shape[1] < prompt_length:
            raise ValueError("hook must expose token positions")
        if any(type(f) is not int or not 0 <= f < tensor.shape[-1] for f in features):
            raise ValueError("invalid feature index")
        modified = tensor.clone()
        modified[:, prompt_length - 1, list(features)] = replacement
        return (modified,) + output[1:] if isinstance(output, tuple) else modified

    try:
        if module is not None:
            handle = module.register_forward_hook(replace)
        model.eval()
        with torch.no_grad():
            output = model(token_ids)
            logits = output.logits if hasattr(output, "logits") else output
            answer = token_ids[:, prompt_length:]
            prediction = logits[:, prompt_length - 1 : -1].log_softmax(-1)
            logprob = (
                prediction.gather(-1, answer.unsqueeze(-1)).squeeze(-1).sum().item()
            )
        if module is not None and calls != 1:
            raise ValueError("hook execution count differs from one")
        return logprob
    finally:
        if handle is not None:
            handle.remove()
        model.train(was_training)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("model_directory", type=Path)
    p.add_argument("prompt")
    p.add_argument("answer")
    p.add_argument("--hook", required=True)
    p.add_argument("--features", nargs="+", type=int, required=True)
    a = p.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        a.model_directory, local_files_only=True, trust_remote_code=False
    )
    model = AutoModelForCausalLM.from_pretrained(
        a.model_directory, local_files_only=True, trust_remote_code=False
    )
    prefix, full = boundary(
        lambda text: tokenizer.encode(text, add_special_tokens=False),
        a.prompt,
        a.answer,
    )
    tokens = torch.tensor([full])
    modules = dict(model.named_modules())
    baseline = answer_logprob(model, tokens, len(prefix))
    ablated = answer_logprob(model, tokens, len(prefix), modules[a.hook], a.features)
    print(
        json.dumps(
            dict(
                prompt_tokens=prefix,
                answer_tokens=full[len(prefix) :],
                baseline_logprob=baseline,
                ablated_logprob=ablated,
                difference=ablated - baseline,
                hook=a.hook,
                features=a.features,
                scope="one supplied prompt; feasibility and cross-notation study remain separate",
            ),
            indent=2,
        )
    )
