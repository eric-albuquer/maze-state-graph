from src.map.map import Map
from src.map.map_nodes import MapDotFloor, MapEnd, MapKey, MapStart, MapWall
from src.metrics.key_layer_metrics import key_layer_metrics


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
            elif symbol == "#":
                tile = MapWall(x, y)
            else:
                tile = MapDotFloor(x, y)
            tile_row.append(tile)
        matrix.append(tile_row)

    assert start is not None
    assert end is not None
    return Map(start, end, matrix)


def test_key_layer_metrics_count_states_and_arcs_between_layers() -> None:
    map = make_map(
        [
            "#######",
            "#S.a.G#",
            "#######",
        ]
    )

    states_per_layer, arcs_between_layers = key_layer_metrics(map)

    assert states_per_layer == {
        frozenset(): 2,
        frozenset({"a"}): 5,
    }
    assert arcs_between_layers == {
        (frozenset(), frozenset({"a"})): 1,
    }


def test_key_layer_metrics_without_keys_has_no_inter_layer_arcs() -> None:
    map = make_map(
        [
            "#####",
            "#S.G#",
            "#####",
        ]
    )

    states_per_layer, arcs_between_layers = key_layer_metrics(map)

    assert states_per_layer == {frozenset(): 3}
    assert arcs_between_layers == {}
