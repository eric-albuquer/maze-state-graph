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
from src.solver.bfs_solver import solve_bfs
from src.solver.solver_common import adj_states


def make_map(rows: list[str]) -> Map:
    tile_types = {
        "#": MapWall,
        ".": MapDotFloor,
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
            elif symbol == "~":
                tile = MapWater(x, y)
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


def test_bfs_finds_a_valid_path() -> None:
    map = make_map(
        [
            "#####",
            "#S..#",
            "###.#",
            "#..G#",
            "#####",
        ]
    )

    solution = solve_bfs(map)

    assert_valid_path(map, solution.path)


def test_bfs_returns_no_path_when_goal_is_unreachable() -> None:
    map = make_map(
        [
            "#####",
            "#S#G#",
            "#####",
        ]
    )

    solution = solve_bfs(map)

    assert solution.path == []


def test_bfs_returns_a_path_with_the_fewest_steps() -> None:
    map = make_map(
        [
            "#######",
            "#S...G#",
            "#.....#",
            "#######",
        ]
    )

    solution = solve_bfs(map)

    assert_valid_path(map, solution.path)
    assert len(solution.path) == 5


def test_bfs_tracks_key_states_to_pass_through_a_locked_door() -> None:
    map = make_map(
        [
            "#######",
            "#S.A.G#",
            "##a####",
            "#######",
        ]
    )

    solution = solve_bfs(map)
    states_at_same_position = [
        state for state in solution.path if state.pos == (2, 1)
    ]

    assert_valid_path(map, solution.path)
    assert len(states_at_same_position) == 2
    assert states_at_same_position[0].keys == frozenset()
    assert states_at_same_position[1].keys == frozenset({"a"})
    assert solution.path[-1].pos == map.end


def test_bfs_prefers_fewer_steps_over_a_lower_cost_route() -> None:
    map = make_map(
        [
            "########",
            "#S~...G#",
            "#......#",
            "########",
        ]
    )

    solution = solve_bfs(map)
    path_cost = sum(
        map.matrix[state.pos[1]][state.pos[0]].cost
        for state in solution.path[1:]
    )
    cheaper_detour = [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (6, 1)]
    detour_cost = sum(map.matrix[y][x].cost for x, y in cheaper_detour)

    assert_valid_path(map, solution.path)
    assert len(solution.path) == 6
    assert any(state.pos == (2, 1) for state in solution.path)
    assert path_cost == 9
    assert detour_cost == 7
