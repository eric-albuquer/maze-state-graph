from map.map_loader import map_load, map_save
from map.map_generator import generate_map
from solver.astar_solver import solve_astar
# from solver.bfs_solver import solve_bfs
# from solver.dfs_solver import solve_dfs
# from solver.dijkstra_solver import solve_dijkstra

map = map_load("m03_tres_chaves.txt")

map = generate_map(
    rows=51,
    cols=51,
    strategy="backtracking",
    keys=["a", "b", "c", "d"],
    braid_factor=0.01,
    water_density=0.1,
    mud_density=0.1,
    source_density=0.005,
    bonus_density=0.001,
    floor_directed_density=0.001,
)

# map_save(map, "huge_map_2001_2001.txt")

# path = solve_bfs(map)

# for val in path:
#     print(val)

# print(len(path))
