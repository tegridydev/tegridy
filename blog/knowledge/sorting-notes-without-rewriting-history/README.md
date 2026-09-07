# sorting old notes without rewriting history

A research folder can become an archaeological site surprisingly quickly.

[Read the post](sorting-notes-without-rewriting-history.md)

## Current scope

The current public modules keep their implementation, tests, dependency file and any result receipt beside the article. A result receipt says which synthetic run produced it; it does not replace the source code or turn a specification into historical evidence. I can refine the current writing while leaving the original Minecraft HTML and screenshots intact. The archive stays outside this public implementation pass.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study sorting-notes-without-rewriting-history --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The archive fixture identified 500 exact-duplicate groups among 1,000 files and reported two name conflicts. Original files were preserved. Repeating this deterministic inventory with different seed labels does not provide independent statistical evidence.

See the [article](sorting-notes-without-rewriting-history.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
