import math
import queue
import sys
import threading
import time
from pathlib import Path
import pygame

from src.map.map import *
from src.map.map_generator import MapGenerationCancelled
from src.settings.display import *
from src.sprites import tile_sprites, player_sprite
from src.settings.map_setup import MAPS, GENERATED, GENERATOR_PARAMS, load_map
from src.settings.solver_setup import SOLVER_NAMES, get_solver

pygame.init()
pygame.font.init()

screen_info = pygame.display.Info()
WIDTH = screen_info.current_w
HEIGHT = int(screen_info.current_h * 0.95)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Graph / Map Visualizer")
clock = pygame.time.Clock()

COLOR_MAP = {
    MapDotFloor: (236, 240, 241),  # Off-white
    MapStart: (46, 204, 113),  # Soft Green
    MapEnd: (231, 76, 60),  # Red / Orange
    MapSource: (155, 89, 182),  # Purple
    MapKey: (241, 196, 15),  # Gold Yellow
    MapPort: (127, 140, 141),  # Gray
    MapMud: (160, 82, 45),  # Earth Brown
    MapWater: (52, 152, 219),  # Blue
    MapBonus: (230, 126, 34),  # Orange
    MapFloorDirected: (26, 188, 156),  # Turquoise / Cyan
}

COLOR_SELECTED = (52, 152, 219)
COLOR_HINT = (150, 150, 150)

# [IA] Claude Code (Claude Sonnet 5.5) – estilo visual da UI em pygame: fonte do projeto e tamanhos de título/item/dica
FONT_FILE = Path(__file__).resolve().parent.parent / FONT_PATH if FONT_PATH else None


def make_font(size: int) -> pygame.font.Font:
    """Fonte do projeto (FONT_PATH) ou, se não existir, monoespaçada em negrito."""
    if FONT_FILE and FONT_FILE.exists():
        return pygame.font.Font(str(FONT_FILE), max(6, int(size * 0.62)))
    return pygame.font.SysFont("monaco,menlo,couriernew", max(6, int(size * 0.75)), bold=True)


title_font = make_font(80)
item_font = make_font(44)
hint_font = make_font(28)


# [IA] Claude Code (Claude Sonnet 5.5) – estilo visual da UI em pygame: caixas estilo arcade com sombra e borda
def draw_box(rect, selected=False, bg=COLOR_MENU_BG, border=None, shadow=True):
    """Caixa estilo arcade: sombra, borda dupla azul (amarela se selecionada), cantos retos."""
    border = border or (COLOR_ACCENT if selected else COLOR_BOX_BORDER)
    if shadow:
        pygame.draw.rect(screen, COLOR_SHADOW, rect.move(5, 5))
    pygame.draw.rect(screen, bg, rect)
    pygame.draw.rect(screen, border, rect, width=3)
    if rect.width > 30 and rect.height > 30:
        pygame.draw.rect(screen, border, rect.inflate(-10, -10), width=1)


# [IA] Claude Code (Claude Sonnet 5.5) – código em pygame da barra de velocidade (escala logarítmica, ligada aos atalhos CIMA/BAIXO)
MIN_SPEED, MAX_SPEED = 1, 10000


def draw_speed_bar(rect: pygame.Rect, speed: int):
    """Barra de velocidade em escala logarítmica (cada CIMA/BAIXO dobra/divide por 2)."""
    pygame.draw.rect(screen, (4, 4, 14), rect)
    ratio = math.log(speed / MIN_SPEED) / math.log(MAX_SPEED / MIN_SPEED)
    fill = rect.inflate(-4, -4)
    fill.width = max(4, int(fill.width * ratio))
    pygame.draw.rect(screen, COLOR_ACCENT, fill)
    pygame.draw.rect(screen, COLOR_BOX_BORDER, rect, width=2)
    for tick in (1, 5, 10, 30, 60, 120):  # marcas de referência
        tx = rect.x + 2 + int((rect.width - 4) * math.log(tick / MIN_SPEED) / math.log(MAX_SPEED / MIN_SPEED))
        pygame.draw.line(screen, COLOR_BOX_BORDER, (tx, rect.y + 2), (tx, rect.bottom - 3), 1)


def item_color(selected: bool):
    return COLOR_ACCENT if selected else COLOR_MENU_TEXT


def cell_to_color(cell: MapTile) -> tuple[int, int, int]:
    for cls, color in COLOR_MAP.items():
        if isinstance(cell, cls):
            return color
    return (0, 0, 0)


