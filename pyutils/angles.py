from __future__ import annotations

import abc
import math
import typing
from fractions import Fraction


class UnsupportedOperation(Exception):
    ...


class Angle(abc.ABC):
    @abc.abstractmethod
    def to_radians(self) -> Radians: ...

    @abc.abstractmethod
    def to_degrees(self) -> Degrees: ...

    @property
    @abc.abstractmethod
    def value(self) -> int | float | Fraction: ...

    @abc.abstractmethod
    def __abs__(self) -> Angle: ...

    @abc.abstractmethod
    def __add__(self, other) -> Angle: ...

    @abc.abstractmethod
    def __radd__(self, other) -> Angle: ...

    @abc.abstractmethod
    def __mul__(self, other) -> Angle: ...

    @abc.abstractmethod
    def __rmul__(self, other) -> Angle: ...

    @abc.abstractmethod
    def __eq__(self, other) -> bool: ...

    @abc.abstractmethod
    def __le__(self, other) -> bool: ...

    @abc.abstractmethod
    def __lt__(self, other) -> bool: ...

    @abc.abstractmethod
    def __ge__(self, other) -> bool: ...

    @abc.abstractmethod
    def __gt__(self, other) -> bool: ...

    @abc.abstractmethod
    def __hash__(self): ...


_T = typing.TypeVar('_T', int, float, Fraction)


class Degrees(Angle, typing.Generic[_T]):
    __slots__ = ('_v',)
    __matchargs__ = __slots__
    _v: _T

    def __init__(self, value: _T | Angle):
        if isinstance(value, Angle):
            self._v = value.to_degrees().value
        else:
            self._v = value

    @property
    def value(self) -> _T:
        return self._v

    def to_degrees(self) -> Degrees:
        return self

    def __abs__(self) -> Degrees[_T]:
        return Degrees(abs(self._v))

    def __add__(self, other) -> Degrees:
        return Degrees(self._v + Degrees(other).value)

    def __radd__(self, other) -> Degrees:
        return Degrees(self._v + Degrees(other).value)

    def __mul__(self, other) -> Degrees:
        if isinstance(other, Angle):
            raise ValueError('Multiplying two angles is not supported.')
        return Degrees(self._v * other)

    def __rmul__(self, other) -> Degrees:
        if isinstance(other, Angle):
            raise ValueError('Multiplying two angles is not supported.')
        return Degrees(self._v * other)

    def __eq__(self, other) -> bool:
        return self._v == Degrees(other).value

    def __le__(self, other) -> bool:
        return self._v <= Degrees(other).value

    def __lt__(self, other) -> bool:
        return self._v < Degrees(other).value

    def __ge__(self, other) -> bool:
        return self._v >= Degrees(other).value

    def __gt__(self, other) -> bool:
        return self._v > Degrees(other).value

    def __hash__(self):
        return hash(self._v)

    def to_radians(self) -> Radians:
        if isinstance(self._v, int) or isinstance(self._v, Fraction):
            return FracRadians(Fraction(self._v, 180))
        else:
            return FloatRadians(self._v / 180 * math.pi)


class Radians(Angle, abc.ABC):
    def to_radians(self) -> Radians:
        return self

    def __new__(cls, angle) -> Radians:
        # TODO: This is really annoying and results in weird code...
        if isinstance(angle, Angle):
            return angle.to_radians()
        return FloatRadians(angle)

    def __hash__(self):
        return hash(self.to_degrees())


class FloatRadians(Radians):
    __slots__ = ('_v',)
    __matchargs__ = __slots__
    _v: float

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)   # "un-overwrite" it

    def __init__(self, value: float):
        if hasattr(self, '_v'):   # the whole Radians.__new__ really messes things up...
            return
        self._v = value

    @property
    def value(self) -> float:
        return self._v

    def to_degrees(self) -> Degrees:
        return Degrees(self._v/math.pi * 180)

    def __abs__(self) -> FloatRadians:
        return FloatRadians(abs(self._v))

    def __add__(self, other) -> FloatRadians:
        return FloatRadians(self._v + Radians(other).value)

    def __radd__(self, other) -> FloatRadians:
        return FloatRadians(self._v + Radians(other).value)

    def __mul__(self, other) -> FloatRadians:
        if isinstance(other, Angle):
            raise ValueError('Multiplying two angles is not supported.')
        return FloatRadians(self._v * other)

    def __rmul__(self, other) -> FloatRadians:
        if isinstance(other, Angle):
            raise ValueError('Multiplying two angles is not supported.')
        return FloatRadians(self._v * other)

    def __eq__(self, other) -> bool:
        return self._v == Radians(other).value

    def __le__(self, other) -> bool:
        return self._v <= Radians(other).value

    def __lt__(self, other) -> bool:
        return self._v < Radians(other).value

    def __ge__(self, other) -> bool:
        return self._v >= Radians(other).value

    def __gt__(self, other) -> bool:
        return self._v > Radians(other).value

    def __hash__(self):
        return hash(self._v)


class FracRadians(Radians):
    __slots__ = ('_f',)
    __matchargs__ = __slots__
    _f: Fraction

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)   # "un-overwrite" it

    def __init__(self, factor: Fraction):
        if hasattr(self, '_f'):
            return
        self._f = factor

    def __str__(self) -> str:
        return f'{self._f}π'

    @property
    def value(self) -> float:
        return self._f * math.pi

    def __abs__(self) -> FracRadians:
        return FracRadians(abs(self._f))

    def __add__(self, other) -> Radians:
        other = Radians(other)
        if isinstance(other, FracRadians):
            return FracRadians(self._f + other._f)
        return FloatRadians(self.value + other.value)

    def __radd__(self, other) -> Radians:
        other = Radians(other)
        if isinstance(other, FracRadians):
            return FracRadians(self._f + other._f)
        return FloatRadians(self.value + other.value)

    def __mul__(self, other) -> Radians:
        if isinstance(other, Angle):
            raise ValueError('Multiplying two angles is not supported.')
        if isinstance(factor := self._f * other, Fraction):
            return FracRadians(factor)
        else:
            return FloatRadians(self.value * other)

    def __rmul__(self, other) -> Radians:
        if isinstance(other, Angle):
            raise ValueError('Multiplying two angles is not supported.')
        if isinstance(factor := self._f * other, Fraction):
            return FracRadians(factor)
        else:
            return FloatRadians(self.value * other)

    def __eq__(self, other) -> bool:
        r = Radians(other)
        return self._f == r._f if isinstance(r, FracRadians) else self.value == r.value

    def __le__(self, other) -> bool:
        r = Radians(other)
        return self._f <= r._f if isinstance(r, FracRadians) else self.value <= r.value

    def __lt__(self, other) -> bool:
        r = Radians(other)
        return self._f < r._f if isinstance(r, FracRadians) else self.value < r.value

    def __ge__(self, other) -> bool:
        r = Radians(other)
        return self._f >= r._f if isinstance(r, FracRadians) else self.value >= r.value

    def __gt__(self, other) -> bool:
        r = Radians(other)
        return self._f > r._f if isinstance(r, FracRadians) else self.value > r.value

    def to_degrees(self) -> Degrees:
        deg = self._f * 180
        if deg.denominator == 1:
            return Degrees(int(deg))
        return Degrees(deg)
