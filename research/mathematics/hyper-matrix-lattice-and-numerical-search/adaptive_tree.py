"""Variance-refined exact 4D tree; fixed threshold affects storage, never query truth."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Summary:
    count: int = 0
    total: float = 0.0
    minimum: float | None = None
    maximum: float | None = None

    @property
    def mean(self):
        return self.total / self.count if self.count else None


def summary(points):
    values = [p[4] for p in points]
    return Summary(
        len(values),
        math.fsum(values),
        min(values) if values else None,
        max(values) if values else None,
    )


def inside(point, bounds):
    return all(lo <= v < hi for v, (lo, hi) in zip(point, bounds))


def child_code(point, middle):
    return sum(
        (value >= mid) << axis for axis, (value, mid) in enumerate(zip(point, middle))
    )


def validate_bounds(bounds):
    if len(bounds) != 4 or any(
        len(b) != 2 or not all(math.isfinite(v) for v in b) or b[0] >= b[1]
        for b in bounds
    ):
        raise ValueError("four finite nonempty half-open bounds required")


class AdaptiveTree:
    def __init__(
        self,
        points,
        bounds=((0.0, 1.0),) * 4,
        capacity=16,
        max_depth=12,
        _depth=0,
        variance_threshold=0.0,
    ):
        validate_bounds(bounds)
        if capacity < 1 or max_depth < 0:
            raise ValueError("invalid tree limits")
        points = list(points)
        if any(
            len(p) != 5
            or not all(math.isfinite(v) for v in p)
            or not inside(p[:4], bounds)
            for p in points
        ):
            raise ValueError("invalid or out-of-domain observation")
        if not math.isfinite(variance_threshold) or variance_threshold < 0:
            raise ValueError("nonnegative variance threshold required")
        self.variance_threshold = variance_threshold
        self.bounds = tuple(bounds)
        self.aggregate = summary(points)
        self.children = {}
        self.points = points
        middle = [lo + (hi - lo) / 2 for lo, hi in bounds]
        mean = self.aggregate.mean
        scale = max((abs(p[4]) for p in points), default=0.0)
        # Compare standard deviations to avoid squaring large finite values.
        deviation = (math.sqrt(math.fsum((p[4] / scale - mean / scale) ** 2 for p in points) / len(points)) * scale) if scale else 0.0

        if (
            deviation <= math.sqrt(variance_threshold)
            or len(points) <= capacity
            or _depth >= max_depth
            or len({tuple(p[:4]) for p in points}) <= 1
            or any(not lo < mid < hi for (lo, hi), mid in zip(bounds, middle))
        ):
            return
        groups = {}
        for point in points:
            groups.setdefault(child_code(point, middle), []).append(point)
        for code, group in groups.items():
            child_bounds = tuple(
                (mid, hi) if code & (1 << axis) else (lo, mid)
                for axis, ((lo, hi), mid) in enumerate(zip(bounds, middle))
            )
            self.children[code] = AdaptiveTree(
                group, child_bounds, capacity, max_depth, _depth + 1, variance_threshold
            )
        self.points = []

    def query(self, bounds):
        validate_bounds(bounds)
        if any(
            hi <= qlo or qhi <= lo for (lo, hi), (qlo, qhi) in zip(self.bounds, bounds)
        ):
            return Summary()
        if all(
            qlo <= lo and hi <= qhi for (lo, hi), (qlo, qhi) in zip(self.bounds, bounds)
        ):
            return self.aggregate
        if not self.children:
            return summary(p for p in self.points if inside(p[:4], bounds))
        parts = [child.query(bounds) for child in self.children.values()]
        nonempty = [p for p in parts if p.count]
        return Summary(
            sum(p.count for p in parts),
            math.fsum(p.total for p in parts),
            min((p.minimum for p in nonempty), default=None),
            max((p.maximum for p in nonempty), default=None),
        )


def benchmark(seed=1729, count=1000):
    import random, time

    rng = random.Random(seed)
    report = {}
    queries = [
        tuple((0.0, 0.5) if i % 2 == 0 else (0.2, 0.8) for _ in range(4))
        for i in range(100)
    ]
    for distribution in ["uniform", "clustered", "identical"]:
        points = [
            tuple(
                rng.random()
                if distribution == "uniform"
                else 0.5
                if distribution == "identical"
                else min(0.999, max(0.0, rng.gauss(0.5, 0.05)))
                for _ in range(4)
            )
            + (rng.random(),)
            for _ in range(count)
        ]
        start = time.perf_counter()
        tree = AdaptiveTree(points, variance_threshold=0.05)
        build = time.perf_counter() - start
        start = time.perf_counter()
        a = [tree.query(q) for q in queries]
        tree_seconds = time.perf_counter() - start
        start = time.perf_counter()
        b = [summary(p for p in points if inside(p[:4], q)) for q in queries]
        scan_seconds = time.perf_counter() - start
        assert all(
            x.count == y.count and math.isclose(x.total, y.total, abs_tol=1e-10)
            for x, y in zip(a, b)
        )
        saving = (scan_seconds - tree_seconds) / len(queries)
        report[distribution] = dict(
            count=count,
            queries=len(queries),
            build_seconds=build,
            tree_seconds=tree_seconds,
            scan_seconds=scan_seconds,
            break_even_queries=math.ceil(build / saving) if saving > 0 else None,
        )
    return report


if __name__ == "__main__":
    import json

    print(json.dumps(benchmark(), indent=2))
