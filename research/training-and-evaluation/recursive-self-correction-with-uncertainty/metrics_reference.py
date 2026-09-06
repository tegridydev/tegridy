"""Evaluation arithmetic only; this module does not generate or revise answers."""
from collections import Counter
import math
import unittest


def revision_metrics(before, after):
    if len(before) != len(after) or any(type(x) is not bool for x in list(before) + list(after)):
        raise ValueError('aligned Boolean correctness labels required')
    counts = Counter(zip(before, after))
    repaired, damaged = counts[(False, True)], counts[(True, False)]
    wrong, correct = before.count(False), before.count(True)
    return {'repaired': repaired, 'damaged': damaged,
            'net_accuracy_change': (repaired - damaged) / len(before) if before else None,
            'repair_rate': repaired / wrong if wrong else None,
            'damage_rate': damaged / correct if correct else None}


def selective_risk(correct, confidence, threshold):
    if len(correct) != len(confidence) or any(type(x) is not bool for x in correct):
        raise ValueError('aligned correctness labels required')
    if any(type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1 for p in list(confidence) + [threshold]):
        raise ValueError('probabilities must lie in [0,1]')
    selected = [label for label, p in zip(correct, confidence) if p >= threshold]
    return {'coverage': len(selected) / len(correct) if correct else None,
            'risk': selected.count(False) / len(selected) if selected else None}


class MetricTests(unittest.TestCase):
    def test_repair_and_damage(self):
        result = revision_metrics([False, True, False, True], [True, False, True, True])
        self.assertEqual(result, {'repaired': 2, 'damaged': 1, 'net_accuracy_change': 0.25,
                                  'repair_rate': 1, 'damage_rate': 0.5})
        self.assertIsNone(revision_metrics([], [])['net_accuracy_change'])

    def test_selective(self):
        self.assertEqual(selective_risk([True, False], [0.9, 0.2], 0.5), {'coverage': 0.5, 'risk': 0})
        self.assertEqual(selective_risk([True], [0.1], 0.8), {'coverage': 0, 'risk': None})


if __name__ == '__main__':
    unittest.main()
