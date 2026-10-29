from src.map.map import *
from src.map.map_state import MapState
from src.solver.solver_common import *
import heapq

def heuristic(pos, end):
    return abs(pos[0] - end[0]) + abs(pos[1] - end[1])


def solve_astar(map: Map) -> list[MapState]:
    start_state = MapState(map.start)

    reverse_path_map = {start_state: None}
    best_cost_map = {start_state: 0}

    h_start = heuristic(map.start, map.end)
    heap = [(h_start, 0, start_state)]

    while heap:
        _, cost, state = heapq.heappop(heap)

        if cost > best_cost_map.get(state, float("inf")):
            continue

        if state.pos == map.end:
            return get_path(reverse_path_map, state)

        adj = adj_states_with_cost(map, state)

        for adj_state, adj_state_cost in adj:
            new_cost = adj_state_cost + cost
            if new_cost >= best_cost_map.get(adj_state, float("inf")):
                continue
            reverse_path_map[adj_state] = state
            best_cost_map[adj_state] = new_cost
            priority = new_cost + heuristic(adj_state.pos, map.end)
            heapq.heappush(heap, (priority, new_cost, adj_state))

    return []
