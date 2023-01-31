import unittest
from fractions import Fraction

from pyutils.angles import FracRadians, Degrees


class TestIntervals(unittest.TestCase):
    def test_frac_radians(self):
        f = FracRadians(Fraction(3, 2))
        self.assertEqual(f + f, FracRadians(Fraction(3, 1)))
        self.assertEqual(f + 2 * f, FracRadians(Fraction(9, 2)))
        self.assertEqual(f, Degrees(270))
