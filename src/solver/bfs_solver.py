from src.map.map import *
from src.map.map_state import MapState
from src.solver.solver_common import *
from collections import deque


def solve_bfs(map: Map) -> list[MapState]:
    start_state = MapState(map.start)
    
    reverse_path_map = {start_state: None}

    queue = deque([start_state])

    while queue:
        state = queue.popleft()

        adj = adj_states(map, state)

        for adj_state in adj:
            if adj_state in reverse_path_map:
                continue
            reverse_path_map[adj_state] = state
            if adj_state.pos == map.end:
                return get_path(reverse_path_map, adj_state)
            queue.append(adj_state)

    return []
