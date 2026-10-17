from map.map_loader import map_load, map_save
from solver.solver import solve
from map.map_generator import generate_map

#map = map_load("m03_tres_chaves.txt")

map = generate_map(
    rows=13,
    cols=31, 
    algorithm="backtracking", 
    loop_density = 0.05,
    water_density= 0.05, 
    mud_density= 0.05, 
    source_density= 0, 
    bonus_density= 0.05, 
    floor_directed_density=0.0
)

print(map)

#map_save(map, "test_map.txt")

path = solve(map)

for val in path:
    print(val)

print(len(path))