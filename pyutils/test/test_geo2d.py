import pickle
import unittest

from pyutils.geo2d import Point, HexVec, HexPoint, Triangle, Vec, Cartesianable, Rect


class TestIntervals(unittest.TestCase):
    def test_cart2d_format(self):
        p = Point(2.1, -3.2)
        self.assertEqual(f'{p:<; >:.03f}', '<2.100; -3.200>')
        self.assertEqual(f'{p:,}', '2.1,-3.2')
        self.assertEqual(repr(p), 'Point(2.1, -3.2)')
        self.assertEqual(str(p), '(2.1, -3.2)')
        self.assertEqual(str(p), format(p, ''))

    def test_cartesianable(self):
        p = HexVec(1, -1, 0)
        match p:
            case Cartesianable():
                pass
            case _:
                self.assertFalse('Failed to match Cartesianable')

    def test_hex(self):
        v = HexVec(2, 3, -5)
        self.assertEqual(2 * v, HexVec(4, 6, -10))
        # points and vectors should be different
        self.assertNotEqual(2 * v, HexPoint(4, 6, -10))
        self.assertEqual(v.hex_norm(), 5)

    def test_hex_rotation(self):
        self.assertEqual(HexVec(3, -2).rotated(1), HexVec(2, 1))
        self.assertEqual(HexVec(3, -2).rotated(2), HexVec(-1, 3))
        self.assertEqual(HexVec(3, -2).rotated(3), -HexVec(3, -2))
        self.assertEqual(HexVec(3, -2).rotated(0), HexVec(3, -2))
        self.assertEqual(HexVec(3, -2).rotated(-1), HexVec(3, -2).rotated(5))

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

    def test_rect(self):
        rect = Rect(Point(3, 1), Point(1, 2))
        vec = Vec(-2, 5)
        self.assertEqual(rect.area(), 2)
        self.assertEqual(rect + vec, Rect(Point(1, 6), Point(-1, 7)))

    def test_pickle(self):
        point = Point(3, 1)
        data = pickle.dumps(point)
        point2 = pickle.loads(data)
        self.assertEqual(point, point2)
