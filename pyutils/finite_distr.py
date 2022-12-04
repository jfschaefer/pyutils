""" Small library for finite probability distributions.

This file is part of the pyutils package (https://github.com/jfschaefer/pyutils/), which comes with the MIT License.

Finite probability distributions can easily be represented as a dictionary:
(e.g. ``{"dog": 0.75, "cat": 0.25}``).
This module introduces the :class:`FiniteDistr` class, which extends
dictionaries with various useful methods for dealing with probabilities.

Example:
    >>> random.seed(0)  # for reproducibility
    >>> p = FDistr({'dog': 0.75, 'cat': 0.25})
    >>> # there are all kinds of useful methods (some are shown here)
    >>> p.most_likely()
    'dog'
    >>> p.sample(8)
    ['cat', 'cat', 'dog', 'dog', 'dog', 'dog', 'cat', 'dog']
    >>> p.entropy()
    0.8112781244591328
    >>> # it's also still just a dictionary
    >>> p['cat']
    0.25
    >>> p['cat'] = 0.4
    >>> p.verify()      # check if the distribution is valid
    Traceback (most recent call last):
        ...
    pyutils.finite_distr.InvalidDistributionError: The probabilities do not sum up to 1
 """
from __future__ import annotations

import math
import random
from collections import Counter
from typing import TypeVar, Generic, Optional, Iterable, Hashable

__all__ = ['InvalidDistributionError', 'EmptyDistributionError', 'FDistr']


class InvalidDistributionError(Exception):
    """ The distribution is not a valid probability distribution. """


class EmptyDistributionError(InvalidDistributionError):
    """ An operation is not permitted because the distribution is empty. """


T = TypeVar('T', bound=Hashable)


class FDistr(Generic[T], dict[T, float]):
    """ A finite probability distribution, based on Python dictionaries.
    See the module description for an example.
    """

    @classmethod
    def uniform_over(cls, elements: Iterable[T]) -> FDistr[T]:
        """ Creates a uniform distribution over ``elements``.

            >>> FDistr.uniform_over('abcd')
            FDistr({'a': 0.25, 'b': 0.25, 'c': 0.25, 'd': 0.25})
        """
        if not hasattr(elements, '__len__'):   # we need to know the length for efficient normalization
            elements = list(elements)
        if not elements:
            raise EmptyDistributionError('Cannot generate a uniform distribution over the empty set.')
        number = len(elements)  # type: ignore
        prob = 1.0/number
        distr = cls({element: prob for element in elements})
        if len(distr.keys()) != number:
            raise Exception('Some elements occurred multiple times.')
        return distr

    @classmethod
    def from_counter(cls, counter: Counter[T]) -> FDistr[T]:
        """ Creates a distribution from a counter.

            >>> import collections
            >>> counter = collections.Counter([0, 1, 0, 0])
            >>> FDistr.from_counter(counter)
            FDistr({0: 0.75, 1: 0.25})
        """
        distr = cls(counter)
        distr.normalize()
        return distr

    def sample(self, n: Optional[int] = None) -> T | list[T]:
        """ Samples from the distribution.

        It returns and individual sample if ``n`` is ``None``, otherwise a list of samples.
        Note that (especially for large distributions) it is more efficient
        to generate many samples at once because of the preprocessing involved.

        >>> random.seed(1)    # for reproducibility
        >>> FDistr({0: 0.2, 1: 0.8}).sample(5)
        [0, 1, 1, 1, 1]
        """
        population, weights = zip(*self.items())
        if n is None:
            return random.choices(population, weights, k=1)[0]
        else:
            return random.choices(population, weights, k=n)

    def normalize(self):
        """ Normalizes the probability distribution (i.e. makes the probabilities sum up to 1
        by multiplying them with a factor).

        >>> p = FDistr({'a': 1, 'b': 3})
        >>> p.normalize()
        >>> p
        FDistr({'a': 0.25, 'b': 0.75})
        """
        if not self:
            raise EmptyDistributionError('Cannot normalize an empty distribution')
        a = sum(self.values())
        for key in self:
            self[key] /= a

    def verify(self, tolerance: float = 1e-10):
        """ Raises an exception if the distribution is not valid.

        This tends to be useful for debugging. Concretely, it verifies that:
            1. the distribution is non-empty,
            2. the probabilities are non-negative,
            3. the probabilities sum up to 1 (up to the specified ``tolerance`` to allow for rounding errors).

        If the distribution is not valid, it raises one of the following exceptions:
            * :class:`EmptyDistributionError`: If the distribution is empty.
            * :class:`InvalidDistributionError`: If the distribution is invalid.


        >>> FDistr({'x': 0.6, 'y': 0.5}).verify()
        Traceback (most recent call last):
            ...
        pyutils.finite_distr.InvalidDistributionError: The probabilities do not sum up to 1
        """
        if not self:
            raise EmptyDistributionError('The distribution is empty')
        if any(val < 0.0 for val in self.values()):
            raise InvalidDistributionError('Distribution has negative probabilities')
        if abs(sum(self.values()) - 1.0) > tolerance:
            raise InvalidDistributionError('The probabilities do not sum up to 1')

    def remove_zeros(self, tolerance: float = 0.0):
        """ Removes entries with a 0 probability.

        Every probability less than or equal to ``tolerance`` will be considered 0.

        >>> p = FDistr({0: 0.9, 1: 0.1, 2: 0.0})
        >>> p.remove_zeros()
        >>> p
        FDistr({0: 0.9, 1: 0.1})
        """
        to_remove = [key for key, val in self.items() if val <= tolerance]
        for entry in to_remove:
            del self[entry]

    def most_likely(self) -> T:
        """ Returns the entry with the highest probability.

        >>> FDistr({'cats': 0.2, 'dogs': 0.8}).most_likely()
        'dogs'
        """
        return max(self, key=self.__getitem__)

    def get_or_zero(self, entry: T) -> float:
        """ Returns the probability ``entry`` (``0.0`` if it is not in the distribution).

        >>> FDistr({'cats': 0.2, 'dogs': 0.8}).get_or_zero('cats')
        0.2
        >>> FDistr({'cats': 0.2, 'dogs': 0.8}).get_or_zero('parrots')
        0.0

        Note:
            This could have been implemented using `collections.defaultdict(float)`.
            However, it might have the unintended side effect of adding entries.
        """
        if entry in self:
            return self[entry]
        return 0.0

    def entropy(self) -> float:
        """ Computes the information entropy of the distribution (in bits).

        >>> FDistr({0: 0.1, 1: 0.9}).entropy()
        0.4689955935892812
        """
        return -sum(p * math.log2(p) for p in self.values() if p > 0.0)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({dict.__repr__(self)})'
