from __future__ import annotations

import enum
import math
import typing

from pyutils.geometry.cart2d import Point2d
from pyutils.geometry.exceptions import ImmutableInstanceError


class Orientation(enum.Enum):
    """ Two orientations:
        * ``A``: The x-axis points to the right and the y-axis points to the top right (60-deg. angle to x-axis)
        * ``B``: Orientation ``A`` with a 30-degree rotation counter-clockwise
    """
    A = 0
    B = 1


_cos_30_deg = math.cos(30 * math.pi/180)


T = typing.TypeVar('T', int, float)


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


class HexPoint( _HexCoords[T], typing.Generic[T]):
    """ Point using hex coordinates """
    def __add__(self, other: HexVec[T]) -> HexPoint[T]:
        return HexPoint(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: HexPoint[T]) -> HexVec[T]:
        return HexVec(self.x - other.x, self.y - other.y, self.z - other.z)

    def to_cart2d(self, orientation: Orientation = Orientation.A) -> Point2d[float]:
        match orientation:
            case Orientation.A:
                return Point2d(self.x + 0.5 * self.y, _cos_30_deg * self.y)
            case Orientation.B:
                return Point2d(_cos_30_deg * self.x, self.y + 0.5 * self.x)


class HexVec(typing.Generic[T], _HexCoords[T]):
    """ The difference between two HexPoints """

    def __abs__(self) -> float:
        # convert to cartesian
        x = self.x + 0.5 * self.y
        y = _cos_30_deg * self.y
        return math.sqrt(x*x + y*y)

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
        return HexVec(other * self.x, other*self.y, other*self.z)
