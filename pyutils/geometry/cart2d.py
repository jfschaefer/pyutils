"""
Classes for 2-dimensional cartesian geometry.
"""

from __future__ import annotations

import math

import random
import typing

from pyutils.geometry.exceptions import ImmutableInstanceError

T = typing.TypeVar('T', int, float)


class _Cart2dCoords(typing.Generic[T]):
    __slots__ = ('x', 'y')  # using slots=True for dataclass doesn't seem to play well with Generic
    x: T
    y: T

    def __init__(self, x: T, y: T):
        object.__setattr__(self, 'x', x)
        object.__setattr__(self, 'y', y)

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y and self.__class__ == other.__class

    def __hash__(self):
        return hash((self.x, self.y))

    def __setattr__(self, key, value):
        raise ImmutableInstanceError(f'{self.__class__.__name__} is immutable')


class Point2d(typing.Generic[T], _Cart2dCoords[T]):
    """ A point in a 2d cartesian coordinate system """

    def __add__(self, other: Vec2d[T]) -> Point2d[T]:
        return Point2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point2d[T]) -> Vec2d[T]:
        return Vec2d(self.x - other.x, self.y - other.y)


class Vec2d(typing.Generic[T], _Cart2dCoords[T]):
    """ A vector in a 2d cartesian coordinate system """

    def __neg__(self) -> Vec2d[T]:
        return Vec2d(-self.x, -self.y)

    def __abs__(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def __rmul__(self, other) -> Vec2d:
        return Vec2d(other*self.x, other*self.y)

    def norm_manhattan(self) -> T:
        return abs(self.x) + abs(self.y)


class Rect(typing.Generic[T]):
    """ The rectangle [x0, x1] x [y0, y1] in a cartesian coordinate system """
    __slots__ = ('x0', 'y0', 'x1', 'y1')
    x0: T
    y0: T
    x1: T
    y1: T

    def __init__(self, x0: T, y0: T, x1: T, y1: T):
        object.__setattr__(self, 'x0', x0)
        object.__setattr__(self, 'y0', y0)
        object.__setattr__(self, 'x1', x1)
        object.__setattr__(self, 'y1', y1)

    def __eq__(self, other) -> bool:
        return self.x0 == other.x0 and self.y0 == other.y0 and self.x1 == other.x1 and self.y1 == other.y1 and \
               self.__class__ == other.__class

    def __hash__(self):
        return hash((self.x0, self.y0, self.x1, self.y1))

    @classmethod
    def from_points(cls, point1: Point2d[T],
                    point2: Point2d[T]) -> Rect[T]:
        return cls(min(point1.x, point2.x), min(point1.y, point2.y), max(point1.x, point2.x), max(point1.y, point2.y))

    def __contains__(self, point: Point2d[T]) -> bool:
        return self.x0 <= point.x <= self.x1 and self.y0 <= point.y <= self.y1

    def __iter__(self) -> typing.Iterator[Point2d[int]]:
        for x in range(math.ceil(self.x0), math.floor(self.x1 + 1)):
            for y in range(math.ceil(self.y0), math.floor(self.y1 + 1)):
                yield Point2d(x, y)

    @property
    def width(self) -> T:
        return self.x1 - self.x0

    @property
    def height(self) -> T:
        return self.y1 - self.y0

    @property
    def empty(self) -> bool:
        return self.x1 < self.x0 or self.y1 < self.y0

    def discr_sample(self) -> Point2d[int]:
        """ Returns a uniformly randomly selected element of self ∩ ZxZ """
        return Point2d(random.randint(math.ceil(self.x0), math.floor(self.x1)),
                       random.randint(math.ceil(self.y0), math.floor(self.y1)))

    def cont_sample(self) -> Point2d[float]:
        """ Returns a uniformly randomly selected element self """
        assert not self.empty
        return Point2d(random.random() * (self.x1 - self.x0) + self.x0,
                       random.random() * (self.y1 - self.y0) + self.y0, )


class LineSegment(typing.Generic[T]):
    """ An ordered line segment """
    __slots__ = ('a', 'b')
    a: Point2d[T]
    b: Point2d[T]

    def __init__(self, a: Point2d[T], b: Point2d[T]):
        object.__setattr__(self, 'a', a)
        object.__setattr__(self, 'b', b)

    def __eq__(self, other):
        """ Note that the line segment is ordered, i.e. (a, b) is different from the line segment (b, a) """
        return self.a == other.a and self.b == other.b and self.__class__ == other.__class__

    def __hash__(self):
        return hash((self.a, self.b))

    def get_point_at(self, frac: float) -> Point2d[float]:
        """ returns frac*a + (1-frac)*to """
        return self.a + (1-frac) * (self.b-self.a)

    def cont_sample(self) -> Point2d[float]:
        return self.get_point_at(random.random())
