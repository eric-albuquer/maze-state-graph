from src.map.map import *
from src.map.map_state import MapState
from src.solver.solver_common import *

def solve_dfs(map: Map) -> list[MapState]:
    start_state = MapState(map.start)
    
    reverse_path_map = {start_state: None}

    stack = [start_state]

    while stack:
        state = stack.pop()

        adj = adj_states_with_cost(map, state)

        for adj_state, _ in adj:
            if adj_state in reverse_path_map:
                continue
            reverse_path_map[adj_state] = state
            if adj_state.pos == map.end:
                return get_path(reverse_path_map, adj_state)
            stack.append(adj_state)

    return []
