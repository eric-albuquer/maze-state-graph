from src.map.map import *
from src.map.map_state import MapState
from src.solver.solver_solution import SolverSolution
from src.solver.solver_common import *
import random


def random_walk(map: Map) -> SolverSolution:
    iterations = []
    state = MapState(map.start)
    
    path = [state]

    while state.pos != map.end:
        x, y = state.pos
        dx, dy = random.choice(DIRECTIONS)
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= map.cols:
            continue
        if ny < 0 or ny >= map.rows:
            continue

        keys = state.keys
        bonus = state.bonus_visited

        cell = map.matrix[ny][nx]

        if isinstance(cell, MapKey):
            keys |= {cell.letter}
        elif isinstance(cell, MapBonus):
            bonus |= {(nx, ny)}

        iterations.append(state)

        next_state = MapState((nx, ny), keys, bonus)
        path.append(next_state)

        state = next_state

    return SolverSolution(iterations, path)
