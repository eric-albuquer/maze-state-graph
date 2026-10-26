from src.map.map import *
from pathlib import Path

MAPS_FOLDER = Path("maps")

def map_load(file_path: str) -> Map:
    def convert_to_node(ch: str, x: int, y: int) -> MapTile | None:
        match ch:
            case "#": return MapWall(x, y)
            case ".": return MapDotFloor(x, y)
            case "S": return MapStart(x, y)
            case "G": return MapEnd(x, y)
            case ",": return MapMud(x, y)
            case "~": return MapWater(x, y)
            case k if "a" <= k <= "z": return MapKey(x, y, k)
            case p if "A" <= p <= "Z": return MapPort(x, y, p.lower())
            case ">": return MapFloorDirected(x, y, (1, 0))
            case "<": return MapFloorDirected(x, y, (-1, 0))
            case "v": return MapFloorDirected(x, y, (0, 1))
            case "^": return MapFloorDirected(x, y, (0, -1))
            case "+": return MapBonus(x, y)
            case "*": return MapSource(x, y)
        return None

    with open(MAPS_FOLDER / file_path, "r") as file:
        start = None
        end = None
        matrix = []
        for y, line in enumerate(file):
            row = []
            for x, ch in enumerate(line):
                node = convert_to_node(ch, x, y)
                if not node: break
                if isinstance(node, MapStart):
                    start = (x, y)
                elif isinstance(node, MapEnd):
                    end = (x, y)
                row.append(node)
            matrix.append(row)

    map = Map(start, end, matrix)
    map.compute_stats()

    return map

def map_save(map: Map, file_path: str = None):
    if not file_path:
        file_path = f"generated_{map.rows}x{map.cols}_{map.start}_{map.end}.txt"

    with open(MAPS_FOLDER / file_path, "w") as file:
        for row in map.matrix:
            row_str = "".join(repr(cell) for cell in row)
            file.write(row_str + "\n")