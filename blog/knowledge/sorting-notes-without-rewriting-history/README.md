# Organising Research Notes Without Losing History

A research folder can become an archaeological site surprisingly quickly.

[Read the post](sorting-notes-without-rewriting-history.md)

## Current scope

The current public modules keep their implementation, tests, dependency file and any result receipt beside the article. A result receipt says which synthetic run produced it; it does not replace the source code or turn a specification into historical evidence. I can refine the current writing while leaving the original Minecraft HTML and screenshots intact. The archive stays outside this public implementation pass.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study sorting-notes-without-rewriting-history --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
