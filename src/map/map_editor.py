# [IA] Claude Code (Claude Sonnet 5.5) – arquivo inteiro: lógica pura do editor de mapas da UI (sem pygame), para poder ser testada

MIN_SIZE = 5
MAX_ROWS = 61
MAX_COLS = 101


def parse_size(text: str, lo: int, hi: int, label: str) -> int:
    """Converte o texto digitado em um tamanho válido (inteiro entre lo e hi)."""
    text = text.strip()
    if not text:
        raise ValueError(f"Digite o número de {label}.")
    if not text.isdigit():
        raise ValueError(f"O número de {label} deve ser um inteiro, só com dígitos.")
    value = int(text)
    if not lo <= value <= hi:
        raise ValueError(f"O número de {label} deve estar entre {lo} e {hi}.")
    return value


def new_grid(rows: int, cols: int) -> list[list[str]]:
    """Mapa vazio: borda de paredes, miolo de chão, S no canto de cima e G no de baixo."""
    if rows < MIN_SIZE or cols < MIN_SIZE:
        raise ValueError(f"O mapa deve ter pelo menos {MIN_SIZE} x {MIN_SIZE}.")
    if rows > MAX_ROWS or cols > MAX_COLS:
        raise ValueError(f"O mapa deve ter no máximo {MAX_ROWS} linhas e {MAX_COLS} colunas.")
    grid = [["#"] * cols]
    grid += [["#"] + ["."] * (cols - 2) + ["#"] for _ in range(rows - 2)]
    grid.append(["#"] * cols)
    grid[1][1] = "S"
    grid[rows - 2][cols - 2] = "G"
    return grid


def is_editable(grid: list[list[str]], x: int, y: int) -> bool:
    """A borda não pode ser alterada (o solver não confere os limites da grade)."""
    return 0 < y < len(grid) - 1 and 0 < x < len(grid[0]) - 1


def paint(grid: list[list[str]], x: int, y: int, symbol: str) -> bool:
    """Coloca o símbolo na casa. S e G são únicos: pintar um novo move o anterior.
    Retorna False se a casa não pode ser alterada."""
    if not is_editable(grid, x, y):
        return False
    if symbol in ("S", "G"):
        for row in grid:
            for i, cell in enumerate(row):
                if cell == symbol:
                    row[i] = "."
    grid[y][x] = symbol
    return True


def erase(grid: list[list[str]], x: int, y: int) -> bool:
    """Apaga a casa (vira chão)."""
    return paint(grid, x, y, ".")


def grid_to_lines(grid: list[list[str]]) -> list[str]:
    return ["".join(row) for row in grid]
