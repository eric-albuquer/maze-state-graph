from pathlib import Path

from src.map.map import Map
from src.map.map_loader import map_load
from src.map.map_nodes import (
    MapBonus,
    MapFloorDirected,
    MapKey,
    MapPort,
    MapWall,
)
from src.metrics.graph_metrics import format_table, graph_metrics, pos_graph
from src.metrics.state_degrees import state_graph
from src.settings.map_setup import MAPS
from src.solver.solver_common import DIRECTIONS


OUT_FILE = Path("out/parte1/metricas_modelos_portas.txt")

DOORS_AS_FLOOR = "doors_as_floor"
DOORS_AS_WALLS = "doors_as_walls"
STATE_GRAPH = "state_graph"

MODEL_TITLES = {
    DOORS_AS_FLOOR: "G_pos (portas tratadas como chao)",
    DOORS_AS_WALLS: "G_pos (portas tratadas como paredes)",
    STATE_GRAPH: "G_es (grafo de estados com chaves)",
}


def pos_graph_doors_as_walls(map: Map) -> dict[tuple[int, int], list[tuple[int, int]]]:
    adj = {}
    stack = [map.start]

    while stack:
        x, y = stack.pop()
        if (x, y) in adj:
            continue

        cell = map.matrix[y][x]
        adj[(x, y)] = []
        for dx, dy in DIRECTIONS:
            neighbor = map.matrix[y + dy][x + dx]
            if isinstance(neighbor, (MapWall, MapPort)):
                continue
            if isinstance(cell, MapFloorDirected) and cell.dir_vec != (dx, dy):
                continue
            next_pos = (x + dx, y + dy)
            adj[(x, y)].append(next_pos)
            stack.append(next_pos)

    return adj


def door_model_metrics(map: Map) -> dict[str, dict]:
    cells = [cell for row in map.matrix for cell in row]
    free_cells = sum(not isinstance(cell, MapWall) for cell in cells)
    free_cells_without_doors = sum(
        not isinstance(cell, (MapWall, MapPort)) for cell in cells
    )
    key_count = sum(isinstance(cell, MapKey) for cell in cells)
    bonus_count = sum(isinstance(cell, MapBonus) for cell in cells)

    return {
        DOORS_AS_FLOOR: graph_metrics(pos_graph(map), free_cells),
        DOORS_AS_WALLS: graph_metrics(
            pos_graph_doors_as_walls(map),
            free_cells_without_doors,
        ),
        STATE_GRAPH: graph_metrics(
            state_graph(map),
            free_cells * 2**key_count * 2**bonus_count,
        ),
    }


def write_report(out_file: Path = OUT_FILE) -> Path:
    rows_by_model = {
        model: []
        for model in (DOORS_AS_FLOOR, DOORS_AS_WALLS, STATE_GRAPH)
    }

    for map_file in MAPS.values():
        map_name = Path(map_file).stem
        metrics = door_model_metrics(map_load(map_file))
        for model, result in metrics.items():
            rows_by_model[model].append((map_name, result))

    lines = []
    for model, title in MODEL_TITLES.items():
        lines.extend(format_table(title, rows_by_model[model]))

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(lines), encoding="utf-8")
    return out_file


if __name__ == "__main__":
    print(f"Relatorio salvo em {write_report()}")
