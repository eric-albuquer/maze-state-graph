from src.map.map import Map
from src.map.map_nodes import MapDotFloor, MapEnd, MapKey, MapPort, MapStart, MapWall
from src.map.map_state import MapState
from src.metrics.door_model_metrics import (
    DOORS_AS_FLOOR,
    DOORS_AS_WALLS,
    STATE_GRAPH,
    door_model_metrics,
)
from src.metrics.state_degrees import state_graph


def make_map(rows: list[str]) -> Map:
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
            elif symbol == "#":
                tile = MapWall(x, y)
            else:
                tile = MapDotFloor(x, y)
            tile_row.append(tile)
        matrix.append(tile_row)

    assert start is not None
    assert end is not None
    return Map(start, end, matrix)


def test_door_models_compare_open_blocked_and_key_gated_routes() -> None:
    map = make_map(
        [
            "#######",
            "#S.A.G#",
            "##..###",
            "###a###",
            "#######",
        ]
    )

    metrics = door_model_metrics(map)
    graph_with_keys = state_graph(map)

    assert metrics[DOORS_AS_FLOOR]["ordem"] > metrics[DOORS_AS_WALLS]["ordem"]
    assert metrics[STATE_GRAPH]["ordem"] > metrics[DOORS_AS_WALLS]["ordem"]
    assert MapState(map.end, frozenset({"a"})) in graph_with_keys
