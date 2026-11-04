from src.map.map import *
from src.map.map_state import MapState
from src.solver.solver_solution import SolverSolution
from src.solver.solver_common import *
import heapq


def solve_dijkstra(map: Map) -> SolverSolution:
    iterations = []
    start_state = MapState(map.start)

    reverse_path_map = {start_state: None}
    best_cost_map = {start_state: 0}

    heap = [(0, start_state)]

    while heap:
        cost, state = heapq.heappop(heap)

        if cost > best_cost_map.get(state, float("inf")):
            continue

        iterations.append(state)

        if state.pos == map.end:
            path = get_path(reverse_path_map, state)
            return SolverSolution(iterations, path)

        adj = adj_states_with_cost(map, state)

        for adj_state, adj_state_cost in adj:
            new_cost = adj_state_cost + cost
            if new_cost >= best_cost_map.get(adj_state, float("inf")):
                continue
            reverse_path_map[adj_state] = state
            best_cost_map[adj_state] = new_cost
            heapq.heappush(heap, (new_cost, adj_state))

    return SolverSolution(iterations)
