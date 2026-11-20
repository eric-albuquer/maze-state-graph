from src.map.map import Map
from src.map.map_nodes import (
    MapDotFloor,
    MapEnd,
    MapKey,
    MapPort,
    MapStart,
    MapWall,
    MapWater,
)
from src.solver.dijkstra_solver import solve_dijkstra
from src.solver.solver_common import adj_states


def make_map(rows: list[str]) -> Map:
    tile_types = {
        "#": MapWall,
        ".": MapDotFloor,
        "~": MapWater,
    }
    matrix = []
    start = None
    end = None

    for y, row in enumerate(rows):
        tile_row = []
        for x, symbol in enumerate(row):
            if symbol == "S":
                tile = MapStart(x, y)
                start = (x, y)
            elif symbol == "G":
                tile = MapEnd(x, y)
                end = (x, y)
            elif symbol == "a":
                tile = MapKey(x, y, symbol)
            elif symbol == "A":
                tile = MapPort(x, y, symbol)
            else:
                tile = tile_types[symbol](x, y)
            tile_row.append(tile)
        matrix.append(tile_row)

    assert start is not None
    assert end is not None
    return Map(start, end, matrix)


def assert_valid_path(map: Map, path) -> None:
    assert path
    assert path[0].pos == map.start
    assert path[-1].pos == map.end

    for current, next_state in zip(path, path[1:]):
        assert next_state in adj_states(map, current)


def path_cost(map: Map, path) -> int:
    return sum(
        map.matrix[state.pos[1]][state.pos[0]].cost
        for state in path[1:]
    )


def test_dijkstra_finds_a_valid_path() -> None:
    map = make_map(
        [
            "#####",
            "#S..#",
            "###.#",
            "#..G#",
            "#####",
        ]
    )

    solution = solve_dijkstra(map)

    assert_valid_path(map, solution.path)


def test_dijkstra_returns_no_path_when_goal_is_unreachable() -> None:
    map = make_map(
        [
            "#####",
            "#S#G#",
            "#####",
        ]
    )

    solution = solve_dijkstra(map)

    assert solution.path == []


def test_dijkstra_finds_the_path_with_the_lowest_cost() -> None:
    map = make_map(
        [
            "########",
            "#S~...G#",
            "#......#",
            "########",
        ]
    )

    solution = solve_dijkstra(map)

    assert_valid_path(map, solution.path)
    assert path_cost(map, solution.path) == 7
    assert len(solution.path) == 8
    assert all(state.pos != (2, 1) for state in solution.path)


def test_dijkstra_tracks_key_states_to_pass_through_a_locked_door() -> None:
    map = make_map(
        [
            "#######",
            "#S.A.G#",
            "##a####",
            "#######",
        ]
    )

    solution = solve_dijkstra(map)
    states_at_same_position = [
        state for state in solution.path if state.pos == (2, 1)
    ]

    assert_valid_path(map, solution.path)
    assert len(states_at_same_position) == 2
    assert states_at_same_position[0].keys == frozenset()
    assert states_at_same_position[1].keys == frozenset({"a"})
    assert any(state.pos == (3, 1) and state.keys == frozenset({"a"}) for state in solution.path)
