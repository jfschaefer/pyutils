""" Library for 2-dimensional Euclidean geometry.

This file is part of the pyutils package (https://github.com/jfschaefer/pyutils/), which comes with the MIT License.
"""

from __future__ import annotations

import abc
import enum
import math

import random
import re
import typing

__all__ = ['ImmutableInstanceError', 'Point', 'Vec', 'Rect', 'Triangle', 'HexOrientation', 'HexPoint', 'HexVec']

T = typing.TypeVar('T', int, float)


################################################################################
# EXCEPTIONS AND ERRORS
################################################################################

class ImmutableInstanceError(AttributeError):
    """ The object cannot be modified - you should probably create a new instance instead.
    Many objects in this library are immutable to enable hashing. """


class EmptyShapeError(Exception):
    """ The shape is empty, which makes the intended action impossible """


################################################################################
# CARTESIAN COORDINATES
################################################################################

_cart2d_format_regex = re.compile(r'^(?P<lpar>[([<⟨{]?)(?P<sep>[,;] ?)(?P<rpar>[)\]>⟩}]?)(:(?P<compformat>.*))?$')


class _Cart2dCoords(typing.Generic[T]):
    __slots__ = ('x', 'y')
    __match_args__ = ('x', 'y')

    x: T
    y: T

    def __init__(self, x: T, y: T):
        object.__setattr__(self, 'x', x)
        object.__setattr__(self, 'y', y)

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__ and self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __setattr__(self, key, value):
        raise ImmutableInstanceError(f'{self.__class__.__name__} is immutable')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.x}, {self.y})'

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __format__(self, format_spec: str):
        if not format_spec:
            return str(self)
        match = _cart2d_format_regex.match(format_spec)
        if not match:
            raise ValueError(f'Invalid format specification {format_spec!r}')
        x = format(self.x, match.group('compformat') or '')
        y = format(self.y, match.group('compformat') or '')
        return f'{match.group("lpar")}{x}{match.group("sep")}{y}{match.group("rpar")}'

    def as_tuple(self) -> tuple[T, T]:
        return self.x, self.y


class Point(typing.Generic[T], _Cart2dCoords[T]):
    """ A point in a 2d cartesian coordinate system """

    @typing.overload
    def __add__(self, other: Vec[float]) -> Point[float]: ...

    @typing.overload
    def __add__(self, other: Vec[int]) -> Point[T]: ...

    def __add__(self, other) -> Point:
        match other:
            case Vec(x, y):
                return Point(self.x + x, self.y + y)
            case _:
                return NotImplemented

    def __sub__(self, other: Point[T]) -> Vec[T]:
        return Vec(self.x - other.x, self.y - other.y)


