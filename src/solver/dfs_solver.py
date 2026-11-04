from src.map.map import *
from src.map.map_state import MapState
from src.solver.solver_solution import SolverSolution
from src.solver.solver_common import *

def solve_dfs(map: Map) -> SolverSolution:
    iterations = []
    start_state = MapState(map.start)
    
    reverse_path_map = {start_state: None}

    stack = [start_state]

    while stack:
        state = stack.pop()
        iterations.append(state)

        adj = adj_states(map, state)

        for adj_state in adj:
            if adj_state in reverse_path_map:
                continue
            reverse_path_map[adj_state] = state
            if adj_state.pos == map.end:
                path = get_path(reverse_path_map, adj_state)
                return SolverSolution(iterations, path)
            stack.append(adj_state)

    return SolverSolution(iterations)
