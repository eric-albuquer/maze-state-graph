from pathlib import Path

from src.map.map import Map
from src.map.map_loader import map_load
from src.metrics.state_degrees import state_graph
from src.settings.map_setup import MAPS


OUT_FILE = Path("out/parte1/metricas_camadas_chaves.txt")


def key_layer_metrics(
    map: Map,
) -> tuple[
    dict[frozenset[str], int],
    dict[tuple[frozenset[str], frozenset[str]], int],
]:
    graph = state_graph(map)
    states_per_layer: dict[frozenset[str], int] = {}
    arcs_between_layers: dict[
        tuple[frozenset[str], frozenset[str]], int
    ] = {}

    for state, neighbors in graph.items():
        states_per_layer[state.keys] = states_per_layer.get(state.keys, 0) + 1
        for neighbor in neighbors:
            if state.keys == neighbor.keys:
                continue
            layer_transition = (state.keys, neighbor.keys)
            arcs_between_layers[layer_transition] = (
                arcs_between_layers.get(layer_transition, 0) + 1
            )

    return states_per_layer, arcs_between_layers


def format_key_layer(key_layer: frozenset[str]) -> str:
    return "{" + ", ".join(sorted(key_layer)) + "}"


def format_map_metrics(map_name: str, map: Map) -> list[str]:
    states_per_layer, arcs_between_layers = key_layer_metrics(map)
    lines = [f"Mapa: {map_name}", "Estados por camada de chaves:"]

    for layer in sorted(states_per_layer, key=lambda keys: tuple(sorted(keys))):
        lines.append(
            f"  {format_key_layer(layer)}: {states_per_layer[layer]} estados"
        )

    lines.append("Arcos dirigidos entre camadas distintas:")
    if not arcs_between_layers:
        lines.append("  Nenhum")
    else:
        for (source, target), count in sorted(
            arcs_between_layers.items(),
            key=lambda item: (
                tuple(sorted(item[0][0])),
                tuple(sorted(item[0][1])),
            ),
        ):
            lines.append(
                f"  {format_key_layer(source)} -> {format_key_layer(target)}: "
                f"{count} arcos"
            )

    lines.append("")
    return lines


if __name__ == "__main__":
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = ["Métricas do grafo de estados por conjunto de chaves", ""]

    for map_file in MAPS.values():
        map_name = Path(map_file).stem
        lines.extend(format_map_metrics(map_name, map_load(map_file)))

    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Relatório salvo em {OUT_FILE}")
