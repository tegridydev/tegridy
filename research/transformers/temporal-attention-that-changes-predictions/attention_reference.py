"""Age-biased attention over already computed scalar content scores."""
import math
import unittest


def attention(scores, event_times, arrivals, query_time, decay=1.0, scale=10.0):
    if not (len(scores) == len(event_times) == len(arrivals)):
        raise ValueError('parallel records must have equal length')
    values = list(scores) + list(event_times) + list(arrivals) + [query_time, decay, scale]
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
        raise ValueError('finite numbers required')
    if scale <= 0 or decay < 0:
        raise ValueError('positive time scale and nonnegative decay required')
    eligible = [i for i, (t, a) in enumerate(zip(event_times, arrivals)) if t <= query_time and a <= query_time]
    if not eligible:
        return None
    logits = {i: scores[i] - decay * ((query_time - event_times[i]) / scale) for i in eligible}
    if not all(math.isfinite(v) for v in logits.values()):
        raise ValueError('age penalty overflow')
    peak = max(logits.values())
    exp = {i: math.exp(v - peak) for i, v in logits.items()}
    total = math.fsum(exp.values())
    return [exp.get(i, 0.0) / total for i in range(len(scores))]


class AttentionTests(unittest.TestCase):
    def test_worked_example(self):
        w = attention([0, 0], [10, 0], [10, 0], 10)
        self.assertAlmostEqual(w[0], 0.7310585786300049)
        self.assertAlmostEqual(sum(w), 1)
        self.assertEqual(attention([0, 0], [10, 0], [10, 0], 10, decay=0), [0.5, 0.5])

    def test_common_age_shift_cancels(self):
        fresh = attention([0, 0], [10, 0], [10, 0], 10)
        older = attention([0, 0], [10, 0], [10, 0], 100)
        for a, b in zip(fresh, older):
            self.assertAlmostEqual(a, b)

    def test_mask_and_empty(self):
        self.assertEqual(attention([0, 100, 100], [0, 11, 0], [0, 11, 12], 10), [1, 0, 0])
        self.assertIsNone(attention([0], [0], [12], 10))
        self.assertIsNone(attention([], [], [], 10))
        with self.assertRaises(ValueError):
            attention([0], [0], [0], 1, scale=0)


if __name__ == '__main__':
    unittest.main()
