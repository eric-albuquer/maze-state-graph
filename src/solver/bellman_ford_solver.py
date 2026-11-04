from src.map.map import *
from src.map.map_state import MapState
from src.solver.solver_common import *
from src.metrics.get_map_states import map_states
from src.solver.solver_solution import SolverSolution

def solve_bellman_ford(map: Map) -> SolverSolution:
    start_state = MapState(map.start)
    iterations = [start_state]

    best_cost_map = {start_state: 0}
    reverse_path_map = {start_state: None}

    total_states = map_states(map)

    for _ in range(len(total_states) - 1):
        changed = False
        for state in total_states:
            if state not in best_cost_map:
                continue
            cost = best_cost_map[state]
            adj = adj_states_with_cost(map, state)

            for adj_state, adj_state_cost in adj:
                new_cost = adj_state_cost + cost
                if new_cost >= best_cost_map.get(adj_state, float("inf")):
                    continue
                iterations.append(adj_state)
                reverse_path_map[adj_state] = state
                best_cost_map[adj_state] = new_cost
                changed = True

        if not changed:
            break

    end_state = None
    end_cost = float("inf")

    for state in total_states:
        if state not in reverse_path_map:
            continue
        cost = best_cost_map[state]
        adj = adj_states_with_cost(map, state)

        if state.pos == map.end and cost < end_cost:
            end_state = state
            end_cost = cost

        for adj_state, adj_state_cost in adj:
            new_cost = adj_state_cost + cost
            if new_cost >= best_cost_map.get(adj_state, float("inf")):
                continue
            raise ValueError(f"Infinite cicle detected: {state} -> {adj_state}")

    if not end_state:
        return SolverSolution(iterations)

    path = get_path(reverse_path_map, end_state)
    return SolverSolution(iterations, path)
