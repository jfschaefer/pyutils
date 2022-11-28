from collections import defaultdict
from typing import TypeVar, Iterable, Callable, Any

T = TypeVar('T')
Key = TypeVar('Key')


def partition(elements: Iterable[T], key: Callable[[T], Key]) -> Iterable[tuple[Key, list[T]]]:
    d = defaultdict(list)
    for element in elements:
        d[key(element)].append(element)
    return iter(d.items())


# TODO: Do by explicitly provided relation (would be less efficient)
