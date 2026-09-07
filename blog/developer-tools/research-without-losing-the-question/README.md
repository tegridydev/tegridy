# doing research without losing the question

I like questions that start slightly sideways.

[Read the post](research-without-losing-the-question.md)

## Current scope

The [arithmetic module](../../../research/transformers/arithmetic-across-notations/README.md) now has a token-boundary checker and an intervention scorer. That makes the next hand-off more concrete: choose a local model, record the exact hook and pass the feasibility check before ranking candidates. It still would not justify writing “arithmetic circuit found” in the session note.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study research-without-losing-the-question --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The worked example linked two claims to one recorded evidence item while preserving the question and revision trail. It demonstrates traceability, not an independently measured improvement in research quality.

See the [article](research-without-losing-the-question.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
