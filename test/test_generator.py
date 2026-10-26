import random
from src.map.map_generator import generate_map
from src.map.map_loader import map_save
from src.solver.astar_solver import solve_astar
import time

# Parameters to choose from randomly
strategies = ["backtracking", "recursive_division", "kruskal", "prim"]
sizes = [i for i in range(9, 26, 2)]
key_sets = [["a"], ["a", "b"], ["a", "b", "c", "d"]]
braid_factors = [0.0, 0.05, 0.1, 0.25]

density_configs = [
    {
        "water_density": 0.05,
        "mud_density": 0.05,
        "source_density": 0.1,
        "bonus_density": 0.05,
        "floor_directed_density": 0.0,
    },
    {
        "water_density": 0.15,
        "mud_density": 0.15,
        "source_density": 0.05,
        "bonus_density": 0.05,
        "floor_directed_density": 0.05,
    },
    {
        "water_density": 0.0,
        "mud_density": 0.0,
        "source_density": 0.0,
        "bonus_density": 0.0,
        "floor_directed_density": 0.0,
    },
    {
        "water_density": 0.1,
        "mud_density": 0.0,
        "source_density": 0.1,
        "bonus_density": 0.1,
        "floor_directed_density": 0.1,
    },
]

total_tests = 0
failed_tests = 0
target_tests = 500

print(f"=== STARTING RANDOMIZED STRESS TEST ({target_tests} MAPS) ===")

while total_tests < target_tests:
    strategy = random.choice(strategies)
    rows, cols = random.choice(sizes), random.choice(sizes)
    keys = random.choice(key_sets)
    braid = random.choice(braid_factors)
    dens = random.choice(density_configs)

    if sum(dens.values()) > 1.0:
        continue

    total_tests += 1

    print(f"\n--- Testing Map {total_tests}/{target_tests} ---")
    print(f"  > Strategy  : {strategy}")
    print(f"  > Size      : {rows}x{cols}")
    print(f"  > Keys      : {keys}")
    print(f"  > Braid     : {braid}")
    print(f"  > Densities : {dens}")

    try:
        # Generation phase
        generation_start = time.time()
        generated_map = generate_map(
            rows=rows,
            cols=cols,
            strategy=strategy,
            keys=keys,
            braid_factor=braid,
            **dens,
        )
        generation_end = time.time()
        gen_time = round(generation_end - generation_start, 3)

        # Solver phase
        solution_start = time.time()
        solution = solve_astar(generated_map)
        solution_end = time.time()
        sol_time = round(solution_end - solution_start, 3)

        print(f"  > Gen Time  : {gen_time}s | Sol Time: {sol_time}s")

        # Checks if the map is unsolvable
        if solution is None:
            failed_tests += 1
            filename = f"failed_{strategy}_{rows}x{cols}_keys{len(keys)}_braid{braid}_{total_tests}.txt"
            map_save(generated_map, filename)
            print(f"  [ALERT]   RESULT: NO SOLUTION (Saved to {filename})")
        else:
            print(f"  [SUCCESS] RESULT: SOLVED (Best State: {solution[-1]})")

    except Exception as e:
        print(f"  [ERROR]   Exception raised: {e}")

print("\n" + "=" * 40)
print("=== STRESS TEST SUMMARY ===")
print(f"Total maps tested : {total_tests}")
print(f"Unsolvable maps   : {failed_tests}")

if failed_tests == 0:
    print(f"Awesome! No generated maps were left without a solution across all {target_tests} random tests.")
else:
    print("Attention: Some maps failed. Check the generated files for analysis.")