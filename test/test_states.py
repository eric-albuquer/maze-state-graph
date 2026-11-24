from src.map.map import Map
from src.map.map_nodes import (
    MapBonus,
    MapDotFloor,
    MapEnd,
    MapKey,
    MapPort,
    MapStart,
    MapWall,
)
from src.map.map_state import MapState
from src.solver.solver_common import adj_states, adj_states_with_cost


def make_map(rows: list[str]) -> Map:
    tile_types = {
        "#": MapWall,
        ".": MapDotFloor,
        "+": MapBonus,
        "a": MapKey,
        "A": MapPort,
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
            elif symbol in ("a", "A"):
                tile = tile_types[symbol](x, y, symbol)
            else:
                tile = tile_types[symbol](x, y)
            tile_row.append(tile)
        matrix.append(tile_row)

    assert start is not None
    assert end is not None
    return Map(start, end, matrix)


def test_collecting_a_key_updates_the_state() -> None:
    map = make_map(
        [
            "#####",
            "#SaG#",
            "#####",
        ]
    )

    next_state = adj_states(map, MapState(map.start))[0]

    assert next_state.pos == (2, 1)
    assert next_state.keys == frozenset({"a"})
    assert next_state.bonus_visited == frozenset()


def test_locked_port_requires_its_matching_key() -> None:
    map = make_map(
        [
            "#####",
            "#SAG#",
            "#####",
        ]
    )
    state_without_key = MapState(map.start)
    state_with_key = MapState(map.start, frozenset({"a"}))

    assert MapState((2, 1)) not in adj_states(map, state_without_key)
    assert MapState((2, 1), frozenset({"a"})) in adj_states(map, state_with_key)


def test_collecting_a_bonus_marks_it_as_visited() -> None:
    map = make_map(
        [
            "#####",
            "#S+G#",
            "#####",
        ]
    )

    bonus_state = adj_states(map, MapState(map.start))[0]
    goal_state = next(
        state for state in adj_states(map, bonus_state)
        if state.pos == map.end
    )

    assert bonus_state.pos == (2, 1)
    assert bonus_state.bonus_visited == frozenset({(2, 1)})
    assert goal_state.bonus_visited == frozenset({(2, 1)})


def test_revisiting_a_bonus_uses_normal_floor_cost() -> None:
    map = make_map(
        [
            "####",
            "#S+#",
            "#G.#",
            "####",
        ]
    )
    bonus_state = adj_states(map, MapState(map.start))[0]
    lower_floor_state = next(
        state for state in adj_states(map, bonus_state)
        if state.pos == (2, 2)
    )
    revisit = next(
        (state, cost)
        for state, cost in adj_states_with_cost(map, lower_floor_state)
        if state.pos == (2, 1)
    )

    assert bonus_state.bonus_visited == frozenset({(2, 1)})
    assert revisit == (bonus_state, 1)
