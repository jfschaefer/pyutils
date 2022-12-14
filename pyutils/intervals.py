""" Module for working with intervals.

Provides the :class:`Interval` class, which can be used to represented open and closed intervals.

Example:
    >>> i1 = Interval.closed(2, 4)
    >>> i1.length
    2
    >>> 3 in i1
    True
    >>> 12 in i1
    False

Example:
    >>> # There are different constructors for closed/open intervals:
    >>> Interval.open_closed(1, 3)
    Interval(1, 3]
    >>> 1 in Interval.open(1, 3)
    False
    >>> 1 in Interval.closed_open(1, 3)
    True
"""

from __future__ import annotations

import dataclasses
import enum
import itertools
import math
import random
import typing
from typing import Generic, Optional, Iterator


class Bound(enum.Enum):
    OPEN = 1
    CLOSED = 2


T = typing.TypeVar('T', int, float)


@dataclasses.dataclass(frozen=True)
class Interval(Generic[T]):
    lower_bound_type: Bound
    lower_bound: T
    upper_bound: T
    upper_bound_type: Bound

    def __contains__(self, x: float) -> bool:
        if self.lower_bound <= x <= self.upper_bound:
            return ((self.lower_bound_type == Bound.CLOSED or self.lower_bound < x) and
                    (self.upper_bound_type == Bound.CLOSED or x < self.upper_bound))
        return False

    def contains(self, x: float, margin: Optional[float] = None):
        """ The margin ε can set to allow room for rounding errors.
            For example, instead of x ∈ [a, b), it would check x ∈ [a-ε, b-ε)
            and instead of x ∈ (a, b), it would check x ∈ (a+ε, b-ε). """
        if margin is None:
            return x in self
        else:
            return x in self.relaxed_interval(margin)

    def relaxed_interval(self, amount: float) -> 'Interval':
        """ Returns the interval "relaxed" by a certain amount (ε).

            This is supposed to allow some room for rounding errors.
            Concretely, intervals will be relaxed in the following way:
                * (a, b) ↦ (a+ε, b-ε)
                * (a, b] ↦ (a+ε, b+ε]
                * [a, b) ↦ [a-ε, b-ε)
                * [a, b] ↦ [a-ε, b+ε]
        """
        lower = self.lower_bound + {Bound.OPEN: amount, Bound.CLOSED: -amount}[self.lower_bound_type]
        upper = self.upper_bound + {Bound.OPEN: -amount, Bound.CLOSED: amount}[self.upper_bound_type]
        return Interval(self.lower_bound_type, lower, upper, self.upper_bound_type)

    @property
    def length(self) -> T:
        """ Technically, the measure of the interval """
        return max(self.upper_bound - self.lower_bound, 0)

    @property
    def is_empty(self) -> bool:
        return self.lower_bound > self.upper_bound or \
            ((self.upper_bound_type == Bound.OPEN or self.lower_bound_type == Bound.OPEN) and
             self.lower_bound == self.upper_bound)

    def sample(self) -> float:
        assert self.lower_bound > -math.inf and self.upper_bound < math.inf
        assert not self.is_empty
        return random.random() * self.length + self.lower_bound

    def lowest_contained_int(self) -> Optional[int]:
        result = math.ceil(self.lower_bound)
        if result == self.lower_bound and self.lower_bound_type == Bound.OPEN:
            result += 1
        if result < self.upper_bound or result == self.upper_bound and self.upper_bound_type == Bound.CLOSED:
            return result
        else:  # interval contains no integers
            return None

    def highest_contained_int(self) -> Optional[int]:
        result = math.floor(self.upper_bound)
        if result == self.upper_bound and self.upper_bound_type == Bound.OPEN:
            result -= 1
        if result > self.lower_bound or result == self.lower_bound and self.lower_bound_type == Bound.CLOSED:
            return result
        else:  # interval contains no integers
            return None

    def int_sample(self) -> int:
        assert self.lower_bound > -math.inf and self.upper_bound < math.inf
        lower = self.lowest_contained_int()
        upper = self.highest_contained_int()
        assert lower is not None, 'Interval contains no integers'
        assert upper is not None
        return random.randint(lower, upper)

    def __lt__(self, other: typing.Union[float, 'Interval']):
        assert not self.is_empty  # TODO: should we return True in this case?
        if isinstance(other, Interval):
            assert not other.is_empty
            return self.upper_bound < other.lower_bound or self.upper_bound == other.lower_bound and \
                (self.upper_bound_type == Bound.OPEN or other.lower_bound_type == Bound.OPEN)
        return self.upper_bound < other or self.upper_bound == other and self.upper_bound_type == Bound.OPEN

    def __gt__(self, other: typing.Union[float, 'Interval']):
        assert not self.is_empty  # TODO: should we return True in this case?
        if isinstance(other, Interval):
            assert not other.is_empty
            return self.lower_bound > other.upper_bound or self.lower_bound == other.upper_bound and \
                (self.lower_bound_type == Bound.OPEN or other.upper_bound_type == Bound.OPEN)
        return self.lower_bound > other or self.lower_bound == other and self.lower_bound_type == Bound.OPEN

    def split(self, values: list[float], upper_bounds: Bound = Bound.OPEN, lower_bounds: Bound = Bound.CLOSED) -> \
            Iterator['Interval']:
        """ Splits an interval into multiple intervals.
        For example, splitting [a, b] at the values x and y would result in the intervals [a, x), [x, y), [y, b]. """
        if len(values) == 0:
            yield self
        else:
            yield Interval(self.lower_bound_type, self.lower_bound, values[0], upper_bounds)
            for lower, upper in itertools.pairwise(values):
                yield Interval(lower_bounds, lower, upper, upper_bounds)
            yield Interval(lower_bounds, values[-1], self.upper_bound, self.upper_bound_type)

    def __str__(self) -> str:
        return (
                {Bound.OPEN: '(', Bound.CLOSED: '['}[self.lower_bound_type] +
                str(self.lower_bound) + ', ' + str(self.upper_bound) +
                {Bound.OPEN: ')', Bound.CLOSED: ']'}[self.upper_bound_type]
        )

    def __repr__(self) -> str:
        return f'Interval{str(self)}'

    # Simplified constructors
    @classmethod
    def open(cls, lower: T, upper: T) -> Interval[T]:
        return Interval(Bound.OPEN, lower, upper, Bound.OPEN)

    @classmethod
    def closed(cls, lower: T, upper: T) -> Interval[T]:
        return Interval(Bound.CLOSED, lower, upper, Bound.CLOSED)

    @classmethod
    def open_closed(cls, lower: T, upper: T) -> Interval[T]:
        return Interval(Bound.OPEN, lower, upper, Bound.CLOSED)

    @classmethod
    def closed_open(cls, lower: T, upper: T) -> Interval[T]:
        return Interval(Bound.CLOSED, lower, upper, Bound.OPEN)
