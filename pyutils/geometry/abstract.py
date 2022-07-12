import abc
import typing


class Point(abc.ABC):
    @abc.abstractmethod
    def __add__(self, other) -> 'Point':   # TODO: switch to typing.Self in python 3.11, especially for other
        raise NotImplemented

    @abc.abstractmethod
    def __sub__(self, other) -> 'Vec':
        raise NotImplemented


P = typing.TypeVar('P', bound=Point)


class Vec(typing.Generic[P], abc.ABC):
    @abc.abstractmethod
    def __neg__(self) -> 'Vec':
        raise NotImplemented

    @abc.abstractmethod
    def __abs__(self) -> float:
        raise NotImplemented


class Shape(typing.Generic[P], abc.ABC):
    @abc.abstractmethod
    def __contains__(self, point: P) -> bool:
        raise NotImplemented

    def sample(self) -> P:
        # return a point of the shape picked uniformly random
        raise NotImplemented

    def __iter__(self) -> typing.Iterator[P]:
        raise NotImplemented
