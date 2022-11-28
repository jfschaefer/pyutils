import unittest

from pyutils.geometry.hex2d import HexVec, HexPoint


class TestIntervals(unittest.TestCase):
    def test_hex(self):
        v = HexVec(2, 3, -5)
        self.assertEqual(2*v, HexVec(4, 6, -10))
        # points and vectors should be different
        self.assertNotEqual(2*v, HexPoint(4, 6, -10))
        self.assertEqual(v.hex_norm(), 5)
