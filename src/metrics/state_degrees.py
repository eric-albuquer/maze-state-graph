from src.map.map import Map
from src.map.map_nodes import *
from src.map.map_state import MapState
from src.metrics.get_map_states import DIRECTIONS

#get a map and a state and return one list of next possible states
def successors(map: Map, state: MapState) -> list[MapState]:
    (x, y), keys, bonus_visited = state
    result = []

    if isinstance(map.matrix[y][x], MapEnd):
        return result

    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        cell = map.matrix[ny][nx]
        if isinstance(cell, MapWall):
            continue
        if isinstance(cell, MapPort) and cell.letter not in keys:
            continue
        if isinstance(cell, MapFloorDirected) and cell.dir_vec != (dx, dy):
            continue

        new_keys = keys
        new_bonus_visited = bonus_visited

        if isinstance(cell, MapKey):
            new_keys = keys | {cell.letter}
        elif isinstance(cell, MapBonus):
            new_bonus_visited = bonus_visited | {(nx, ny)}

        result.append(MapState((nx, ny), new_keys, new_bonus_visited))

    return result


def state_graph(map: Map) -> dict[MapState, list[MapState]]:
    start = MapState(map.start, frozenset(), frozenset())
    adj = {}
    stack = [start]

    while stack:
        state = stack.pop()
        if state in adj:
            continue
        adj[state] = successors(map, state)
        stack.extend(adj[state])

    return adj


def degrees(adj: dict[MapState, list[MapState]]):
    out_deg = {s: len(neighbors) for s, neighbors in adj.items()}
    in_deg = dict.fromkeys(adj, 0)
    for neighbors in adj.values():
        for v in neighbors:
            in_deg[v] += 1
    return in_deg, out_deg


def state_degrees(map: Map) -> str:
    adj = state_graph(map)
    in_deg, out_deg = degrees(adj)

    assert sum(in_deg.values()) == sum(out_deg.values())

    lines = [
        f"{s}  in={in_deg[s]}  out={out_deg[s]}"
        for s in sorted(adj, key=lambda s: (s.pos, sorted(s.keys), sorted(s.bonus_visited)))
    ]
    return "\n".join(lines)