def draw_centered(font, text, color, y, x=None):
    surf = font.render(text, True, color)
    screen.blit(surf, surf.get_rect(center=(WIDTH // 2 if x is None else x, y)))


# ---------------------------------------------------------------- menus


# [IA] Claude Code (Claude Sonnet 5.5) – código em pygame da tela inicial de escolha de mapa e algoritmo, com pré-visualização do mapa
def menu_screen(
    title: str, options: list[str], subtitle: str = "", previews: list | None = None
) -> int | None:
    """Mostra uma lista de opções. Retorna o índice escolhido, ou None se ESC.
    `previews` (opcional) tem um Map (ou None) por opção, mostrado ao lado da lista."""
    cx = WIDTH // 4 + 20 if previews else WIDTH // 2
    preview_area = pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - HEIGHT // 3, WIDTH // 2 - 40, HEIGHT * 2 // 3)
    play_cache = {}
    selected = 0
    item_h = max(36, min(62, (HEIGHT - 260) // len(options)))
    btn_w = WIDTH // 2 - 100 if previews else 520
    top = HEIGHT // 2 - (len(options) * item_h) // 2 + 40
    rects = [
        pygame.Rect(cx - btn_w // 2, top + i * item_h, btn_w, item_h - 10)
        for i in range(len(options))
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return selected
            elif event.type == pygame.MOUSEMOTION:
                for i, r in enumerate(rects):
                    if r.collidepoint(event.pos):
                        selected = i
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, r in enumerate(rects):
                    if r.collidepoint(event.pos):
                        return i

        screen.fill(COLOR_BACKGROUND)
        draw_centered(title_font, title, COLOR_MENU_TEXT, top - 130, cx)
        if subtitle:
            draw_centered(hint_font, subtitle, COLOR_HINT, top - 70, cx)

        for i, (rect, label) in enumerate(zip(rects, options)):
            draw_box(rect, i == selected)
            draw_centered(item_font, label, item_color(i == selected), rect.centery, cx)

        if previews:
            draw_box(preview_area)
            pm = previews[selected]
            if pm is None:
                draw_centered(
                    hint_font, "Sem pré-visualização (mapa aleatório)", COLOR_HINT,
                    preview_area.centery, preview_area.centerx,
                )
            else:
                if selected not in play_cache:
                    play_cache[selected] = Playback(pm, [], None, "")
                play_cache[selected].draw_map(preview_area.inflate(-30, -70).move(0, 15))
                draw_centered(
                    hint_font, f"{pm.rows} x {pm.cols}", COLOR_HINT,
                    preview_area.bottom - 22, preview_area.centerx,
                )

        draw_centered(
            hint_font,
            "Setas ou mouse para navegar  •  Enter/clique para escolher  •  ESC para voltar",
            COLOR_HINT,
            HEIGHT - 30,
        )
        pygame.display.flip()
        clock.tick(30)


# [IA] Claude Code (Claude Sonnet 5.5) – tela de espera em pygame enquanto os solvers rodam em threads (a janela não trava)
def solve_screen(map: Map, solvers: list, labels: list[str]):
    """Roda os solvers em threads (em paralelo) para a janela não travar.
    Retorna uma lista de (solução, erro) ou None se o usuário cancelou."""
    results = [{} for _ in solvers]

    def work(solver, result):
        try:
            result["solution"] = solver(map)
        except Exception as e:  # NotImplementedError, ciclo negativo etc.
            result["error"] = f"{type(e).__name__}: {e}"

    for solver, result in zip(solvers, results):
        threading.Thread(target=work, args=(solver, result), daemon=True).start()

    dots = 0
    while not all("solution" in r or "error" in r for r in results):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None  # as threads ficam rodando em segundo plano (daemon)
        screen.fill(COLOR_BACKGROUND)
        dots = (dots + 1) % 4
        draw_centered(
            title_font, "Resolvendo" + "." * dots, COLOR_MENU_TEXT, HEIGHT // 2 - 40
        )
        for i, (label, r) in enumerate(zip(labels, results)):
            done = "solution" in r or "error" in r
            draw_centered(
                hint_font,
                f"{label}: {'pronto' if done else 'calculando...'}",
                COLOR_MENU_TEXT if done else COLOR_HINT,
                HEIGHT // 2 + 20 + i * 30,
            )
        draw_centered(hint_font, "ESC para cancelar", COLOR_HINT, HEIGHT - 30)
        pygame.display.flip()
        clock.tick(4)

    return [(r.get("solution"), r.get("error")) for r in results]


# [IA] Claude Code (Claude Sonnet 5.5) – código em pygame da seleção de 4 algoritmos para o modo de comparação
def select_screen(title: str, options: list[str], count: int, subtitle: str = ""):
    """Seleção múltipla: o usuário marca exatamente `count` opções.
    Retorna a lista de índices marcados (em ordem), ou None se ESC."""
    chosen = list(range(count))
    cursor = 0
    item_h = 62
    top = HEIGHT // 2 - (len(options) * item_h) // 2 + 40
    rects = [
        pygame.Rect(WIDTH // 2 - 260, top + i * item_h, 520, item_h - 10)
        for i in range(len(options))
    ]

    def toggle(i):
        if i in chosen:
            chosen.remove(i)
        elif len(chosen) < count:
            chosen.append(i)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    cursor = (cursor - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    cursor = (cursor + 1) % len(options)
                elif event.key == pygame.K_SPACE:
                    toggle(cursor)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if len(chosen) == count:
                        return sorted(chosen)
            elif event.type == pygame.MOUSEMOTION:
                for i, r in enumerate(rects):
                    if r.collidepoint(event.pos):
                        cursor = i
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, r in enumerate(rects):
                    if r.collidepoint(event.pos):
                        toggle(i)

        screen.fill(COLOR_BACKGROUND)
        draw_centered(title_font, title, COLOR_MENU_TEXT, top - 130)
        if subtitle:
            draw_centered(hint_font, subtitle, COLOR_HINT, top - 70)
        for i, (rect, label) in enumerate(zip(rects, options)):
            draw_box(rect, i == cursor)
            mark = "[x] " if i in chosen else "[ ] "
            draw_centered(item_font, mark + label, item_color(i == cursor), rect.centery)
        ready = len(chosen) == count
        draw_centered(
            hint_font,
            f"Marcados: {len(chosen)}/{count}"
            + ("  •  Enter para iniciar" if ready else ""),
            COLOR_MENU_TEXT if ready else COLOR_HINT,
            top + len(options) * item_h + 20,
        )
        draw_centered(
            hint_font,
            "Espaço/clique para marcar  •  ESC para voltar",
            COLOR_HINT,
            HEIGHT - 30,
        )
        pygame.display.flip()
        clock.tick(30)


# ------------------------------------------------------- generator config

# [IA] Claude Code (Claude Sonnet 5.5) – código em pygame da tela de parâmetros do mapa gerado (campos, limites e validação da soma das densidades)
STRATEGIES = ["backtracking", "recursive_division", "kruskal", "prim"]
KEY_LETTERS = "abcdefhijklmnopqrtuwxyz"

# (chave, rótulo, mínimo, máximo, passo)
CONFIG_FIELDS = [
    ("rows", "Linhas", 7, 81, 2),
    ("cols", "Colunas", 7, 121, 2),
    ("strategy", "Estratégia", None, None, None),
    ("n_keys", "Nº de chaves", 0, len(KEY_LETTERS), 1),
    ("braid_factor", "Braid (loops)", 0.0, 1.0, 0.05),
    ("water_density", "Água", 0.0, 1.0, 0.01),
    ("mud_density", "Lama", 0.0, 1.0, 0.01),
    ("source_density", "Fontes (*)", 0.0, 1.0, 0.01),
    ("bonus_density", "Bônus (+)", 0.0, 1.0, 0.005),
    ("floor_directed_density", "Esteiras", 0.0, 1.0, 0.005),
]
DENSITY_KEYS = [
    "water_density", "mud_density", "source_density",
    "bonus_density", "floor_directed_density",
]


def default_config() -> dict:
    cfg = dict(GENERATOR_PARAMS)
    cfg["n_keys"] = len(cfg.pop("keys"))
    return cfg


last_config = default_config()


def config_to_params(cfg: dict) -> dict:
    params = {k: v for k, v in cfg.items() if k != "n_keys"}
    params["keys"] = list(KEY_LETTERS[: cfg["n_keys"]])
    return params


def format_value(key: str, value) -> str:
    if key == "strategy":
        return value
    if isinstance(value, float):
        return f"{value * 100:.1f}%" if key != "braid_factor" else f"{value:.2f}"
    return str(value)


def config_screen() -> dict | None:
    """Tela de parâmetros do mapa gerado. Retorna os kwargs de generate_map,
    ou None se o usuário voltou com ESC."""
    global last_config
    cfg = dict(last_config)
    n = len(CONFIG_FIELDS)
    buttons = ["Gerar mapa", "Restaurar padrão"]
    cursor = 0
    item_h = max(30, min(52, (HEIGHT - 190) // (n + len(buttons))))
    top = 100
    rows_rects = [
        pygame.Rect(WIDTH // 2 - 300, top + i * item_h, 600, item_h - 8)
        for i in range(n + len(buttons))
    ]

    def change(i, direction):
        key, _, lo, hi, step = CONFIG_FIELDS[i]
        if key == "strategy":
            idx = STRATEGIES.index(cfg[key])
            cfg[key] = STRATEGIES[(idx + direction) % len(STRATEGIES)]
            return
        v = cfg[key] + direction * step
        v = min(max(v, lo), hi)
        cfg[key] = round(v, 4) if isinstance(step, float) else int(v)

    def total_density():
        return sum(cfg[k] for k in DENSITY_KEYS)

    pygame.key.set_repeat(300, 60)
    try:
        while True:
            too_dense = total_density() > 1.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        last_config = cfg
                        return None
                    elif event.key == pygame.K_UP:
                        cursor = (cursor - 1) % len(rows_rects)
                    elif event.key == pygame.K_DOWN:
                        cursor = (cursor + 1) % len(rows_rects)
                    elif event.key == pygame.K_LEFT and cursor < n:
                        change(cursor, -1)
                    elif event.key == pygame.K_RIGHT and cursor < n:
                        change(cursor, 1)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if cursor == n and not too_dense:
                            last_config = cfg
                            return config_to_params(cfg)
                        elif cursor == n + 1:
                            cfg = default_config()
                        elif cursor < n:
                            change(cursor, 1)
                elif event.type == pygame.MOUSEMOTION:
                    for i, r in enumerate(rows_rects):
                        if r.collidepoint(event.pos):
                            cursor = i
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, r in enumerate(rows_rects):
                        if not r.collidepoint(event.pos):
                            continue
                        cursor = i
                        if i < n:
                            change(i, -1 if event.pos[0] < r.centerx else 1)
                        elif i == n and not too_dense:
                            last_config = cfg
                            return config_to_params(cfg)
                        elif i == n + 1:
                            cfg = default_config()

            screen.fill(COLOR_BACKGROUND)
            draw_centered(title_font, "Parâmetros do mapa", COLOR_MENU_TEXT, top - 60)

            for i, rect in enumerate(rows_rects):
                draw_box(rect, i == cursor)
                tc = item_color(i == cursor)
                if i < n:
                    key, label, *_ = CONFIG_FIELDS[i]
                    screen.blit(
                        item_font.render(label, True, tc),
                        (rect.x + 20, rect.centery - item_font.get_height() // 2),
                    )
                    val = item_font.render(
                        f"<  {format_value(key, cfg[key])}  >", True, tc
                    )
                    screen.blit(val, val.get_rect(midright=(rect.right - 20, rect.centery)))
                else:
                    label = buttons[i - n]
                    color = COLOR_HINT if (i == n and too_dense) else tc
                    draw_centered(item_font, label, color, rect.centery)

            total = total_density()
            msg = f"Soma das densidades: {total * 100:.1f}%"
            if too_dense:
                msg += "  (máximo 100% - reduza para gerar)"
            draw_centered(
                hint_font, msg, (231, 76, 60) if too_dense else COLOR_HINT,
                rows_rects[-1].bottom + 22,
            )
            draw_centered(
                hint_font,
                "Cima/Baixo escolhe  •  Esq/Dir (ou clique nas metades) altera  •  ESC volta",
                COLOR_HINT,
                HEIGHT - 30,
            )
            pygame.display.flip()
            clock.tick(30)
    finally:
        pygame.key.set_repeat()


def generate_map_with_loading(params: dict) -> Map | None:
    """Gera em background; ESC/clique cancela e retorna None."""
    completed = threading.Event()
    cancel_event = threading.Event()
    progress_updates = queue.Queue()
    result = {}

    def generate():
        try:
            result["map"] = load_map(
                GENERATED, params, cancel_event,
                lambda stage, estimate, stage_number, stage_count: progress_updates.put(
                    (stage, estimate, stage_number, stage_count)
                ),
            )
        except Exception as error:
            result["error"] = error
        finally:
            completed.set()

    worker = threading.Thread(target=generate, daemon=True)
    worker.start()
    loading_font = make_font(max(32, int(HEIGHT * 0.05)))
    hint_font = make_font(max(20, int(HEIGHT * 0.03)))
    stage_font = make_font(max(16, int(HEIGHT * 0.022)))
    cancel_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 78, 300, 58)
    current_stage = "Iniciando..."
    stage_number = 0
    stage_count = 0
    estimate = 0.0
    started_at = time.perf_counter()
    estimated_remaining = None
    eta_updated_at = started_at
    frame = 0
    stage_labels = {
        "generate_backtracking": "Construindo o labirinto (backtracking)",
        "generate_recursive_division": "Construindo o labirinto (divisão recursiva)",
        "generate_kruskal": "Construindo o labirinto (Kruskal)",
        "generate_prim": "Construindo o labirinto (Prim)",
        "generate_loops": "Criando ciclos no labirinto",
        "get_cells_by_distance": "Calculando distâncias entre células",
        "generate_key_port": "Distribuindo chaves e portas",
        "get_worst_cell": "Buscando a célula mais distante",
        "generate_floor_direct": "Distribuindo esteiras",
        "generate_floor_variation": "Distribuindo tipos de terreno",
        "compute_stats": "Calculando estatísticas do mapa",
        "Concluído": "Geração concluída",
    }

    def format_duration(seconds: float) -> str:
        seconds = max(0, int(seconds))
        return f"{seconds // 60:02}:{seconds % 60:02}"

    while not completed.is_set():
        while True:
            try:
                stage, estimate, stage_number, stage_count = progress_updates.get_nowait()
                current_stage = stage_labels.get(stage, stage)
                eta_updated_at = time.perf_counter()
                elapsed_at_update = eta_updated_at - started_at
                estimated_remaining = (
                    elapsed_at_update * (1.0 - estimate) / estimate
                    if estimate > 0.05
                    else None
                )
            except queue.Empty:
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cancel_event.set()
                worker.join()
                pygame.quit()
                sys.exit()
            if cancel_event.is_set():
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                cancel_event.set()
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and cancel_button.collidepoint(event.pos)
            ):
                cancel_event.set()

        screen.fill(COLOR_BACKGROUND)
        message = "Cancelando geracao..." if cancel_event.is_set() else "Gerando mapa..."
        draw_centered(loading_font, message, COLOR_MENU_TEXT, HEIGHT // 2 - 105)
        stage_label = (
            f"Etapa {stage_number}/{stage_count} — {current_stage}"
            if stage_count
            else current_stage
        )
        stage_surface = stage_font.render(stage_label, True, COLOR_HINT)
        max_stage_width = WIDTH - 80
        if stage_surface.get_width() > max_stage_width:
            stage_surface = pygame.transform.smoothscale(
                stage_surface,
                (
                    max_stage_width,
                    int(stage_surface.get_height() * max_stage_width / stage_surface.get_width()),
                ),
            )
        screen.blit(stage_surface, stage_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 55)))

        bar = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 - 20, 440, 26)
        pygame.draw.rect(screen, (6, 6, 20), bar)
        fill = bar.inflate(-4, -4)
        progress_width = int(fill.width * min(max(estimate, 0.0), 1.0))
        fill.width = progress_width
        if fill.width:
            pygame.draw.rect(screen, COLOR_ACCENT, fill)
        if not cancel_event.is_set() and estimate < 1.0:
            indicator_x = bar.x + 2 + progress_width
            indicator_width = min(48, bar.right - 2 - indicator_x)
            travel_width = bar.right - 2 - indicator_x - indicator_width
            if indicator_width > 0:
                segment_x = indicator_x + int((frame * 5) % (travel_width + 1))
                pygame.draw.rect(
                    screen, COLOR_ACCENT,
                    (segment_x, fill.y, indicator_width, fill.height),
                )
        pygame.draw.rect(screen, COLOR_BOX_BORDER, bar, width=2)
        now = time.perf_counter()
        elapsed = now - started_at
        percent_label = f"Estimativa: {estimate:.0%}"
        if estimated_remaining is not None:
            remaining = max(0, estimated_remaining - (now - eta_updated_at))
            estimate_label = (
                f"{percent_label}   Decorrido {format_duration(elapsed)}"
                f"   Restante ~{format_duration(remaining)}"
            )
        else:
            estimate_label = f"{percent_label}   Decorrido {format_duration(elapsed)}"
        draw_centered(
            hint_font, estimate_label, COLOR_MENU_TEXT, HEIGHT // 2 + 20
        )
        if not cancel_event.is_set():
            draw_box(cancel_button, bg=(6, 6, 20), border=COLOR_BOX_BORDER, shadow=False)
            draw_centered(
                hint_font, "Cancelar (ESC)", COLOR_MENU_TEXT, cancel_button.centery
            )

        pygame.display.flip()
        clock.tick(FPS)
        frame += 1

    if "error" in result:
        if isinstance(result["error"], MapGenerationCancelled):
            return None
        raise result["error"]
    return result["map"]


# ----------------------------------------------------------- simulation


# [IA] Claude Code (Claude Sonnet 5.5) – animação do percurso em pygame (fase de iterações em roxo e fase do caminho, mesma velocidade para todos os algoritmos)
class Playback:
    """Estado da animação de uma solução (um algoritmo)."""

    def __init__(self, map: Map, solution, error: str | None, label: str):
        """`solution` é um SolverSolution (iterations + path) ou None."""
        self.map = map
        self.iterations = list(solution.iterations) if solution else []
        self.solution = list(solution.path) if solution else []  # o caminho final
        self.error = error
        self.label = label
        self._fonts = {}
        self._bg = None
        self._scene = None
        self.reset()

    def reset(self):
        self.phase = "iterations" if self.iterations else "path"
        self.iter_n = 0
        self.iter_cell = None
        self.iter_visits = {}
        self.step_n = 0
        self.cost = 0
        self.visits = {}
        self.used_ports = set()
        self.cell = self.map.start
        self.direction = (1, 0)
        self.keys = frozenset()
        self.finished = not self.iterations and not self.solution
        self.popup_open = True

    def advance(self):
        if self.finished:
            return

        if self.phase == "iterations":
            # uma iteração por tick, igual para todos os algoritmos
            self.iter_cell = self.iterations[self.iter_n].pos
            self.iter_visits[self.iter_cell] = self.iter_visits.get(self.iter_cell, 0) + 1
            self.iter_n += 1
            if self.iter_n >= len(self.iterations):
                self.iter_cell = None
                if self.solution:
                    self.phase = "path"
                else:
                    self.finished = True
            return

        prev = self.cell
        self.cell, self.keys, _ = self.solution[self.step_n]
        d = (self.cell[0] - prev[0], self.cell[1] - prev[1])
        if d != (0, 0):
            self.direction = d
        x, y = self.cell
        self.cost += self.map.matrix[y][x].cost
        self.visits[self.cell] = self.visits.get(self.cell, 0) + 1
        self.step_n += 1
        if self.step_n == len(self.solution):
            self.finished = True

    def status(self, paused: bool) -> str:
        if self.error:
            return "Erro"
        if self.finished:
            return "Finalizado" if self.solution else "Sem solução"
        if paused:
            return "Pausado"
        return "Explorando" if self.phase == "iterations" else "Caminho"

    def progress_text(self) -> str:
        """Resumo curto do progresso para o cabeçalho dos quadrantes."""
        if self.phase == "iterations" and not self.finished:
            return f"Iter {self.iter_n}/{len(self.iterations)}"
        return f"Passos {self.step_n}/{len(self.solution)}  Custo {self.cost}"

    def _build_background(self, cs: int) -> pygame.Surface:
        """Desenha uma vez o mapa estático (tiles, bordas, letras) em cs x cs por célula."""
        map = self.map
        bg = pygame.Surface((map.cols * cs, map.rows * cs), 0, 24)  # sem canal alfa
        size = max(8, int(cs * 0.8))
        if size not in self._fonts:
            self._fonts[size] = make_font(size)
        font = self._fonts[size]

        for i, row in enumerate(map.matrix):
            for j, cell in enumerate(row):
                cell_rect = pygame.Rect(j * cs, i * cs, cs, cs)
                layers = tile_sprites(cell, cs) if USE_SPRITES else None
                if layers:
                    for layer in layers:
                        bg.blit(layer, cell_rect)
                else:
                    pygame.draw.rect(bg, cell_to_color(cell), cell_rect)
                    pygame.draw.rect(bg, COLOR_GRID_BORDER, cell_rect, width=1)

                # Com sprites, só chaves/portas/início precisam de letra
                if layers is None or isinstance(cell, (MapKey, MapPort, MapStart)):
                    text = font.render(repr(cell), True, COLOR_TEXT if not layers else (255, 255, 255))
                    bg.blit(text, text.get_rect(center=cell_rect.center))
        return bg

    def draw_map(self, rect: pygame.Rect):
        map = self.map
        x, y = self.cell
        if isinstance(map.matrix[y][x], MapPort):
            self.used_ports.add(map.matrix[y][x].letter)

        cs = max(1, int(min(rect.width / map.cols, rect.height / map.rows)))
        ox = rect.x + (rect.width - map.cols * cs) // 2
        oy = rect.y + (rect.height - map.rows * cs) // 2

        if self._bg is None or self._bg[0] != cs:
            self._bg = (cs, self._build_background(cs))

        # [IA] Claude Code (Claude Sonnet 5.5) – código de desenho do rastro com opacidade progressiva (composição em superfície sem alfa)
        # A janela do macOS (cocoa) tem canal alfa: blitar translúcido direto nela
        # NÃO mistura as cores (a opacidade era ignorada). Por isso compomos tudo
        # numa superfície de 24 bits (sem alfa) e só então copiamos para a tela.
        if self._scene is None or self._scene.get_size() != self._bg[1].get_size():
            self._scene = pygame.Surface(self._bg[1].get_size(), 0, 24)
        scene = self._scene
        scene.blit(self._bg[1], (0, 0))
        ox_screen, oy_screen = ox, oy
        ox = oy = 0

        overlay = pygame.Surface((cs, cs), pygame.SRCALPHA)

        # [IA] Claude Code (Claude Sonnet 5.5) – código de desenho das iterações exploradas, com opacidade crescente por visita
        # Etapa 1 (roxo): células exploradas pelo algoritmo, mais forte a cada nova iteração
        r, g, b = ITER_COLOR
        count_size_it = max(8, int(cs * 0.4))
        if count_size_it not in self._fonts:
            self._fonts[count_size_it] = make_font(count_size_it)
        for (j, i), v in self.iter_visits.items():
            alpha = min(ITER_ALPHA_FIRST + (v - 1) * ITER_ALPHA_STEP, ITER_ALPHA_MAX)
            overlay.fill((r, g, b, alpha))
            scene.blit(overlay, (ox + j * cs, oy + i * cs))
            if v > 1:
                text = self._fonts[count_size_it].render(f"{v}x", True, (200, 225, 255))
                scene.blit(text, text.get_rect(bottomleft=(ox + j * cs + 2, oy + (i + 1) * cs - 1)))
        if self.iter_cell is not None:  # célula sendo explorada agora
            j, i = self.iter_cell
            pygame.draw.rect(scene, COLOR_ACCENT, (ox + j * cs, oy + i * cs, cs, cs), width=max(2, cs // 10))

        count_size = max(8, int(cs * 0.45))
        if count_size not in self._fonts:
            self._fonts[count_size] = make_font(count_size)
        count_font = self._fonts[count_size]
        for (j, i), v in self.visits.items():
            alpha = min(VISIT_ALPHA_FIRST + (v - 1) * VISIT_ALPHA_STEP, VISIT_ALPHA_MAX)
            r, g, b = VISIT_COLORS[min(v, len(VISIT_COLORS)) - 1]
            overlay.fill((r, g, b, alpha))
            scene.blit(overlay, (ox + j * cs, oy + i * cs))
            if v > 1:  # passou de novo por aqui: mostra quantas vezes
                text = count_font.render(f"{v}x", True, (255, 255, 255))
                scene.blit(text, text.get_rect(topright=(ox + (j + 1) * cs - 2, oy + i * cs + 1)))

        px, py = ox + self.cell[0] * cs, oy + self.cell[1] * cs
        sprite = player_sprite(self.direction, self.step_n, cs) if USE_SPRITES else None
        if sprite:
            scene.blit(sprite, (px, py))
        else:
            overlay.fill(COLOR_PLAYER)
            scene.blit(overlay, (px, py))
        screen.blit(scene, (ox_screen, oy_screen))


# [IA] Claude Code (Claude Sonnet 5.5) – pop-up em pygame ao fim do algoritmo, com iterações, passos e custo
def draw_popup(p: Playback, area: pygame.Rect, color, title_font, body_font):
    """Caixa centralizada em `area` avisando que o algoritmo terminou."""
    if p.error:
        title, lines = f"{p.label}: erro", [p.error[:50]]
    elif not p.solution:
        title = f"{p.label} terminou"
        lines = ["Sem solução para este mapa", f"Iterações: {len(p.iterations)}"]
    else:
        title = f"{p.label} terminou!"
        lines = [
            f"Iterações: {len(p.iterations)}",
            f"Passos: {len(p.solution)}",
            f"Custo total: {p.cost}",
        ]

    line_h = body_font.get_linesize()
    w = min(area.width - 20, max(280, int(area.width * 0.6)))
    h = title_font.get_linesize() + line_h * (len(lines) + 1) + 30
    box = pygame.Rect(0, 0, w, h)
    box.center = area.center
    draw_box(box, bg=(6, 6, 20), border=color)

    y = box.y + 12
    t = title_font.render(title, True, color)
    screen.blit(t, t.get_rect(centerx=box.centerx, y=y))
    y += title_font.get_linesize() + 4
    for line in lines:
        t = body_font.render(line, True, COLOR_MENU_TEXT)
        screen.blit(t, t.get_rect(centerx=box.centerx, y=y))
        y += line_h
    t = body_font.render("Enter/clique para fechar", True, COLOR_HINT)
    screen.blit(t, t.get_rect(centerx=box.centerx, y=y))


# [IA] Claude Code (Claude Sonnet 5.5) – modo com 4 algoritmos em tela dividida em quadrantes (cores por quadrante)
QUAD_COLORS = [(52, 152, 219), (46, 204, 113), (241, 196, 15), (231, 76, 60)]


# [IA] Claude Code (Claude Sonnet 5.5) – laço de exibição em pygame: painel lateral, 4 quadrantes, barra de velocidade, pausa/reinício e pop-up
def run_simulation(map: Map, plays: list[Playback], map_label: str):
    """Anima 1 solução (painel lateral) ou 4 (tela dividida em quadrantes).
    Retorna ao pressionar ESC."""
    quad = len(plays) > 1

    MENU_WIDTH = int(WIDTH * MENU_WIDTH_RATIO)
    menu_font_size = max(25, int(MENU_WIDTH * 0.09))
    menu_title_size = max(30, int(MENU_WIDTH * 0.12))
    menu_font = make_font( menu_font_size)
    menu_title_font = make_font( menu_title_size)
    quad_font = make_font(max(20, int(HEIGHT * 0.032)))
    popup_title_font = make_font(max(32, int(HEIGHT * 0.05)))
    popup_body_font = make_font(max(24, int(HEIGHT * 0.036)))

    speed = FPS
    paused = False
    step_accumulator = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key in (pygame.K_UP, pygame.K_PLUS, pygame.K_EQUALS):
                    speed = min(speed * 2, MAX_SPEED)
                elif event.key in (pygame.K_DOWN, pygame.K_MINUS):
                    speed = max(speed // 2, MIN_SPEED)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    for p in plays:
                        p.popup_open = False
                elif event.key == pygame.K_r:
                    for p in plays:
                        p.reset()
                    paused = False
                    step_accumulator = 0.0

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for p in plays:
                    p.popup_open = False

        if not paused:
            step_accumulator += dt * speed
            steps = int(step_accumulator)
            step_accumulator -= steps
            for _ in range(steps):
                for p in plays:
                    p.advance()

        screen.fill(COLOR_BACKGROUND)

        if quad:
            half_w, half_h = WIDTH // 2, HEIGHT // 2
            header_h = int(quad_font.get_height() * 2.3)
            for idx, p in enumerate(plays):
                quadrant = pygame.Rect((idx % 2) * half_w, (idx // 2) * half_h, half_w, half_h)
                color = QUAD_COLORS[idx % len(QUAD_COLORS)]
                draw_box(quadrant, bg=COLOR_MENU_BG, border=color, shadow=False)

                line1 = f"{p.label} - {p.status(paused)}"
                if p.error:
                    line2 = p.error[:60]
                else:
                    keys = "".join(sorted(p.keys)) or "-"
                    line2 = f"{p.progress_text()}  Chaves {keys}"
                screen.blit(quad_font.render(line1, True, color), (quadrant.x + 10, quadrant.y + 6))
                screen.blit(
                    quad_font.render(line2, True, COLOR_MENU_TEXT),
                    (quadrant.x + 10, quadrant.y + 6 + quad_font.get_height() * 1.1),
                )
                p.draw_map(pygame.Rect(quadrant.x + 4, quadrant.y + header_h, half_w - 8, half_h - header_h - 4))
                if p.finished and p.popup_open:
                    draw_popup(p, quadrant, color, popup_title_font, popup_body_font)
            bar_w = min(360, WIDTH // 4)
            bar_box = pygame.Rect(WIDTH // 2 - bar_w // 2, HEIGHT // 2 - 24, bar_w, 48)
            draw_box(bar_box, bg=(6, 6, 20), border=COLOR_ACCENT)
            label = quad_font.render(f"Velocidade: {speed} passos/s", True, COLOR_MENU_TEXT)
            screen.blit(label, label.get_rect(midtop=(bar_box.centerx, bar_box.y + 5)))
            draw_speed_bar(pygame.Rect(bar_box.x + 12, bar_box.bottom - 18, bar_w - 24, 10), speed)
        else:
            p = plays[0]
            map_area = pygame.Rect(MENU_WIDTH, 0, WIDTH - MENU_WIDTH, HEIGHT)
            p.draw_map(map_area)

            margin = 8
            pad = 14
            line_spacing = int(menu_font_size * 1.2)
            shortcuts = (
                "ESPACO: pausar",
                "R: reiniciar",
                "CIMA/BAIXO: velocidade",
                "ENTER: fechar aviso",
                "ESC: voltar",
            )
            shortcuts_h = int(menu_title_size * 1.8) + len(shortcuts) * line_spacing + pad
            info_rect = pygame.Rect(margin, margin, MENU_WIDTH - 2 * margin, HEIGHT - shortcuts_h - 3 * margin)
            keys_rect = pygame.Rect(margin, info_rect.bottom + margin, info_rect.width, shortcuts_h)
            inner_w = info_rect.width - 2 * pad

            def put(text, color, x, y):
                """Escreve o texto reduzindo-o se não couber na largura do painel."""
                surf = menu_font.render(text, True, color)
                if surf.get_width() > inner_w:
                    surf = pygame.transform.smoothscale(
                        surf, (inner_w, int(surf.get_height() * inner_w / surf.get_width()))
                    )
                screen.blit(surf, (x, y))

            # --- Painel 1: informações do algoritmo ---
            draw_box(info_rect)
            x0 = info_rect.x + pad
            y = info_rect.y + pad
            screen.blit(menu_title_font.render("Informações", True, COLOR_ACCENT), (x0, y))
            y += int(menu_title_size * 1.5)
            pygame.draw.line(screen, COLOR_BOX_BORDER, (x0, y - 6), (info_rect.right - pad, y - 6), 2)

            infos = [
                f"Mapa: {map_label}",
                f"Algoritmo: {p.label}",
                f"Status: {p.status(paused)}",
                f"Iterações: {p.iter_n}/{len(p.iterations)}",
                f"Passos: {p.step_n}/{len(p.solution)}",
                f"Posição: {p.cell if p.iter_cell is None else p.iter_cell}",
                f"Custo: {p.cost}",
                f"Visitas: {(p.visits.get(p.cell, 0) if p.iter_cell is None else p.iter_visits.get(p.iter_cell, 0))}x",
            ]
            for text in infos:
                put(text, COLOR_MENU_TEXT, x0, y)
                y += line_spacing
            if p.error:
                put(p.error[:40], (231, 76, 60), x0, y)
                y += line_spacing

            put(f"Velocidade: {speed}/s", COLOR_MENU_TEXT, x0, y)
            y += line_spacing - 2
            draw_speed_bar(pygame.Rect(x0, y, inner_w, 16), speed)
            y += 16 + int(menu_font_size * 0.6)
            put("Chaves coletadas:", COLOR_MENU_TEXT, x0, y)
            y += int(line_spacing * 1.2)
            if not p.keys:
                put("  Nenhuma", COLOR_HINT, x0, y)
            else:
                for key in sorted(p.keys):
                    key_text = f"  - Chave {key}" + (" (usada)" if key in p.used_ports else "")
                    put(key_text, COLOR_ACCENT, x0, y)
                    y += line_spacing

            # --- Painel 2: atalhos ---
            draw_box(keys_rect)
            y = keys_rect.y + pad
            screen.blit(menu_title_font.render("Atalhos", True, COLOR_ACCENT), (x0, y))
            y += int(menu_title_size * 1.5)
            pygame.draw.line(screen, COLOR_BOX_BORDER, (x0, y - 6), (keys_rect.right - pad, y - 6), 2)
            for text in shortcuts:
                put(text, COLOR_HINT, x0, y)
                y += line_spacing

            if p.finished and p.popup_open:
                draw_popup(p, map_area, COLOR_ACCENT, popup_title_font, popup_body_font)

        pygame.display.flip()


# ----------------------------------------------------------------- main


# [IA] Claude Code (Claude Sonnet 5.5) – fluxo de telas da UI (mapa, parâmetros, algoritmo, comparação); a geração com carregamento em thread não é da IA
def main():
    map_choices = [GENERATED] + list(MAPS)
    map_labels = ["Mapa gerado aleatório"] + [
        name.removesuffix(".txt") for name in MAPS.values()
    ]
    map_previews = [None] + [load_map(c) for c in map_choices[1:]]
    solver_choices = list(SOLVER_NAMES)
    solver_labels = [SOLVER_NAMES[c] for c in solver_choices]
    compare_label = "Comparar Algoritmos"

    while True:
        m = menu_screen("Escolha o mapa", map_labels, previews=map_previews)
        if m is None:
            break
        params = None
        if map_choices[m] == GENERATED:
            params = config_screen()
            if params is None:
                continue
        try:
            map = (
                generate_map_with_loading(params)
                if map_choices[m] == GENERATED
                else load_map(map_choices[m], params)
            )
        except Exception as e:
            menu_screen("Erro ao gerar o mapa", ["Voltar"], subtitle=str(e)[:110])
            continue
        if map is None:
            continue

        while True:
            s = menu_screen(
                "Escolha o algoritmo",
                solver_labels + [compare_label],
                subtitle=f"Mapa: {map_labels[m]}",
            )
            if s is None:
                break

            if s == len(solver_labels):
                picked = select_screen(
                    "Escolha 4 Algoritmos",
                    solver_labels,
                    count=4,
                    subtitle=f"Mapa: {map_labels[m]}",
                )
                if picked is None:
                    continue
            else:
                picked = [s]

            labels = [solver_labels[i] for i in picked]
            out = solve_screen(
                map, [get_solver(solver_choices[i]) for i in picked], labels
            )
            if out is None:
                continue
            plays = [
                Playback(map, solution, error, label)
                for (solution, error), label in zip(out, labels)
            ]
            run_simulation(map, plays, map_labels[m])

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
