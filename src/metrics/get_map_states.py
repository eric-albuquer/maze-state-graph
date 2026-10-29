from src.map.map import Map
from src.map.map_nodes import *
from src.map.map_state import MapState
from src.solver.solver_common import adj_states

def map_states(map: Map) -> set[MapState]:
    start_state = MapState(map.start, frozenset(), frozenset())

    states = {start_state}
    stack = [start_state]

    while stack:
        state = stack.pop()

        adj = adj_states(map, state)

        for new_state in adj:
            if new_state in states:
                continue
            stack.append(new_state)
            states.add(new_state)

    return states