from src.solver.astar_solver import solve_astar
from src.solver.bfs_solver import solve_bfs
from src.solver.dfs_solver import solve_dfs
from src.solver.dijkstra_solver import solve_dijkstra
from src.solver.bellman_ford_solver import solve_bellman_ford
from src.solver.wall_solver import solve_wall_bfs
from src.solver.xiter_solver import xiter_solver
from src.solver.random_walk import random_walk
from src.solver.portal_solver import portal_solver

# Legenda do SOLVER_CHOICE (qual algoritmo resolve o mapa):
#   1 = A*
#   2 = BFS
#   3 = DFS
#   4 = Dijkstra
#   5 = Bellman-Ford
#   6 = Caminhada pelas paredes
SOLVER_CHOICE = 5

SOLVERS = {
    1: solve_astar,
    2: solve_bfs,
    3: solve_dfs,
    4: solve_dijkstra,
    5: solve_bellman_ford,
    6: solve_wall_bfs,
    7: xiter_solver,
    8: random_walk,
    9: portal_solver
}


# [IA] Claude Code (Claude Sonnet 5.5) – nomes dos algoritmos para os menus da UI e escolha do solver por parâmetro (sem alterar os algoritmos)
SOLVER_NAMES = {
    1: "A*",
    2: "BFS",
    3: "DFS",
    4: "Dijkstra",
    5: "Bellman-Ford",
    6: "BFS Wall",
    7: "A* Hack",
    8: "Random Walk",
    9: "Portal Solver"
}


def get_solver(choice: int = SOLVER_CHOICE):
    if choice not in SOLVERS:
        raise ValueError(f"SOLVER_CHOICE inválido: {choice} (use 1..{len(SOLVERS)})")
    return SOLVERS[choice]
