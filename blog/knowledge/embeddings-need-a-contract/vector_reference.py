"""Small standard-library reference for vector validation and signed cosine."""
import math
import unittest


def validate(vector, dimension):
    if not isinstance(vector, (list, tuple)) or len(vector) != dimension or dimension < 1:
        raise ValueError("vector shape mismatch")
    if any(type(v) not in (float, int) or not math.isfinite(v) for v in vector):
        raise ValueError("coordinates must be finite numbers, excluding booleans")
    norm = math.hypot(*vector)
    if not norm or not math.isfinite(norm):
        raise ValueError("cosine requires a finite nonzero norm")
    return tuple(v / norm for v in vector)


def cosine(query, document, query_manifest, document_manifest):
    if not query_manifest or query_manifest != document_manifest:
        raise ValueError("incompatible representation manifests")
    q = validate(query, len(query))
    d = validate(document, len(q))
    return max(-1.0, min(1.0, math.fsum(a * b for a, b in zip(q, d))))


class VectorTests(unittest.TestCase):
    def test_signed_geometry(self):
        for target, expected in [([2, 0], 1), ([0, 1], 0), ([-1, 0], -1)]:
            self.assertAlmostEqual(cosine([1, 0], target, 'recipe-v1', 'recipe-v1'), expected)

    def test_bad_inputs(self):
        for v in [[], [0, 0], [True, 1], [float('nan'), 1], [float('inf'), 0], [[1], 0], [1]]:
            with self.assertRaises(ValueError):
                cosine([1, 0], v, 'v1', 'v1')
        with self.assertRaises(ValueError):
            cosine([1, 0], [1, 0], 'v1', 'v2')


if __name__ == '__main__':
    unittest.main()
