"""Deterministic pair generator and exact scorer for the article's protocol.
Run normally for tests; --emit prints JSON to stdout without writing files.
"""
from collections import defaultdict, Counter
import json
import random
import sys
import unittest

ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'zero ten twenty thirty forty fifty sixty seventy eighty ninety'.split()


def english(n):
    if type(n) is not int or not 0 <= n <= 99:
        raise ValueError('operand must be an integer in [0, 99]')
    if n < 20:
        return ONES[n]
    return TENS[n // 10] + ('-' + ONES[n % 10] if n % 10 else '')


def exact_answer(response, target):
    if type(target) is not int or not 0 <= target <= 198:
        raise ValueError('invalid target')
    return isinstance(response, str) and response.strip() == str(target)


def pairs(seed=1729):
    rng = random.Random(seed)
    strata = defaultdict(list)
    for a in range(100):
        for b in range(a, 100):
            strata[(a % 10 + b % 10 >= 10, len(str(a + b)))].append((a, b))
    keys = sorted(strata)
    sizes = {k: len(strata[k]) * 600 // 5050 for k in keys}
    remainder = 600 - sum(sizes.values())
    ranked = sorted(keys, key=lambda k: (-(len(strata[k]) * 600 % 5050), k))
    for k in ranked[:remainder]:
        sizes[k] += 1
    rows = []
    splits = ('development', 'discovery', 'final')
    for k in keys:
        selected = rng.sample(strata[k], sizes[k])
        for a, b in selected:
            split = splits[len(rows) % 3]
            prompts = []
            for x, y in sorted({(a, b), (b, a)}):
                prompts.extend([
                    f'Calculate {x} + {y}. Answer with digits only:',
                    f'Calculate {english(x)} plus {english(y)}. Answer with digits only:',
                ])
            rows.append(dict(a=a, b=b, carry=k[0], answer_digits=k[1], split=split,
                             target=str(a+b), prompts=prompts))
    return rows


class ProtocolTests(unittest.TestCase):
    def test_scoring(self):
        for text, valid in [('45', True), (' 45\n', True), ('045', False),
                            ('The answer is 45', False), ('45 or 46', False), ('', False)]:
            self.assertEqual(exact_answer(text, 45), valid)

    def test_pairs(self):
        rows = pairs()
        self.assertEqual(rows, pairs())
        self.assertEqual(len({(x['a'], x['b']) for x in rows}), 600)
        self.assertEqual(Counter(x['split'] for x in rows), {'development': 200, 'discovery': 200, 'final': 200})
        for x in rows:
            self.assertEqual(x['target'], str(x['a'] + x['b']))
            self.assertEqual(len(x['prompts']), 2 if x['a'] == x['b'] else 4)
        self.assertEqual(english(0), 'zero')
        self.assertEqual(english(99), 'ninety-nine')


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit']:
        print(json.dumps(pairs(), indent=2))
    else:
        unittest.main()
