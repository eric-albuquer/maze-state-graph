from pathlib import Path

from src.map.map import Map
from src.map.map_loader import map_load
from src.solver.astar_solver import solve_astar
from src.solver.bellman_ford_solver import solve_bellman_ford
from src.solver.bfs_solver import solve_bfs
from src.solver.dfs_solver import solve_dfs
from src.solver.dijkstra_solver import solve_dijkstra

OUT_DIR = Path("out/parte1/gabarito_mapa_gerado")

# nome da pasta -> (nome exibido, função do algoritmo)
ALGORITHMS = {
    "astar": ("A*", solve_astar),
    "bfs": ("BFS", solve_bfs),
    "dfs": ("DFS", solve_dfs),
    "dijkstra": ("Dijkstra", solve_dijkstra),
    "bellman_ford": ("Bellman-Ford", solve_bellman_ford),
}


def solution_txt(map: Map, name: str, folder: str, out_dir: Path = OUT_DIR) -> Path | None:
    algorithm_name, solver = ALGORITHMS[folder]
    path = solver(map).path
    if not path:
        return None

    out_dir = out_dir / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"gabarito_{name}.txt"

    lines = [f"Mapa: {name}", f"Algoritmo: {algorithm_name}", "pos   /   linha    / coluna",""]
    for i, state in enumerate(path):
        x, y = state.pos
        lines.append(f"{i:>3}: ({y}, {x})")

    file_path.write_text("\n".join(lines) + "\n")
    return file_path


if __name__ == "__main__":
    from src.settings.map_setup import MAPS

    for map_file in MAPS.values():
        map = map_load(map_file)
        for folder in ALGORITHMS:
            try:
                file_path = solution_txt(map, Path(map_file).stem, folder)
            except Exception as error:
                print(f"{map_file} [{folder}]: erro {type(error).__name__}: {error}")
                continue
            print(f"{map_file} [{folder}]: {file_path or 'sem solução'}")
