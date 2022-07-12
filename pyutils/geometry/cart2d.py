"""
Classes for 2-dimensional cartesian geometry.
"""
import dataclasses
import math

import random
import typing

import pyutils.geometry.abstract as abstract

T = typing.TypeVar('T', int, float)


@dataclasses.dataclass(frozen=True)
class Point2d(typing.Generic[T], abstract.Point):
    """ The point (x, y) in a cartesian coordinate system """
    __slots__ = ('x', 'y')    # using slots=True for dataclass doesn't seem to play well with Generic
    x: T
    y: T

    def __add__(self, other: 'Vec2d[T]') -> 'Point2d[T]':
        return Point2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Point2d[T]') -> 'Vec2d[T]':
        return Vec2d(self.x - other.x, self.y - other.y)


@dataclasses.dataclass(frozen=True)
class Vec2d(typing.Generic[T], abstract.Vec[Point2d[T]]):
    """ The vector (x, y) in a cartesian coordinate system """
    __slots__ = ('x', 'y')
    x: T
    y: T

    def __neg__(self) -> 'Vec2d[T]':
        return Vec2d(-self.x, -self.y)

    def __abs__(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)


@dataclasses.dataclass(frozen=True)
class Rect(typing.Generic[T], abstract.Shape[Point2d[T]]):
    """ The rectangle [x0, x1] x [y0, y1] in a cartesian coordinate system """
    __slots__ = ('x', 'y')
    x0: T
    y0: T
    x1: T
    y1: T

    def __contains__(self, point: Point2d[T]) -> bool:
        return self.x0 <= point.x <= self.x1 and self.y0 <= point.y <= self.y1

    def __iter__(self) -> typing.Iterator[Point2d[T]]:
        for x in range(math.ceil(self.x0), math.floor(self.x1 + 1)):
            for y in range(math.ceil(self.y0), math.floor(self.y1 + 1)):
                yield Point2d(x, y)

    @property
    def width(self) -> T:
        return self.x1 - self.x0

    @property
    def height(self) -> T:
        return self.y1 - self.y0


class IntRect(Rect[int]):
    def sample(self) -> Point2d[int]:
        return Point2d(random.randint(self.x0, self.x1), random.randint(self.y0, self.y1))
