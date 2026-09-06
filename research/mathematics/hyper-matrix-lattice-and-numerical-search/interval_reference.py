"""Exact half-open interval search; validate the immutable array once at build."""
from bisect import bisect_left
import math
import random
import unittest


def finite_number(value):
    return type(value) in (float, int) and math.isfinite(value)


class SortedIndex:
    def __init__(self, values):
        self.values = tuple(values)
        if not all(finite_number(v) for v in self.values):
            raise ValueError('finite numbers required')
        if any(a > b for a, b in zip(self.values, self.values[1:])):
            raise ValueError('array must be sorted')

    def bounds(self, lo, hi):
        if not finite_number(lo) or not finite_number(hi) or lo > hi:
            raise ValueError('invalid half-open interval')
        return bisect_left(self.values, lo), bisect_left(self.values, hi)


class IntervalTests(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(SortedIndex([1, 2, 2, 4]).bounds(2, 4), (1, 3))
        self.assertEqual(SortedIndex([]).bounds(0, 1), (0, 0))
        self.assertEqual(SortedIndex([1]).bounds(1, 1), (0, 0))
        with self.assertRaises(ValueError):
            SortedIndex([2, 1])
        with self.assertRaises(ValueError):
            SortedIndex([1]).bounds(2, 1)

    def test_scan_oracle(self):
        rng = random.Random(1729)
        index = SortedIndex(sorted(rng.randrange(-20, 21) for _ in range(500)))
        for _ in range(200):
            lo, hi = sorted([rng.randrange(-25, 26), rng.randrange(-25, 26)])
            left, right = index.bounds(lo, hi)
            expected = [i for i, v in enumerate(index.values) if lo <= v < hi]
            self.assertEqual(list(range(left, right)), expected)


if __name__ == '__main__':
    unittest.main()
