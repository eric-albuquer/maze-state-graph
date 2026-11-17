from src.map.map import *
from src.map.map_state import MapState
from src.solver.solver_solution import SolverSolution
from src.solver.solver_common import *

def xiter_solver(map: Map) -> SolverSolution:
    iterations = []
    path = []
    
    x0, y0 = map.start
    x1, y1 = map.end

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    erro = dx - dy

    bonus = frozenset()
    keys = frozenset()

    while True:
        cell = map.matrix[y0][x0]
        
        if isinstance(cell, MapKey):
            keys |= {cell.letter}
        elif isinstance(cell, MapBonus):
            bonus |= {(x0, y0)}
            
        state = MapState((x0, y0), keys, bonus)

        iterations.append(state)
        path.append(state)

        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * erro
        if e2 > -dy:
            erro -= dy
            x0 += sx
        if e2 < dx:
            erro += dx
            y0 += sy

    return SolverSolution(iterations, path)
