import pytest

from src.map.map import Map
from src.map.map_nodes import MapDotFloor, MapFloorDirected, MapWall
from src.map.map_state import MapState
from src.solver.solver_common import adj_states, adj_states_with_cost
# aproveitado o metodo adj

DIRECTION_BY_SYMBOL = {
    ">": (1, 0),
    "<": (-1, 0),
    "^": (0, -1),
    "v": (0, 1),
}

#Cada pyteste executa 4 vezes para testas todos os quatro sentidos de DIRECTIONS
#resultando em 12
DIRECTIONS = [
    pytest.param(">", (1, 0), id="right"),
    pytest.param("<", (-1, 0), id="left"),
    pytest.param("^", (0, -1), id="up"),
    pytest.param("v", (0, 1), id="down"),
]


def make_map_with_directed_floor(symbol: str) -> Map:
    direction = DIRECTION_BY_SYMBOL[symbol]
    matrix = [
        [MapWall(x, y) for x in range(5)]
        for y in range(5)
    ]

    for x, y in ((2, 1), (1, 2), (3, 2), (2, 3)):
        matrix[y][x] = MapDotFloor(x, y)
    matrix[2][2] = MapFloorDirected(2, 2, direction)

    return Map((2, 2), (3, 3), matrix)


@pytest.mark.parametrize(("symbol", "direction"), DIRECTIONS)
def test_directed_floor_allows_only_the_arrow_direction(
    symbol: str,
    direction: tuple[int, int],
) -> None:
    map = make_map_with_directed_floor(symbol)
    current = MapState((2, 2))
    expected = MapState((2 + direction[0], 2 + direction[1]))

    assert adj_states(map, current) == [expected]


@pytest.mark.parametrize(("symbol", "direction"), DIRECTIONS)
def test_weighted_adjacency_preserves_directed_floor_direction(
    symbol: str,
    direction: tuple[int, int],
) -> None:
    map = make_map_with_directed_floor(symbol)
    current = MapState((2, 2))
    expected = MapState((2 + direction[0], 2 + direction[1]))

    assert adj_states_with_cost(map, current) == [(expected, 1)]


@pytest.mark.parametrize(("symbol", "direction"), DIRECTIONS)
def test_directed_floor_can_be_entered_from_any_side(
    symbol: str,
    direction: tuple[int, int],
) -> None:
    map = make_map_with_directed_floor(symbol)
    opposite_neighbor = MapState((2 - direction[0], 2 - direction[1]))
    directed_state = MapState((2, 2))

    assert directed_state in adj_states(map, opposite_neighbor)
