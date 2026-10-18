from map.map_loader import map_load, map_save
from solver.astar_solver import solve_astar
from map.map_generator import generate_map

# map = map_load("m03_tres_chaves.txt")

map = generate_map(
    rows=13,
    cols=31,
    strategy="backtracking",
    keys=["a", "b", "c", "d"],
    braid_factor=0.05,
    water_density=0.05,
    mud_density=0.05,
    source_density=0.1,
    bonus_density=0.05,
    floor_directed_density=0.0,
)

print(map)

# map_save(map, "test_map.txt")

path = solve_astar(map)

for val in path:
    print(val)

print(len(path))
