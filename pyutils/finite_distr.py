""" Small library for finite probability distributions.

Finite probability distributions can easily be represented as a dictionary
(e.g. ``{"dog": 0.75, "cat": 0.25}``).
This module introduces the :class:`FiniteDistr` class, which extends
dictionaries with various useful methods for dealing with probabilities.

Example:
    >>> random.seed(0)  # for reproducibility
    >>> p = FiniteDistr({'dog': 0.75, 'cat': 0.25})
    >>> # there are all kinds of useful methods
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
    pyutils.finite_distr.InvalidDistributionException: The probabilities do not sum up to 1
 """
import math
import random
from collections import Counter
from typing import TypeVar, Generic, Optional, Iterable, Type

__all__ = ['InvalidDistributionException', 'EmptyDistributionException', 'FiniteDistr']


class InvalidDistributionException(Exception):
    """ The distribution is not a valid probability distribution. """


class EmptyDistributionException(InvalidDistributionException):
    """ An operation is not permitted because the distribution is empty. """


class BadArgumentException(Exception):
    """ An argument does not meet the method's excpections. """


T = TypeVar('T')


class FiniteDistr(Generic[T], dict[T, float]):
    """ A finite probability distribution, based on Python dictionaries (see module description for examples). """

    @classmethod
    def uniform_over(cls, elements: Iterable[T]) -> 'FiniteDistr[T]':
        """ Creates a uniform distribution over ``elements``.

        Example:
            >>> FiniteDistr.uniform_over('abcd')
            {'a': 0.25, 'b': 0.25, 'c': 0.25, 'd': 0.25}

        Args:
            elements: Elements of the distribution (should not be repeated)

        Returns:
            The distribution.
        """
        if not hasattr(elements, '__len__'):   # we need to know the length for efficient normalization
            elements = list(elements)
        if not elements:
            raise EmptyDistributionException('Cannot generate a uniform distribution over the empty set.')
        number = len(elements)  # type: ignore
        prob = 1.0/number
        distr = cls({element: prob for element in elements})
        if len(distr.keys()) != number:
            raise BadArgumentException('Some elements occurred multiple times.')
        return distr

    @classmethod
    def from_counter(cls, counter: Counter[T]) -> 'FiniteDistr[T]':
        """ Creates a distribution from a counter.

        Example:
            >>> import collections
            >>> counter = collections.Counter(['dog', 'cat', 'dog', 'dog'])
            >>> p = FiniteDistr.from_counter(counter)
            >>> p
            {'dog': 0.75, 'cat': 0.25}

        Args:
            counter: A counter.

        Returns:
            The distribution.
        """
        distr = cls(counter)
        distr.normalize()
        return distr

    def sample(self, n: Optional[int] = None) -> T | list[T]:
        """ Sample from the distribution

        Args:
            n: Number of samples.

        Returns:
            An individual sample if n is ``None``, otherwise a list of samples.
        """
        population, weights = zip(*self.items())
        if n is None:
            return random.choices(population, weights, k=1)[0]
        else:
            return random.choices(population, weights, k=n)

    def normalize(self):
        """ Normalizes the probability distribution (i.e. makes the probabilities sum up to 1
        by multiplying them with a factor). """
        if not self:
            raise EmptyDistributionException('Cannot normalize an empty distribution')
        a = sum(self.values())
        for key in self:
            self[key] /= a

    def verify(self, tolerance: float = 1e-10):
        """ Raises an exception if the distribution is not valid.

        Concretely, it verifies that:
            1. the distribution is non-empty,
            2. the probabilities are non-negative,
            3. the probabilities sum up to 1 (up to the specified `tolerance`).
        This tends to be useful for debugging.

        Args:
            tolerance: Allowed difference between the summed up probabilities and 1.0 (to allow for rounding errors)

        Raises:
            EmptyDistributionException: If the distribution is empty.
            InvalidDistributionException: If the distribution is invalid.
        """
        if not self:
            raise EmptyDistributionException('The distribution is empty')
        if any(val < 0.0 for val in self.values()):
            raise InvalidDistributionException('Distribution has negative probabilities')
        if abs(sum(self.values()) - 1.0) > tolerance:
            raise InvalidDistributionException('The probabilities do not sum up to 1')

    def remove_zeros(self, tolerance: float = 0.0):
        """ Removes entries with a 0 probability.

        Args:
            tolerance: Every probability less than or equal to ``tolerance`` will be considered 0.
        """
        for key, val in self.items():
            if val <= tolerance:
                del self[key]

    def most_likely(self) -> T:
        """ Returns the entry with the highest probability.

        Returns:
            Entry with the highest probability.
        """
        return max(self, key=self.__getitem__)

    def get_or_zero(self, entry: T) -> float:
        """ Returns the probability `entry` (`0.0` if it is not in the distribution).

        Note:
            This could have been implemented using `collections.defaultdict(float)`.
            However, it might have the unintended side effect of adding entries.

        Args:
            entry: The entry you want the probability of.

        Returns:
            The probability.
        """
        if entry in self:
            return self[entry]
        return 0.0

    def entropy(self) -> float:
        """ Computes the information entropy of the distribution.

        Returns:
            The entropy in bits.
        """
        return -sum(p * math.log2(p) for p in self.values() if p > 0.0)
