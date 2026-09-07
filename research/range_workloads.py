"""Seeded, distinct range-query workloads shared by the two tree studies."""
import math
import random

def workloads(seed, count, distribution):
    rng = random.Random(seed)
    points = []
    for index in range(count):
        center = 0.2 if index % 3 else 0.8
        coordinates = []
        for axis in range(4):
            value = (rng.random() if distribution == 'uniform' else .5 if distribution == 'identical'
                     else rng.gauss(center, .025) if distribution == 'clustered'
                     else rng.gauss(.15 if index % 5 else .85, .015) if distribution == 'bursty-time' and axis == 3
                     else rng.random() ** 5 if distribution == 'imbalanced' else rng.random())
            coordinates.append(min(math.nextafter(1., 0.), max(0., value)))
        points.append(tuple(coordinates) + (rng.uniform(-1, 1),))
    return points


def queries(seed, count=100):
    rng = random.Random(seed)
    result, seen = [], set()
    while len(result) < count:
        aligned = len(result) < count // 2
        bounds = []
        for _ in range(4):
            if aligned:
                a, b = sorted(rng.sample(range(9), 2))
                bounds.append((a / 8, b / 8))
            else:
                a, b = sorted([rng.random(), rng.random()])
                bounds.append((a, b))
        bounds = tuple(bounds)
        if bounds not in seen:
            seen.add(bounds)
            result.append(bounds)
    return result


