# A Practical Workflow for Independent AI Research

I like questions that start slightly sideways.

[Read the post](research-without-losing-the-question.md)

## Current scope

The [LLM Arithmetic: Digits vs Number Words](../../../research/transformers/arithmetic-across-notations/README.md) now has a token boundary checker and an intervention scorer. That makes the next hand off more concrete: choose a local model, record the exact hook and pass the feasibility check before ranking candidates. It still would not justify writing “arithmetic circuit found” in the session note.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study research-without-losing-the-question --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
