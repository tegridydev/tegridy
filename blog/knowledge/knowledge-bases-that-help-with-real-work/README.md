# Building Technical Knowledge Bases for Troubleshooting

I keep technical knowledge bases because remembering a term is different from knowing which check to perform next.

[Read the post](knowledge-bases-that-help-with-real-work.md)

## Current scope

There is now a [Embedding Compatibility: Models, Vectors and Search](../embeddings-need-a-contract/README.md) and a [Graph Based Research Memory with Source Provenance](../../../research/knowledge/graph-memory-with-a-paper-trail/README.md). I can use those to check two smaller questions: did the useful record rank, and did I keep its version condition? The external knowledge bases discussed here remain external projects; a useful reading route does not require pretending I rebuilt them.

[Topic index](../README.md) · [Blog index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study knowledge-bases-that-help-with-real-work --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
