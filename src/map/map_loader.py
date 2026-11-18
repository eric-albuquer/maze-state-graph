from src.map.map import *
from pathlib import Path

MAPS_FOLDER = Path("maps")
# [IA] Claude Code (Claude Sonnet 5.5) – subpasta maps/update/ onde ficam os mapas importados
UPDATE_FOLDER = "update"

# [IA] Claude Code (Claude Sonnet 5.5) – parsing extraído de map_load para ser reaproveitado pela importação (comportamento inalterado)
def _parse_map(lines) -> Map:
    def convert_to_node(ch: str, x: int, y: int) -> MapTile | None:
        match ch:
            case "#": return MapWall(x, y)
            case ".": return MapDotFloor(x, y)
            case "S": return MapStart(x, y)
            case "G": return MapEnd(x, y)
            case ",": return MapMud(x, y)
            case "~": return MapWater(x, y)
            case ">": return MapFloorDirected(x, y, (1, 0))
            case "<": return MapFloorDirected(x, y, (-1, 0))
            case "v": return MapFloorDirected(x, y, (0, 1))
            case "^": return MapFloorDirected(x, y, (0, -1))
            case k if "a" <= k <= "z": return MapKey(x, y, k)
            case p if "A" <= p <= "Z": return MapPort(x, y, p.lower())
            case "+": return MapBonus(x, y)
            case "*": return MapSource(x, y)
        return None

    start = None
    end = None
    matrix = []
    for y, line in enumerate(lines):
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


def map_load(file_path: str) -> Map:
    with open(MAPS_FOLDER / file_path, "r") as file:
        return _parse_map(file)


# [IA] Claude Code (Claude Sonnet 5.5) – símbolos aceitos na importação de mapas
VALID_SYMBOLS = set("#.SG,~><v^+*") | set("abcdefghijklmnopqrstuvwxyz") | set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


# [IA] Claude Code (Claude Sonnet 5.5) – importa e valida mapa de arquivo .md/.txt (solto ou em bloco de código)
def map_import(file_path: str | Path) -> Map:
    """Lê um mapa de um arquivo .md/.txt qualquer (caminho absoluto ou relativo).

    O mapa pode estar solto no arquivo ou dentro de um bloco de código (```).
    Linhas em branco e as cercas ``` são ignoradas. Levanta ValueError se o
    conteúdo não for um mapa válido.
    """
    try:
        text = Path(file_path).read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("O arquivo não é um texto válido (use .md ou .txt em UTF-8).")
    except OSError as e:
        raise ValueError(f"Não foi possível ler o arquivo ({e.strerror or e}).")
    lines = [
        line.rstrip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("```")
    ]
    if not lines:
        raise ValueError("O arquivo está vazio.")

    for y, line in enumerate(lines, start=1):
        for ch in line:
            if ch not in VALID_SYMBOLS:
                raise ValueError(f"Símbolo inválido {ch!r} na linha {y}.")
    if len({len(line) for line in lines}) != 1:
        raise ValueError("Todas as linhas do mapa devem ter o mesmo tamanho.")

    flat = "".join(lines)
    if flat.count("S") != 1:
        raise ValueError("O mapa deve ter exatamente um início (S).")
    if flat.count("G") != 1:
        raise ValueError("O mapa deve ter exatamente um fim (G).")

    return _parse_map(lines)

def map_save(map: Map, file_path: str = None):
    if not file_path:
        file_path = f"generated_{map.rows}x{map.cols}_{map.start}_{map.end}.txt"

    with open(MAPS_FOLDER / file_path, "w") as file:
        for row in map.matrix:
            row_str = "".join(repr(cell) for cell in row)
            file.write(row_str + "\n")

# [IA] Claude Code (Claude Sonnet 5.5) – importa o mapa e o salva em maps/update/ sem sobrescrever
def map_import_and_save(file_path: str | Path) -> tuple[Map, str]:
    """Importa o mapa (ver map_import) e o salva em maps/update/ como .txt.

    Nunca sobrescreve: se o nome já existe, acrescenta _2, _3... Retorna o mapa
    e o caminho salvo relativo a maps/ (ex.: "update/meu_mapa.txt").
    """
    map = map_import(file_path)
    folder = MAPS_FOLDER / UPDATE_FOLDER
    folder.mkdir(parents=True, exist_ok=True)

    stem = Path(file_path).stem
    name = f"{stem}.txt"
    n = 2
    while (folder / name).exists():
        name = f"{stem}_{n}.txt"
        n += 1

    saved = f"{UPDATE_FOLDER}/{name}"
    map_save(map, saved)
    return map, saved


# [IA] Claude Code (Claude Sonnet 5.5) – lista os mapas já salvos em maps/update/
def list_update_maps() -> list[str]:
    """Mapas já salvos em maps/update/, como caminhos relativos a maps/."""
    folder = MAPS_FOLDER / UPDATE_FOLDER
    if not folder.is_dir():
        return []
    return [f"{UPDATE_FOLDER}/{p.name}" for p in sorted(folder.glob("*.txt"))]
