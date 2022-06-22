import dataclasses
import enum
import itertools
from typing import Optional, Iterable, Iterator


class Bound(enum.Enum):
    OPEN = 1
    CLOSED = 2


@dataclasses.dataclass(frozen=True, slots=True)
class Interval:
    lower_bound_type: Bound
    lower_bound: float
    upper_bound: float
    upper_bound_type: Bound

    def __contains__(self, element: float) -> bool:
        if self.lower_bound <= element <= self.upper_bound:
            return ((self.lower_bound_type == Bound.CLOSED or self.lower_bound < element) and
                    (self.upper_bound_type == Bound.CLOSED or element < self.upper_bound))
        return False

    def contains(self, element: float, margin: Optional[float] = None):
        """ The margin ε can set to allow room for rounding errors.
            For example, instead of element ∈ [a, b), it would check element ∈ [a-ε, b-ε)
            and instead of element ∈ (a, b), it would check element ∈ (a+ε, b-ε). """
        if margin is None:
            return element in self
        else:
            return element in self.relaxed_interval(margin)

    def relaxed_interval(self, amount: float) -> 'Interval':
        """ Returns the interval "relaxed" by a certain amount (ε).
            This is supposed to allow some room for rounding errors.
            Concretely, intervals will be relaxed in the following way:
                (a, b) ↦ (a+ε, b-ε)
                (a, b] ↦ (a+ε, b+ε]
                [a, b) ↦ [a-ε, b-ε)
                [a, b] ↦ [a-ε, b+ε]
        """
        lower = self.lower_bound + {Bound.OPEN: amount, Bound.CLOSED: -amount}[self.lower_bound_type]
        upper = self.upper_bound + {Bound.OPEN: -amount, Bound.CLOSED: amount}[self.upper_bound_type]
        return Interval(self.lower_bound_type, lower, upper, self.upper_bound_type)

    @property
    def length(self) -> float:
        """ Technically, the measure of the interval """
        return max(self.upper_bound - self.lower_bound, 0)

    @property
    def is_empty(self) -> bool:
        return self.lower_bound > self.upper_bound or\
               ((self.upper_bound_type == Bound.OPEN or self.lower_bound_type == Bound.OPEN) and
                self.lower_bound == self.upper_bound)

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

    # Simplified constructors
    @classmethod
    def open(cls, lower: float, upper: float) -> 'Interval':
        return Interval(Bound.OPEN, lower, upper, Bound.OPEN)

    @classmethod
    def closed(cls, lower: float, upper: float) -> 'Interval':
        return Interval(Bound.CLOSED, lower, upper, Bound.CLOSED)

    @classmethod
    def open_closed(cls, lower: float, upper: float) -> 'Interval':
        return Interval(Bound.OPEN, lower, upper, Bound.CLOSED)

    @classmethod
    def closed_open(cls, lower: float, upper: float) -> 'Interval':
        return Interval(Bound.CLOSED, lower, upper, Bound.OPEN)
