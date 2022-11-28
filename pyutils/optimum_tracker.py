import abc
import math
import typing

_T = typing.TypeVar('_T')


class OptimumTracker(typing.Generic[_T], abc.ABC):
    best: typing.Optional[_T]
    evaluation: float

    @abc.abstractmethod
    def update(self, candidate: _T, evaluation: float) -> bool:
        raise NotImplementedError()

    def nongreedy_update(self, candidate: _T, evaluation: float) -> bool:
        """ The update method is greedy (mostly to ensure that `best` is set as soon as possible).
            nongreedy_update instead keeps the currently best candidate if the evaluation is the same. """
        if evaluation != self.evaluation:
            return self.update(candidate, evaluation)
        return False


class MinimumTracker(typing.Generic[_T], OptimumTracker[_T]):
    def __init__(self):
        self.best = None
        self.evaluation = math.inf

    def update(self, candidate: _T, evaluation: float) -> bool:
        if evaluation <= self.evaluation:
            self.best = candidate
            self.evaluation = evaluation
            return True
        return False


class MaximumTracker(typing.Generic[_T], OptimumTracker[_T]):
    def __init__(self):
        self.best = None
        self.evaluation = -math.inf

    def update(self, candidate: _T, evaluation: float) -> bool:
        if evaluation >= self.evaluation:
            self.best = candidate
            self.evaluation = evaluation
            return True
        return False
