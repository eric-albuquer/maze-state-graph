from pathlib import Path

from src.map.map import Map
from src.map.map_loader import map_load
from src.solver.astar_solver import solve_astar

OUT_DIR = Path("out/parte1/gabarito_mapa_gerado")


def solution_txt(map: Map, name: str, out_dir: Path = OUT_DIR) -> Path | None:
    path = solve_astar(map).path
    if not path:
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"gabarito_{name}.txt"

    lines = [f"Mapa: {name}", "Algoritmo: A*", "pos   /   linha    / coluna",""]
    for i, state in enumerate(path):
        x, y = state.pos
        lines.append(f"{i:>3}: ({y}, {x})")

    file_path.write_text("\n".join(lines) + "\n")
    return file_path


if __name__ == "__main__":
    from src.settings.map_setup import MAPS

    for map_file in MAPS.values():
        file_path = solution_txt(map_load(map_file), Path(map_file).stem)

