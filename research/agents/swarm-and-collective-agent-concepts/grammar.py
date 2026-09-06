"""Finite legal sequences, ordered counts and token-matched neighbour coupling."""

from collections import Counter
import json
import math
import random

GRAMMAR = {
    "START": ["A", "B"],
    "A": ["C", "D"],
    "B": ["C", "D"],
    "C": ["E"],
    "D": ["F"],
    "E": ["END"],
    "F": ["END"],
}


def legal_sequences(grammar=GRAMMAR):
    def walk(state, path):
        if state == "END":
            yield tuple(path)
            return
        if len(path) > 16:
            raise ValueError("grammar is cyclic or exceeds bound")
        for token in grammar[state]:
            yield from walk(token, path + [token])

    return list(walk("START", []))


def counts(sequences):
    result = Counter()
    for sequence in sequences:
        for a, b in zip(("START",) + tuple(sequence), sequence):
            result[a, b] += 1
    return result


def likelihood(training, evaluation, alpha=1.0):
    if alpha <= 0:
        raise ValueError("positive fixed smoothing required")
    tally = counts(training)
    logs = []
    for sequence in evaluation:
        state = "START"
        for token in sequence:
            legal = GRAMMAR[state]
            if token not in legal:
                raise ValueError("illegal evaluation sequence")
            total = sum(tally[state, b] for b in legal)
            logs.append(
                math.log((tally[state, token] + alpha) / (total + alpha * len(legal)))
            )
            state = token
    return sum(logs) / len(logs) if logs else None


def generate(seed, coupling=0.0, tokens=2000):
    if coupling < 0 or tokens < 0 or tokens % 4:
        raise ValueError(
            "nonnegative coupling and token budget divisible by four required"
        )
    rng = random.Random(seed)
    histories = [None] * 4
    sequences = []
    for turn in range(tokens // 4):
        agent = turn % 4
        neighbour = histories[(agent - 1) % 4]
        state = "START"
        sequence = []
        while state != "END":
            choices = GRAMMAR[state]
            position = len(sequence)
            weights = [
                1 + coupling * (neighbour is not None and neighbour[position] == token)
                for token in choices
            ]
            state = rng.choices(choices, weights=weights, k=1)[0]
            sequence.append(state)
        histories[agent] = tuple(sequence)
        sequences.append(tuple(sequence))
    return sequences


def compare():
    legal = legal_sequences()
    report = []
    for seed in [17, 29, 43, 59, 71]:
        for coupling in [0.0, 2.0]:
            sequences = generate(seed, coupling)
            report.append(
                dict(
                    seed=seed,
                    coupling=coupling,
                    tokens=sum(map(len, sequences)),
                    coverage=len(set(sequences)) / len(legal),
                    held_out_uniform_grammar_logprob=likelihood(sequences, legal),
                    sequence_counts={
                        " ".join(k): v for k, v in Counter(sequences).items()
                    },
                )
            )
    return report


if __name__ == "__main__":
    print(json.dumps(compare(), indent=2))
