import unittest

from pyutils.intervals import Interval, Bound


class TestIntervals(unittest.TestCase):
    def test_is_empty(self):
        self.assertTrue(Interval.open(5, 3).is_empty)
        self.assertTrue(Interval.closed(5, 3).is_empty)
        self.assertTrue(Interval.open(5, 5).is_empty)
        self.assertTrue(Interval.closed_open(5, 5).is_empty)
        self.assertFalse(Interval.open(3, 5).is_empty)
        self.assertFalse(Interval.closed(3, 5).is_empty)
        self.assertFalse(Interval.closed(5, 5).is_empty)

    def test_membership(self):
        interval = Interval.closed_open(3, 5)
        self.assertTrue(3 in interval)
        self.assertTrue(4 in interval)
        self.assertFalse(5 in interval)

        relaxed = interval.relaxed_interval(0.1)
        self.assertTrue(2.99 in relaxed)
        self.assertTrue(4.0 in relaxed)
        self.assertFalse(4.99 in relaxed)

    def assert_split_result(self, got: list[Interval], expected: list[Interval]):
        self.assertEqual(len(got), len(expected))
        for a, b in zip(got, expected):
            self.assertEqual(a, b)

    def test_split(self):
        interval = Interval.open_closed(-4, 12)
        self.assert_split_result(list(interval.split([])), [interval])
        self.assert_split_result(list(interval.split([5], upper_bounds=Bound.CLOSED, lower_bounds=Bound.OPEN)),
                                 [Interval.open_closed(-4, 5), Interval.open_closed(5, 12)])
        self.assert_split_result(list(interval.split([5, 7], upper_bounds=Bound.CLOSED, lower_bounds=Bound.OPEN)),
                                 [Interval.open_closed(-4, 5), Interval.open_closed(5, 7), Interval.open_closed(7, 12)])


if __name__ == '__main__':
    unittest.main()
