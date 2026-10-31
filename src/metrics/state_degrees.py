import csv
from pathlib import Path

from src.map.map import Map
from src.settings.map_setup import MAP_CHOICE, MAPS
from src.map.map_nodes import *
from src.map.map_state import MapState
from src.solver.solver_common import adj_states

def state_graph(map: Map) -> dict[MapState, list[MapState]]:
    start = MapState(map.start, frozenset(), frozenset())
    adj = {}
    stack = [start]

    while stack:
        state = stack.pop()
        if state in adj:
            continue
        adj[state] = adj_states(map, state)
        stack.extend(adj[state])

    return adj


def degrees(adj: dict[MapState, list[MapState]]):
    out_deg = {s: len(neighbors) for s, neighbors in adj.items()}
    in_deg = dict.fromkeys(adj, 0)
    for neighbors in adj.values():
        for v in neighbors:
            in_deg[v] += 1
    return in_deg, out_deg


def state_degrees(map: Map) -> str:
    adj = state_graph(map)
    in_deg, out_deg = degrees(adj)

    assert sum(in_deg.values()) == sum(out_deg.values())

    lines = [
        f"{s}  in={in_deg[s]}  out={out_deg[s]}"
        for s in sorted(adj, key=lambda s: (s.pos, sorted(s.keys), sorted(s.bonus_visited)))
    ]
    return "\n".join(lines)



def state_degrees_csv(map: Map, out_dir: Path = Path("out/parte1")) -> Path:
    adj = state_graph(map)
    in_deg, out_deg = degrees(adj)

    name = Path(MAPS[MAP_CHOICE]).stem if MAP_CHOICE in MAPS else "gerado"
    file_path = out_dir / f"graus_{name}.csv"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", newline="") as file:

        writer = csv.writer(file)
        writer.writerow(["pos", "chaves", "bonus_visitados", "grau_entrada", "grau_saida"])


        for s in sorted(adj, key=lambda s: (s.pos, sorted(s.keys), sorted(s.bonus_visited))):

            writer.writerow([
                f"{s.pos[0]},{s.pos[1]}",
                "".join(sorted(s.keys)),
                ";".join(str(b) for b in sorted(s.bonus_visited)),
                in_deg[s],
                out_deg[s],
            ])
            
    return file_path
