"""A 256-symbol byte unigram baseline; document controls are not modelled."""
from collections import Counter
import math
import unittest


def fit(documents, alpha=1.0):
    if type(alpha) not in (float, int) or not math.isfinite(alpha) or alpha <= 0:
        raise ValueError('positive finite smoothing required')
    counts = Counter()
    for document in documents:
        if not isinstance(document, bytes):
            raise TypeError('supply raw bytes')
        counts.update(document)
    total = sum(counts.values()) + 256 * alpha
    return tuple((counts[i] + alpha) / total for i in range(256))


def bits_per_byte(documents, probabilities):
    if len(probabilities) != 256 or any(not math.isfinite(p) or p <= 0 for p in probabilities):
        raise ValueError('256 positive finite probabilities required')
    if not math.isclose(sum(probabilities), 1.0):
        raise ValueError('probabilities must sum to one')
    losses = []
    for document in documents:
        if not isinstance(document, bytes):
            raise TypeError('supply raw bytes')
        losses.extend(-math.log2(probabilities[value]) for value in document)
    if not losses:
        raise ValueError('bits per byte undefined for empty evaluation')
    return math.fsum(losses) / len(losses)


class ByteTests(unittest.TestCase):
    def test_uniform_and_unicode(self):
        uniform = fit([])
        self.assertEqual(bits_per_byte([b'abc'], uniform), 8)
        text = 'café 🌱'; raw = text.encode('utf-8')
        self.assertEqual(raw.decode('utf-8'), text)
        self.assertGreater(len(raw), len(text))
        self.assertAlmostEqual(bits_per_byte([raw], uniform), 8)
        self.assertEqual(bits_per_byte([b'\xff'], uniform), 8)

    def test_training_and_empty(self):
        trained = fit([b'a' * 100])
        self.assertLess(bits_per_byte([b'aaa'], trained), 8)
        with self.assertRaises(ValueError):
            bits_per_byte([b''], trained)


if __name__ == '__main__':
    unittest.main()
