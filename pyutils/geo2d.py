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
from fractions import Fraction

from .angles import Angle, as_angle, Degrees

__all__ = ['ImmutableInstanceError', 'EmptyShapeError', 'Point', 'Vec', 'Rect', 'Triangle', 'HexOrientation',
           'HexPoint', 'HexVec', 'Polygon']

T = typing.TypeVar('T', int, float, Fraction)


################################################################################
# EXCEPTIONS AND ERRORS
################################################################################

class ImmutableInstanceError(AttributeError):
    """ The object cannot be modified - you should probably create a new instance instead.
    Many objects in this library are immutable to enable hashing. """


class _ImmutableMixin:
    __slots__: tuple[str, ...]

    def __setattr__(self, key, value):
        if key in self.__slots__ and not hasattr(self, key):
            object.__setattr__(self, key, value)
        else:
            raise ImmutableInstanceError(f'{self.__class__.__name__} is immutable')


class EmptyShapeError(Exception):
    """ The shape is empty, which makes the intended action impossible """


################################################################################
# CARTESIAN COORDINATES
################################################################################


class Cartesianable(abc.ABC):
    """ An object can be converted to cartesian coordinates via a .to_cart() method.

    It should not be implemented for representations that already use cartesian coordinates
    to enable the following pattern without enforcing a particular order of the cases:
        def process(vector):
            match vector:
                case Cartesianable():
                    return process(vector.to_cart())
                case Vec(x, y):
                    ...
    """

    @abc.abstractmethod
    def to_cart(self) -> _Cart2dCoords:
        ...

    @classmethod
    def __subclasshook__(cls, class_):
        if cls is Cartesianable:
            if any('to_cart' in c.__dict__ for c in class_.__mro__):
                return True
        return NotImplemented


_cart2d_format_regex = re.compile(r'^(?P<lpar>[([<⟨{]?)(?P<sep>[,;] ?)(?P<rpar>[)\]>⟩}]?)(:(?P<compformat>.*))?$')


class _Cart2dCoords(typing.Generic[T], _ImmutableMixin):
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

    def __deepcopy__(self, memodict={}):
        return self.__class__(self.x, self.y)


class Point(typing.Generic[T], _Cart2dCoords[T]):
    """ A point in a 2d cartesian coordinate system """

    @typing.overload
    def __add__(self, other: Vec[float] | PolarVec) -> Point[float]:
        ...

    @typing.overload
    def __add__(self, other: Vec[int]) -> Point[T]:
        ...

    def __add__(self, other) -> Point:
        if isinstance(other, Cartesianable):
            other = other.to_cart()
        if isinstance(other, Vec):
            return Point(self.x + other.x, self.y + other.y)
        return NotImplemented

    @typing.overload
    def __sub__(self, other: Vec[float] | Point[float]) -> Vec[float]:
        ...

    @typing.overload
    def __sub__(self, other: Vec[int] | Point[int]) -> Vec[T]:
        ...

    @typing.overload
    def __sub__(self: Point[Fraction], other: Point[Fraction] | Vec[Fraction] | Point[int] | Vec[int]) -> Vec[Fraction]:
        ...

    def __sub__(self, other) -> Vec:
        if isinstance(other, Cartesianable):
            other = other.to_cart()
        if isinstance(other, Vec) or isinstance(other, Point):
            return Vec(self.x - other.x, self.y - other.y)
        return NotImplemented


