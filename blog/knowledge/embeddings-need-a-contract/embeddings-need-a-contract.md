# [td] tegridydev | an embedding column needs more than a convincing name

An embedding workbench is a very satisfying thing to build.

Load some text, turn it into vectors, add a search box and a colourful scatterplot and suddenly I have what looks like a tiny semantic brain.

The problem is that a column named `embedding` does not actually prove I have embeddings :)

Before I trust the search, I want a contract between generation, storage and retrieval: **what produced this vector, what happened to the text first, and which other vectors is it valid to compare against?**

Think of map coordinates. Two numbers aren't enough unless I know the coordinate system.

## what actually made the vector?

A text encoder produces a fixed-dimensional representation using a specific model and procedure.

That procedure can include tokenisation, prefixes, pooling, normalisation and truncation. Some retrieval models expect different instructions for queries and documents.

Matching dimensions isn't enough.

Two unrelated encoders can both output 768 values and still live in completely different representation spaces.

Sentence-BERT is a useful established example because its sentence representations are trained for comparison rather than being arbitrary numbers generated as text. [Reimers and Gurevych, 2019](https://arxiv.org/abs/1908.10084v1).

## save the recipe beside the vectors

I want a small manifest:

```text
model + immutable revision
tokeniser + revision
preprocessing
query/document instructions
pooling
normalisation
dimension
precision
maximum input length
```

Each passage then keeps a stable ID, source/version ID, exact encoded text or recoverable reference, text hash, manifest ID and status.

If encoding fails, save the failure.

Don't quietly replace it with an all-zero vector and let that thing wander into the index like nothing happened.

The cache key also needs the whole representation recipe. Change the prefix or truncation rule and the old cache may no longer be compatible even if the friendly model name stayed the same.

## validate before indexing

Every vector should be one-dimensional, have the declared length and contain finite numbers.

Reject ragged values, booleans, NaNs and infinities.

Zero vectors need an explicit policy for cosine similarity because their norm is zero. For ordinary nonzero vectors:

```text
cos(q, d) = dot(q, d) / (norm(q) · norm(d))
```

A tiny sanity check:

```text
q = (1, 0)

cos(q, (2, 0))  =  1
cos(q, (0, 1))  =  0
cos(q, (-1, 0)) = -1
```

Opposite directions stay negative. I don't want an accidental `abs()` turning them into perfect matches.

And I definitely don't want vectors from incompatible manifests compared just because the arrays are the same length.

## search, clusters and pretty dots are different jobs

Retrieval asks whether useful passages rank near the top.

Clustering proposes groups.

Projection squashes some geometry into two or three dimensions so I can look at it.

A gorgeous cluster doesn't prove its members answer the same question, and a 2D plot can distort relationships from the original space. The UI should always let me get back to the source text and real score.

An exact error code is a nice example. Lexical search may nail the identifier while semantic search retrieves a beautifully related explanation that never mentions it.

That's a good reason to evaluate both, not declare semantic search universally better because it has more floating-point numbers involved.

## make the benchmark readable

I'd start with a small self-authored corpus containing exact IDs, paraphrases, negation, conflicting versions, near-duplicates, long passages and queries with no valid answer.

Keep query families together when splitting development from evaluation.

Then compare:

```text
lexical baseline
vector ranking
combined ranking
```

over the same passage set.

A simple reciprocal-rank fusion baseline is enough to start:

```text
score = Σ 1 / (60 + rank)
```

For metrics I'd keep precision/recall and graded ranking measures such as nDCG, but I care just as much about the failure table:

```text
wrong version
identifier missed
missing context
truncation
representation mismatch
ambiguous query
disputed relevance
```

That usually tells me what to fix much faster than one aggregate score.

## debug the contract before changing the model

If an exact code misses, inspect lexical results before swapping encoders.

If every query suddenly looks unrelated, compare the query/document manifests.

If only long passages fail, inspect the exact encoded text and truncation.

Those are different bugs and no amount of t-SNE colouring is going to fix them for me.

## what I built from this

[vector_reference.py](vector_reference.py) validates compatible finite vectors and signed cosine using only the standard library.

```sh
python3 vector_reference.py
```

The local [search.py](search.py) tool then provides a BM25-style lexical baseline, signed-cosine ranking over supplied vectors and reciprocal-rank fusion.

It checks unique document IDs, dimensions and exact representation-manifest compatibility. Negative cosine scores remain visible.

The [module README](README.md) documents the index/query format. No embedding model is bundled or called; neural relevance still depends on externally supplied vectors and truthful provenance.

That's deliberate.

Before I build a bigger semantic search toy, I want to know the numbers in my `embedding` column actually mean what the label says they mean.

## reference

Nils Reimers and Iryna Gurevych. **Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.** EMNLP 2019; arXiv v1, 27 August 2019. [Paper record](https://arxiv.org/abs/1908.10084v1). DOI: `10.48550/arXiv.1908.10084`.

[Blog index](../../README.md)
