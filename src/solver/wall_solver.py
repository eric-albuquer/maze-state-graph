from src.map.map import *
from src.map.map_state import MapState
from src.solver.solver_solution import SolverSolution
from src.solver.solver_common import *
from collections import deque


def solve_wall_bfs(map: Map) -> SolverSolution:
    iterations = []
    start_state = MapState(map.start)
    
    reverse_path_map = {start_state: None}

    queue = deque([start_state])

    while queue:
        state = queue.popleft()
        x, y = state.pos
        iterations.append(state)

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= map.cols:
                continue
            if ny < 0 or ny >= map.rows:
                continue
            if not isinstance(map.matrix[ny][nx], (MapWall, MapEnd)):
                continue
            adj_state = MapState((nx, ny))
            if adj_state in reverse_path_map:
                continue
            reverse_path_map[adj_state] = state
            if adj_state.pos == map.end:
                path = get_path(reverse_path_map, adj_state)
                return SolverSolution(iterations, path, reverse_path_map)
            queue.append(adj_state)

    return SolverSolution(iterations, parent=reverse_path_map)
