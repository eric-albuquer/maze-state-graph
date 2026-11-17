from src.map.map import *
from src.map.map_state import MapState
from src.solver.solver_solution import SolverSolution
from src.solver.solver_common import *
import random


def random_walk(map: Map) -> SolverSolution:
    state = MapState(map.start)

    path = [state]

    while state.pos != map.end and len(path) < map.stats.estimated_states ** 2:
        state = random.choice(adj_states(map, state))
        path.append(state)

    return SolverSolution(path, path)