class Vec(typing.Generic[T], _Cart2dCoords[T]):
    """ A vector in a 2d cartesian coordinate system """

    def __neg__(self) -> Vec[T]:
        return Vec(-self.x, -self.y)

    def __abs__(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def __rmul__(self, other) -> Vec:
        return Vec(other * self.x, other * self.y)

    def norm_manhattan(self) -> T:
        return abs(self.x) + abs(self.y)


################################################################################
# SHAPES
################################################################################

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
    def from_points(cls, point1: Point[T],
                    point2: Point[T]) -> Rect[T]:
        return cls(min(point1.x, point2.x), min(point1.y, point2.y), max(point1.x, point2.x), max(point1.y, point2.y))

    def __contains__(self, point: Point[T]) -> bool:
        return self.x0 <= point.x <= self.x1 and self.y0 <= point.y <= self.y1

    def __iter__(self) -> typing.Iterator[Point[int]]:
        for x in range(math.ceil(self.x0), math.floor(self.x1 + 1)):
            for y in range(math.ceil(self.y0), math.floor(self.y1 + 1)):
                yield Point(x, y)

    def width(self) -> T:
        return self.x1 - self.x0

    def height(self) -> T:
        return self.y1 - self.y0

    def empty(self) -> bool:
        return self.x1 < self.x0 or self.y1 < self.y0

    def discr_sample(self) -> Point[int]:
        """ Returns a uniformly randomly selected element of self ∩ ZxZ """
        return Point(random.randint(math.ceil(self.x0), math.floor(self.x1)),
                     random.randint(math.ceil(self.y0), math.floor(self.y1)))

    def cont_sample(self) -> Point[float]:
        """ Returns a uniformly randomly selected element self """
        if self.empty():
            raise EmptyShapeError(f'Cannot sample from an empty {self.__class__.__name__}')
        return Point(random.random() * (self.x1 - self.x0) + self.x0,
                     random.random() * (self.y1 - self.y0) + self.y0, )


class Triangle(typing.Generic[T]):
    """ A triangle """
    __slots__ = ('a', 'b', 'c')
    a: Point[T]
    b: Point[T]
    c: Point[T]

    def __init__(self, a: Point[T], b: Point[T], c: Point[T]):
        object.__setattr__(self, 'a', a)
        object.__setattr__(self, 'b', b)
        object.__setattr__(self, 'c', c)

    def signed_area(self) -> float:
        a, b, c = self.a, self.b, self.c
        return 0.5 * ((c.x - a.x) * (c.y - b.y) + (c.y - a.y) * (b.x - c.x))

    def area(self) -> float:
        return abs(self.signed_area())

    def __add__(self, other) -> Triangle:
        return Triangle(self.a + other, self.b + other, self.c + other)

    def __radd__(self, other) -> Triangle:
        return Triangle(self.a + other, self.b + other, self.c + other)
    
    def __repr__(self) -> str:
        return f'Triangle({self.a!r}, {self.b!r}, {self.c!r})'

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b and self.c == other.c

################################################################################
# LINES
################################################################################

class LineSegment(typing.Generic[T]):
    """ An ordered line segment """
    __slots__ = ('a', 'b')
    a: Point[T]
    b: Point[T]

    def __init__(self, a: Point[T], b: Point[T]):
        object.__setattr__(self, 'a', a)
        object.__setattr__(self, 'b', b)

    def __eq__(self, other):
        """ Note that the line segment is ordered, i.e. (a, b) is different from the line segment (b, a) """
        return self.a == other.a and self.b == other.b and self.__class__ == other.__class__

    def __hash__(self):
        return hash((self.a, self.b))

    def get_point_at(self, frac: float) -> Point[float]:
        """ returns frac*a + (1-frac)*to """
        return self.a + (1 - frac) * (self.b - self.a)

    def cont_sample(self) -> Point[float]:
        return self.get_point_at(random.random())

    def length(self) -> float:
        return abs(self.b - self.a)


################################################################################
# HEXAGONAL COORDINATES
################################################################################

class HexOrientation(enum.Enum):
    """ Orientation of hexagonal coordinate system relative to a cartesian one. Two options:
        * ``A``: The x-axis points to the right and the y-axis points to the top right (60-deg. angle to x-axis)
        * ``B``: ``A`` rotated 30-degree counter-clockwise
    """
    A = 0
    B = 1


_cos_30_deg = math.cos(30 * math.pi / 180)


class _HexCoords(typing.Generic[T]):
    """ Hex coordinates (x, y, z) with the invariant x+y+z=0 """
    __slots__ = ('x', 'y', 'z')  # using slots=True for dataclass doesn't seem to play well with Generic
    x: T
    y: T
    z: T

    def __init__(self, x: T, y: T, z: T):
        object.__setattr__(self, 'x', x)
        object.__setattr__(self, 'y', y)
        object.__setattr__(self, 'z', z)

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z and self.__class__ == other.__class__

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __setattr__(self, key, value):
        raise ImmutableInstanceError(f'{self.__class__.__name__} is immutable')

    def is_valid(self, epsilon: float = 1e-12) -> bool:
        return abs(self.x + self.y + self.z) <= epsilon

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case ',':
                return f'{self.x},{self.y}'
            case ',,':
                return f'{self.x},{self.y},{self.y}'
            case '(,)':
                return f'({self.x},{self.y})'
            case _:
                raise Exception(f'Unsupported format {format_spec}')


class HexPoint(_HexCoords[T], typing.Generic[T]):
    """ Point using hex coordinates """

    def __add__(self, other: HexVec[T]) -> HexPoint[T]:
        return HexPoint(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: HexPoint[T]) -> HexVec[T]:
        return HexVec(self.x - other.x, self.y - other.y, self.z - other.z)

    def to_cart2d(self, orientation: HexOrientation = HexOrientation.A) -> Point[float]:
        match orientation:
            case HexOrientation.A:
                return Point(self.x + 0.5 * self.y, _cos_30_deg * self.y)
            case HexOrientation.B:
                return Point(_cos_30_deg * self.x, self.y + 0.5 * self.x)


class HexVec(typing.Generic[T], _HexCoords[T]):
    """ The difference between two HexPoints """

    def __abs__(self) -> float:
        # convert to cartesian
        x = self.x + 0.5 * self.y
        y = _cos_30_deg * self.y
        return math.sqrt(x * x + y * y)

    def __neg__(self) -> HexVec[T]:
        return HexVec(-self.x, -self.y, -self.z)

    def hex_norm(self) -> float:
        """ Something like the Manhattan norm for a hexagonal grid """
        return (abs(self.x) + abs(self.y) + abs(self.z)) / 2

    def rotated(self, n: int) -> HexVec[T]:
        """ The vector rotated n turns (60 degrees) counter-clockwise """
        if n < 0:
            # (-1)**(-1) = -1.0  while  (-1)**1 = -1
            f = (-1) ** (-n)
        else:
            f = (-1) ** n
        v = (f * self.x, f * self.y, f * self.z)
        return HexVec(v[n % 3], v[(n + 1) % 3], v[(n + 2) % 3])

    def __rmul__(self, other) -> HexVec:
        return HexVec(other * self.x, other * self.y, other * self.z)
