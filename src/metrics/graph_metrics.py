from pathlib import Path

from src.map.map import Map
from src.map.map_loader import map_load
from src.map.map_nodes import MapBonus, MapFloorDirected, MapKey, MapWall
from src.metrics.state_degrees import state_graph
from src.settings.map_setup import MAPS
from src.solver.solver_common import DIRECTIONS

OUT_FILE = Path("out/parte1/metricas_grafos.txt")


# G_pos células que podem ser alcançadas aparti de s ignrando chaves e bonus
# portas sao tratadas como abertas
def pos_graph(map: Map) -> dict[tuple, list[tuple]]:

    adj = {} # o que ja foi visitado
    stack = [map.start]
    while stack:
        x, y = stack.pop()
        if (x, y) in adj:
            continue
        cell = map.matrix[y][x]
        adj[(x, y)] = []
        for dx, dy in DIRECTIONS:
            if isinstance(map.matrix[y + dy][x + dx], MapWall):
                continue
            if isinstance(cell, MapFloorDirected) and cell.dir_vec != (dx, dy):
                continue
            adj[(x, y)].append((x + dx, y + dy))
            stack.append((x + dx, y + dy))
    return adj


def graph_metrics(adj: dict, ceiling: int) -> dict:
    order = len(adj)
    size = sum(len(neighbors) for neighbors in adj.values())
    max_edges = order * (order - 1)
    return {
        "ordem": order,
        "tamanho": size,
        "densidade": size / max_edges if max_edges else 0,
        "teto": ceiling,
        "ocupacao": order / ceiling if ceiling else 0,
    }


def map_metrics(map: Map) -> tuple[dict, dict]:
    cells = [cell for row in map.matrix for cell in row]
    free_cells = sum(not isinstance(cell, MapWall) for cell in cells)
    keys = sum(isinstance(cell, MapKey) for cell in cells)
    bonus = sum(isinstance(cell, MapBonus) for cell in cells)

    g_pos = graph_metrics(pos_graph(map), free_cells)
    g_es = graph_metrics(state_graph(map), free_cells * 2**keys * 2**bonus)
    return g_pos, g_es


def format_table(title: str, rows: list[tuple[str, dict]]) -> list[str]:
    header = f"{'mapa':<20}{'ordem':>8}{'tamanho':>10}{'densidade':>12}{'teto':>10}{'ocupacao':>11}"
    lines = [title, "-" * len(header), header, "-" * len(header)]
    for name, m in rows:
        lines.append(
            f"{name:<20}{m['ordem']:>8}{m['tamanho']:>10}"
            f"{m['densidade']:>12.4f}{m['teto']:>10}{m['ocupacao']:>11.1%}"
        )
    lines.append("")
    return lines


if __name__ == "__main__":
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    pos_rows, es_rows = [], []
    for map_file in MAPS.values():
        g_pos, g_es = map_metrics(map_load(map_file))
        name = Path(map_file).stem
        pos_rows.append((name, g_pos))
        es_rows.append((name, g_es))

    lines = format_table("G_pos (grafo de posicoes)", pos_rows)
    lines += format_table("G_es (grafo de estados)", es_rows)
    OUT_FILE.write_text("\n".join(lines))

    print(f"TXT salvo em {OUT_FILE}")
