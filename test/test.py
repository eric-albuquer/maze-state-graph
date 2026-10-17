from map.map_loader import map_load, map_save
from solver.solver import solve
from map.map_generator import generate_map

#map = map_load("m02_uma_chave.txt")
map = generate_map(
    rows=7,
    cols=15, 
    backtracking=True, 
    loop_density = 0.0,
    water_density= 0.05, 
    mud_density= 0.05, 
    source_density= 0, 
    bonus_density= 0.0, 
    floor_directed_density=0.2
)

print(map)

#map_save(map, "gerado")

path = solve(map)
for val in path:
    print(val)