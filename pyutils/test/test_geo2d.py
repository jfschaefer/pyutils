import unittest

from pyutils.geo2d import Point, HexVec, HexPoint


class TestIntervals(unittest.TestCase):
    def test_cart2d_format(self):
        p = Point(2.1, -3.2)
        self.assertEqual(f'{p:<; >:.03f}', '<2.100; -3.200>')
        self.assertEqual(f'{p:,}', '2.1,-3.2')
        self.assertEqual(repr(p), 'Point(2.1, -3.2)')
        self.assertEqual(str(p), '(2.1, -3.2)')
        self.assertEqual(str(p), format(p, ''))

    def test_hex(self):
        v = HexVec(2, 3, -5)
        self.assertEqual(2*v, HexVec(4, 6, -10))
        # points and vectors should be different
        self.assertNotEqual(2*v, HexPoint(4, 6, -10))
        self.assertEqual(v.hex_norm(), 5)
