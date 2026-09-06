"""Rule baseline only. None represents MASK; separators and checksum stay intact."""
from collections import Counter
import unittest

POSITIONS = tuple(range(5)) + tuple(range(6, 11)) + tuple(range(12, 17))


def encode(values):
    if len(values) != 5 or any(type(v) is not int or not 0 <= v < 16 for v in values):
        raise ValueError('five integer values in [0,15] required')
    return list(values) + ['SEP'] + list(values) + ['SEP'] + list(values) + [sum(values) % 16]


def repair(record):
    if len(record) != 18 or record[5] != 'SEP' or record[11] != 'SEP':
        raise ValueError('invalid record layout')
    if type(record[17]) is not int or not 0 <= record[17] < 16:
        raise ValueError('invalid checksum')
    if any(record[i] is not None and (type(record[i]) is not int or not 0 <= record[i] < 16) for i in POSITIONS):
        raise ValueError('invalid data token')
    out = list(record)
    unresolved = []
    recovered = []
    for field in range(5):
        positions = (field, field + 6, field + 12)
        counts = Counter(record[i] for i in positions if record[i] is not None)
        winners = [value for value, n in counts.items() if n >= 2]
        if winners:
            value = winners[0]
            for i in positions:
                out[i] = value
            recovered.append(value)
        else:
            unresolved.append(field)
    checksum_ok = None if unresolved else sum(recovered) % 16 == record[17]
    return out, unresolved, checksum_ok


class RepairTests(unittest.TestCase):
    def test_clean_and_mask(self):
        clean = encode([2, 5, 1, 3, 4])
        self.assertEqual(repair(clean), (clean, [], True))
        damaged = list(clean); damaged[0] = None
        self.assertEqual(repair(damaged), (clean, [], True))

    def test_ambiguity_and_checksum(self):
        damaged = encode([2, 5, 1, 3, 4]); damaged[0] = 6; damaged[6] = 7
        out, unresolved, checksum = repair(damaged)
        self.assertEqual(out, damaged)
        self.assertEqual(unresolved, [0])
        self.assertIsNone(checksum)
        damaged = encode([2, 5, 1, 3, 4]); damaged[17] = 0
        self.assertFalse(repair(damaged)[2])
        damaged = encode([2, 5, 1, 3, 4]); damaged[0] = damaged[6] = None
        self.assertEqual(repair(damaged)[1], [0])


if __name__ == '__main__':
    unittest.main()
