# knowledge bases should help me choose the next check

I keep technical knowledge bases because remembering a term is different from knowing which check to perform next.

[Read the post](knowledge-bases-that-help-with-real-work.md)

## Current scope

There is now a [local lexical/vector search tool](../embeddings-need-a-contract/README.md) and a [Cedar evidence fixture](../../../research/knowledge/graph-memory-with-a-paper-trail/README.md). I can use those to check two smaller questions: did the useful record rank, and did I keep its version condition? The external knowledge bases discussed here remain external projects; a useful reading route does not require pretending I rebuilt them.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study knowledge-bases-that-help-with-real-work --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

The four-question walkthrough separated two scoped answers, one request needing clarification and one unsupported question. This demonstrates the intended evidence and next-check behaviour on authored documents; it is not a general question-answering benchmark.

See the [article](knowledge-bases-that-help-with-real-work.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