class Vec(typing.Generic[T], _Cart2dCoords[T]):
    """ A vector in a 2d cartesian coordinate system """

    def __neg__(self) -> Vec[T]:
        return Vec(-self.x, -self.y)

    def __abs__(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    @typing.overload
    def __rmul__(self, other: int) -> Vec[T]:
        ...

    @typing.overload
    def __rmul__(self, other: float) -> Vec[float]:
        ...

    def __rmul__(self, other) -> Vec:
        return Vec(other * self.x, other * self.y)

    def norm_manhattan(self) -> T:
        return abs(self.x) + abs(self.y)

    @typing.overload
    def __add__(self, other: Vec[float]) -> Vec[float]:
        ...

    @typing.overload
    def __add__(self, other: Vec[int]) -> Vec[T]:
        ...

    @typing.overload
    def __add__(self, other: Point[float]) -> Point[float]:
        ...

    @typing.overload
    def __add__(self, other: Point[int]) -> Point[T]:
        ...

    def __add__(self, other):
        if isinstance(other, Vec):
            return Vec(self.x + other.x, self.y + other.y)
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        return NotImplemented


################################################################################
# POLAR COORDINATES
################################################################################


class PolarVec(Cartesianable, _ImmutableMixin):
    __slots__ = ('r', 'phi')
    r: float
    phi: Angle

    def __init__(self, r: float, phi: float | Angle):
        object.__setattr__(self, 'r', r)
        object.__setattr__(self, 'phi', as_angle(phi))

    def to_cart(self) -> Vec:
        return Vec(self.r * self.phi.cos(), self.r * self.phi.sin())

    def rotated(self, angle: float | Angle) -> PolarVec:
        return PolarVec(self.r, self.phi + as_angle(angle))

    def __add__(self, other):
        return self.to_cart() + other

    def __repr__(self):
        return f'{self.__class__.__name__}({self.r}, {self.phi})'


################################################################################
# SHAPES
################################################################################

class Rect(typing.Generic[T], _ImmutableMixin):
    __slots__ = ('a', 'b')
    a: Point[T]  # bottom left
    b: Point[T]  # top right

    def __init__(self, p1: Point[T], p2: Point[T]):
        a = Point(x=min(p1.x, p2.x), y=min(p1.y, p2.y))
        b = Point(x=max(p1.x, p2.x), y=max(p1.y, p2.y))
        object.__setattr__(self, 'a', a)
        object.__setattr__(self, 'b', b)

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__ and self.a == other.a and self.b == other.b

    def __contains__(self, point) -> bool:
        return self.a.x <= point.x <= self.b.x and self.a.y <= point.y <= self.b.y

    def __iter__(self) -> typing.Iterator[Point[int]]:
        for x in range(math.ceil(self.a.x), math.floor(self.b.x + 1)):
            for y in range(math.ceil(self.a.y), math.floor(self.b.y + 1)):
                yield Point(x, y)

    def __hash__(self):
        return hash((self.a, self.b))

    def width(self) -> T:
        return self.b.x - self.a.x

    def height(self) -> T:
        return self.b.y - self.a.y

    def area(self) -> T:
        return self.width() * self.height()

    def __add__(self, other) -> Rect:
        return Rect(self.a + other, self.b + other)

    def __radd__(self, other):
        return Rect(self.a + other, self.b + other)

    def discr_sample(self) -> Point[int]:
        """ Returns a uniformly randomly selected point of self ∩ ZxZ """
        return Point(random.randint(math.ceil(self.a.x), math.floor(self.b.x)),
                     random.randint(math.ceil(self.a.y), math.floor(self.b.y)))

    def cont_sample(self) -> Point[float]:
        """ Returns a uniformly randomly selected element self """
        return Point(random.random() * (self.b.x - self.a.x) + self.a.x,
                     random.random() * (self.b.y - self.a.y) + self.a.y)


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


class Polygon(typing.Generic[T]):
    __slots__ = ('vertices',)
    vertices: tuple[Point[T], ...]

    def __init__(self, vertices: tuple[Point[T], ...]):
        object.__setattr__(self, 'vertices', vertices)

    @classmethod
    def regular(cls, number_of_vertices: int, circumradius: float = 1.0, center: Point = Point(0, 0),
                rotated: float | Angle = Degrees(0)) -> Polygon:
        # Notes:
        #  * circumradius may not be very convenient (consider supporting apothem and side length)
        #  * would it make sense to make a RegularPolygon subclass instead?
        rotated = as_angle(rotated)
        angle = Degrees(360 / number_of_vertices)
        return Polygon(tuple(center + PolarVec(circumradius, rotated + n * angle) for n in range(number_of_vertices)))

    def __add__(self, other) -> Polygon:
        return Polygon(tuple(v + other for v in self.vertices))


################################################################################
# LINES
################################################################################


class LineSegment(typing.Generic[T], _ImmutableMixin):
    """ An ordered line segment """
    __slots__ = ('a', 'b')
    a: Point[T]
    b: Point[T]

    def __init__(self, a: Point[T], b: Point[T]):
        object.__setattr__(self, 'a', a)
        object.__setattr__(self, 'b', b)

    def __eq__(self, other):
        """ Note that the line segment is ordered, i.e. (a, b) is different from the line segment (b, a) """
        return self.__class__ == other.__class__ and self.a == other.a and self.b == other.b

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
        * ``B``: Orientation ``A`` rotated 30-degree counter-clockwise
    """
    A = 0
    B = 1


_cos_30_deg = math.cos(30 * math.pi / 180)


class _HexCoords(typing.Generic[T], _ImmutableMixin):
    """ Hex coordinates (x, y, z) with the invariant x+y+z=0 """
    __slots__ = ('x', 'y', 'z')  # using slots=True for dataclass doesn't seem to play well with Generic
    x: T
    y: T
    z: T

    def __init__(self, x: T, y: T, z: typing.Optional[T] = None):
        object.__setattr__(self, 'x', x)
        object.__setattr__(self, 'y', y)
        object.__setattr__(self, 'z', -(x + y) if z is None else z)

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z and self.__class__ == other.__class__

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def is_valid(self, epsilon: float = 1e-12) -> bool:
        return abs(self.x + self.y + self.z) <= epsilon

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.x}, {self.y}, {self.z})'

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

    def __deepcopy__(self, memodict={}):
        return self.__class__(self.x, self.y, self.z)


class HexPoint(_HexCoords[T], typing.Generic[T], Cartesianable):
    """ Point using hex coordinates """

    def __add__(self, other: HexVec[T]) -> HexPoint[T]:
        return HexPoint(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: HexPoint[T]) -> HexVec[T]:
        return HexVec(self.x - other.x, self.y - other.y, self.z - other.z)

    def to_cart(self, orientation: HexOrientation = HexOrientation.A) -> Point[float]:
        match orientation:
            case HexOrientation.A:
                return Point(self.x + 0.5 * self.y, _cos_30_deg * self.y)
            case HexOrientation.B:
                return Point(_cos_30_deg * self.x, self.y + 0.5 * self.x)


class HexVec(typing.Generic[T], _HexCoords[T], Cartesianable):
    """ The difference between two HexPoints """

    def __abs__(self) -> float:
        # convert to cartesian
        x = self.x + 0.5 * self.y
        y = _cos_30_deg * self.y
        return math.sqrt(x * x + y * y)

    def __neg__(self) -> HexVec[T]:
        return HexVec(-self.x, -self.y, -self.z)

    @typing.overload
    def hex_norm(self: HexVec[Fraction]) -> Fraction:
        ...

    @typing.overload
    def hex_norm(self: HexVec[int] | HexVec[float]) -> Fraction:
        ...

    def hex_norm(self):
        """ Something like the Manhattan norm for a hexagonal grid """
        return (abs(self.x) + abs(self.y) + abs(self.z)) / 2

    def rotated(self, n: int) -> HexVec[T]:
        """ The vector rotated n turns (60 degrees) counter-clockwise """
        f = -1 if n % 2 else 1
        v = (f * self.x, f * self.y, f * self.z)
        return HexVec(v[n % 3], v[(n + 1) % 3], v[(n + 2) % 3])

    def __rmul__(self, other) -> HexVec:
        return HexVec(other * self.x, other * self.y, other * self.z)

    def to_cart(self, orientation: HexOrientation = HexOrientation.A) -> Vec[float]:
        match orientation:
            case HexOrientation.A:
                return Vec(self.x + 0.5 * self.y, _cos_30_deg * self.y)
            case HexOrientation.B:
                return Vec(_cos_30_deg * self.x, self.y + 0.5 * self.x)
