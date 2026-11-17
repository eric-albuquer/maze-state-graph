from src.map.map_loader import map_load, map_save
from src.map.map_generator import generate_map
from src.solver.astar_solver import solve_astar
from src.metrics.get_map_states import map_states
# from solver.bfs_solver import solve_bfs
# from solver.dfs_solver import solve_dfs
# from solver.dijkstra_solver import solve_dijkstra
from src.solver.bellman_ford_solver import solve_bellman_ford
from src.solver.portal_solver import portal_solver

map = map_load("m03_tres_chaves.txt")

# map = generate_map(
#     rows=101,
#     cols=131,
#     strategy="backtracking",
#     keys=["a", "b", "c", "d"],
#     braid_factor=0.001,
#     water_density=0.15,
#     mud_density=0.1,
#     source_density=0.02,
#     bonus_density=0.02,
#     floor_directed_density=0.001,
# )

print(map)
# states = map_states(map)

# for s in states:
#     print(s)
# print(len(states))

portal_solver(map)

# path = solve_astar(map)

# for val in path:
#     print(val)

# print(len(path))
