from src.map.map import Map
from src.map.map_nodes import *
from src.map.map_state import MapState

DIRECTIONS = (
    (0, -1),
    (1, 0),
    (0, 1),
    (-1, 0)
)

def map_states(map: Map) -> set[MapState]:
    start_state = MapState(map.start, frozenset(), frozenset())

    states = {start_state}
    stack = [start_state]

    while stack:
        (x, y), keys, bonus_visited = stack.pop()

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            cell = map.matrix[ny][nx]
            if isinstance(cell, MapWall):
                continue
            if isinstance(cell, MapPort) and cell.letter not in keys:
                continue
            if isinstance(map.matrix[y][x], MapFloorDirected) and map.matrix[y][x].dir_vec != (dx, dy):
                continue

            new_keys = keys
            new_bonus_visited = bonus_visited

            if isinstance(cell, MapKey):
                new_keys = keys | {cell.letter}
            elif isinstance(cell, MapBonus):
                new_bonus_visited = bonus_visited | {(nx, ny)}

            new_state = MapState((nx, ny), new_keys, new_bonus_visited)

            if new_state in states:
                continue

            stack.append(new_state)
            states.add(new_state)

    return states