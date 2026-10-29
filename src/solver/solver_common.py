from src.map.map import *
from src.map.map_state import MapState

DIRECTIONS = (
    (0, -1),
    (1, 0),
    (0, 1),
    (-1, 0)
)

def adj_states_with_cost(map: Map, state: MapState) -> list[tuple[MapState, int]]:
    (x, y), keys, bonus_visited = state
    result = []

    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        cell = map.matrix[ny][nx]
        if isinstance(cell, MapWall):
            continue
        if isinstance(cell, MapPort) and cell.letter not in keys:
            continue
        if isinstance(map.matrix[y][x], MapFloorDirected) and map.matrix[y][x].dir_vec != (dx, dy):
            continue

        cell_cost = cell.cost
        new_keys = keys
        new_bonus_visited = bonus_visited

        new_pos = (nx, ny)

        if isinstance(cell, MapKey):
            new_keys = keys | {cell.letter}
        elif isinstance(cell, MapBonus):
            if new_pos in bonus_visited:
                cell_cost = 1
            else:
                new_bonus_visited = bonus_visited | {new_pos}

        result.append((MapState(new_pos, new_keys, new_bonus_visited), cell_cost))

    return result

def get_path(
        reverse_path_map: dict[MapState, MapState],
        state: MapState
    ) -> list[MapState]:
    curr = state
    path = []
    while curr:
        path.append(curr)
        curr = reverse_path_map[curr]
    return path[::-1]