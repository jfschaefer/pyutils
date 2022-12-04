import unittest

from pyutils.geo2d import Point, HexVec, HexPoint, Triangle, Vec


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

    def test_triangle_area(self):
        a, b, c = Point(1, 1), Point(2, 3), Point(6, -1)
        triangle = Triangle(a, b, c)
        signed_area = triangle.signed_area()
        self.assertEqual(signed_area, -6.0)
        area = triangle.area()
        self.assertEqual(area, 6.0)

    def test_translate_triangle(self):
        triangle = Triangle(Point(2, 1), Point(4, 0), Point(3, 1))
        self.assertEqual(triangle + Vec(1, -2), Triangle(Point(3, -1), Point(5, -2), Point(4, -1)))
        self.assertEqual(Vec(1, -2) + triangle, Triangle(Point(3, -1), Point(5, -2), Point(4, -1)))
