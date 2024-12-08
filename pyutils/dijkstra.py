import itertools
from abc import abstractmethod
from collections.abc import Hashable
from heapq import heappop, heappush
from typing import TypeVar, Callable, Iterable, Optional, Protocol


class CostType(Protocol):
    @abstractmethod
    def __add__(self, other: 'CostType') -> 'CostType': ...

    @abstractmethod
    def __lt__(self, other: 'CostType') -> bool: ...


_NodeType = TypeVar('_NodeType', bound=Hashable)
_EdgeType = TypeVar('_EdgeType')
_CostType = TypeVar('_CostType', bound=CostType)


def dijkstra(
        start: _NodeType,
        get_edges: Callable[
            [_NodeType],
            Iterable[tuple[_NodeType, _CostType, _EdgeType]]
        ],
        is_goal: Callable[[_NodeType], bool],
        start_cost: _CostType = 0,  # type: ignore
) -> Optional[tuple[list[_NodeType], _CostType, list[tuple[_NodeType, _CostType, _EdgeType, _NodeType]]]]:
    predecessor: dict[_NodeType, tuple[_NodeType, _CostType, _EdgeType]] = {}
    queue: list[tuple[_CostType, _NodeType]] = [(start_cost, start)]

    # Afaik, here is no simple approach to updating items in a priority queue in python.
    # Instead, we will simply make new entries whenever we find an improvement.
    # `irrelevant_nodes` will keep track of nodes that have already been processed.
    # If a node shows up again in the fringe, it must be outdated and can safely be ignored.
    irrelevant_nodes: set[_NodeType] = set()

    goal: Optional[_NodeType] = None
    goal_cost: Optional[_CostType] = None
    found_goal = False

    while queue:
        cost, node = heappop(queue)
        if is_goal(node):
            goal = node
            goal_cost = cost
            found_goal = True
            break
        if node in irrelevant_nodes:
            continue
        irrelevant_nodes.add(node)

        for neighbor, edge_cost, edge in get_edges(node):
            new_cost = cost + edge_cost
            if neighbor not in predecessor or new_cost < predecessor[neighbor][1]:
                predecessor[neighbor] = (node, edge_cost, edge)
                heappush(queue, (new_cost, neighbor))

    if not found_goal:
        return None

    # reconstruct path
    path = []
    n = goal
    assert goal_cost is not None
    while n != start:
        p, c, e = predecessor[n]
        path.append((p, c, e, n))
        n = p
    path.reverse()

    return (
        list(itertools.chain((start,), (n for _, _, _, n in path))),
        goal_cost,
        path,
    )
