"""Two-bit ternary symbol reference. Shape and scale must be stored separately."""
import itertools
import unittest

ENCODE = {0: 0, -1: 1, 1: 2}
DECODE = {v: k for k, v in ENCODE.items()}


def pack(values):
    out = bytearray((len(values) + 3) // 4)
    for i, value in enumerate(values):
        if type(value) is not int or value not in ENCODE:
            raise ValueError('expected -1, 0 or 1')
        out[i // 4] |= ENCODE[value] << (2 * (i % 4))
    return bytes(out)


def unpack(data, count):
    if type(count) is not int or count < 0 or len(data) != (count + 3) // 4:
        raise ValueError('incompatible count and payload')
    result = []
    for i in range(len(data) * 4):
        code = (data[i // 4] >> (2 * (i % 4))) & 3
        if i >= count:
            if code != 0:
                raise ValueError('nonzero padding')
        elif code not in DECODE:
            raise ValueError('reserved symbol')
        else:
            result.append(DECODE[code])
    return result


class PackingTests(unittest.TestCase):
    def test_all_short_sequences(self):
        for length in range(6):
            for values in itertools.product((-1, 0, 1), repeat=length):
                self.assertEqual(unpack(pack(values), length), list(values))

    def test_corruption(self):
        for data, count in [(b'\x03', 1), (b'\x04', 1), (b'', 1)]:
            with self.assertRaises(ValueError):
                unpack(data, count)
        with self.assertRaises(ValueError):
            pack([True])


if __name__ == '__main__':
    unittest.main()
