"""Local lexical/vector/hybrid ranking over an explicit representation manifest."""

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from vector_reference import cosine, validate


def lexical(query, documents):
    terms = Counter(re.findall(r"\w+", query.casefold()))
    corpus = [Counter(re.findall(r"\w+", d["text"].casefold())) for d in documents]
    average = sum(map(lambda c: sum(c.values()), corpus)) / len(corpus) if corpus else 0
    scored = []
    for document, words in zip(documents, corpus):
        score = 0.0
        for term in terms:
            df = sum(term in c for c in corpus)
            idf = math.log(1 + (len(corpus) - df + 0.5) / (df + 0.5))
            tf = words[term]
            if tf:
                score += (
                    idf
                    * tf
                    * 2.2
                    / (tf + 1.2 * (0.25 + 0.75 * sum(words.values()) / average))
                )
        if score:
            scored.append((document["id"], score))
    return sorted(scored, key=lambda p: (-p[1], p[0]))


def rank(query, index, query_vector=None, query_manifest=None):
    documents = index["documents"]
    if len({d["id"] for d in documents}) != len(documents):
        raise ValueError("duplicate document identity")
    lex = lexical(query, documents)
    vectors = []
    if query_vector is not None:
        manifest = index["manifest"]
        if not all(
            manifest.get(k)
            for k in ["model_revision", "tokenizer_revision", "pooling", "dimension"]
        ):
            raise ValueError("complete representation manifest required")
        validate(query_vector, manifest["dimension"])
        for d in documents:
            validate(d["vector"], manifest["dimension"])
            vectors.append(
                (d["id"], cosine(query_vector, d["vector"], query_manifest, manifest))
            )
        vectors.sort(key=lambda p: (-p[1], p[0]))
    fused = Counter()
    for ranking in [lex, vectors]:
        for position, (identity, _) in enumerate(ranking, 1):
            fused[identity] += 1 / (60 + position)
    return dict(
        lexical=lex,
        vector=vectors,
        hybrid=sorted(fused.items(), key=lambda p: (-p[1], p[0])),
        fusion="reciprocal rank, k=60; signed cosine retained in vector results",
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("index", type=Path)
    p.add_argument("query")
    p.add_argument("--query-vector", type=Path)
    a = p.parse_args()
    index = json.loads(a.index.read_text())
    vector = json.loads(a.query_vector.read_text()) if a.query_vector else None
    print(
        json.dumps(
            rank(
                a.query,
                index,
                vector["vector"] if vector else None,
                vector["manifest"] if vector else None,
            ),
            indent=2,
        )
    )
