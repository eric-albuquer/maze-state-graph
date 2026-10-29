from src.solver.astar_solver import solve_astar
from src.solver.bfs_solver import solve_bfs
from src.solver.dfs_solver import solve_dfs
from src.solver.dijkstra_solver import solve_dijkstra
from src.solver.bellman_ford_solver import solve_bellman_ford

# Legenda do SOLVER_CHOICE (qual algoritmo resolve o mapa):
#   1 = A*
#   2 = BFS
#   3 = DFS
#   4 = Dijkstra
#   5 = Bellman-Ford
# Obs.: BFS, DFS, Dijkstra e Bellman-Ford ainda não foram implementados
# (levantam NotImplementedError); por enquanto só o A* funciona.
SOLVER_CHOICE = 5

SOLVERS = {
    1: solve_astar,
    2: solve_bfs,
    3: solve_dfs,
    4: solve_dijkstra,
    5: solve_bellman_ford,
}


def get_solver():
    if SOLVER_CHOICE not in SOLVERS:
        raise ValueError(
            f"SOLVER_CHOICE inválido: {SOLVER_CHOICE} (use 1..{len(SOLVERS)})"
        )
    return SOLVERS[SOLVER_CHOICE]
