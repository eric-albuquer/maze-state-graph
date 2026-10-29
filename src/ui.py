import sys
import pygame

from src.map.map import *
from src.settings.display import *
from src.settings.map_setup import load_selected_map
from src.settings.solver_setup import get_solver

pygame.init()
pygame.font.init()

screen_info = pygame.display.Info()
WIDTH = screen_info.current_w
HEIGHT = screen_info.current_h * 0.95
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Graph / Map Visualizer")

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


def cell_to_color(cell: MapTile) -> tuple[int, int, int]:
    for cls, color in COLOR_MAP.items():
        if isinstance(cell, cls):
            return color
    return (0, 0, 0)


map = load_selected_map()

solution = get_solver()(map)

current_cell = map.start
current_steps = 0
current_cost = 0
current_keys = frozenset()
current_ports = set()

visit_counts = {}

MENU_WIDTH = int(WIDTH * MENU_WIDTH_RATIO)
map_area_width = WIDTH - MENU_WIDTH
map_area_height = HEIGHT

cell_size = min(map_area_width / map.cols, map_area_height / map.rows)

offset_x = MENU_WIDTH + (map_area_width - (map.cols * cell_size)) / 2
offset_y = (map_area_height - (map.rows * cell_size)) / 2

font_size = int(cell_size * 1.1)
font = pygame.font.SysFont(None, font_size)

menu_font_size = max(25, int(MENU_WIDTH * 0.09))
menu_title_size = max(30, int(MENU_WIDTH * 0.12))
menu_font = pygame.font.SysFont(None, menu_font_size)
menu_title_font = pygame.font.SysFont(None, menu_title_size)

clock = pygame.time.Clock()
moving = True
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    if moving:
        state_info = solution[current_steps]
        current_cell, current_keys, _ = state_info
        x, y = current_cell

        current_cost += map.matrix[y][x].cost
        visit_counts[current_cell] = visit_counts.get(current_cell, 0) + 1
        
        current_steps += 1

        if current_steps == len(solution):
            moving = False

    x, y = current_cell
    if isinstance(map.matrix[y][x], MapPort):
        current_ports.add(map.matrix[y][x].letter)

    screen.fill(COLOR_BACKGROUND)

    # --- DRAW MAP ---
    for i, row in enumerate(map.matrix):
        for j, cell in enumerate(row):
            color = cell_to_color(cell)
            x = offset_x + (j * cell_size)
            y = offset_y + (i * cell_size)

            cell_rect = pygame.Rect(x, y, cell_size, cell_size)

            pygame.draw.rect(screen, color, cell_rect)

            v_count = visit_counts.get((j, i), 0)
            if v_count > 0:
                overlay_alpha = min(v_count * 80, 240)
                visit_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                visit_surface.fill((255, 0, 0, overlay_alpha))
                screen.blit(visit_surface, (x, y))

            pygame.draw.rect(screen, COLOR_GRID_BORDER, cell_rect, width=1)

            char_str = repr(cell)
            text_surface = font.render(char_str, True, COLOR_TEXT)
            text_rect = text_surface.get_rect()
            text_rect.center = cell_rect.center
            screen.blit(text_surface, text_rect)

    # DRAW PLAYER
    player_x = offset_x + current_cell[0] * cell_size
    player_y = offset_y + current_cell[1] * cell_size
    cell_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    pygame.draw.rect(cell_surface, COLOR_PLAYER, (0, 0, cell_size, cell_size))
    screen.blit(cell_surface, (player_x, player_y))

    # --- DRAW SIDE MENU ---
    menu_rect = pygame.Rect(0, 0, MENU_WIDTH, HEIGHT)
    pygame.draw.rect(screen, COLOR_MENU_BG, menu_rect)
    pygame.draw.line(
        screen, COLOR_GRID_BORDER, (MENU_WIDTH, 0), (MENU_WIDTH, HEIGHT), 3
    )

    margin_x = int(MENU_WIDTH * 0.08)
    start_y = int(HEIGHT * 0.035)
    line_spacing = int(menu_font_size * 1.2)

    title_surf = menu_title_font.render("Control Panel", True, COLOR_MENU_TEXT)
    screen.blit(title_surf, (margin_x, start_y))

    pygame.draw.line(
        screen,
        COLOR_GRID_BORDER,
        (margin_x, start_y + int(menu_title_size * 1.2)),
        (MENU_WIDTH - margin_x, start_y + int(menu_title_size * 1.2)),
        2,
    )

    info_y = start_y + int(menu_title_size * 1.8)

    infos = [
        f"Steps: {current_steps}",
        f"Position: {current_cell}",
        f"Cost: {current_cost}",
        f"Cell visits: {visit_counts.get(current_cell, 0)}x",
    ]

    for text in infos:
        surf = menu_font.render(text, True, COLOR_MENU_TEXT)
        screen.blit(surf, (margin_x, info_y))
        info_y += line_spacing

    info_y += int(menu_font_size * 0.5)
    keys_title_surf = menu_font.render("Keys Collected:", True, COLOR_MENU_TEXT)
    screen.blit(keys_title_surf, (margin_x, info_y))
    info_y += int(line_spacing * 1.2)

    if not current_keys:
        none_surf = menu_font.render("  None", True, (150, 150, 150))
        screen.blit(none_surf, (margin_x, info_y))
    else:
        for key in sorted(current_keys):
            key_text = f"  - Key: {key}" + (" (USED)" if key in current_ports else "")
            key_surf = menu_font.render(key_text, True, (241, 196, 15))
            screen.blit(key_surf, (margin_x, info_y))
            info_y += line_spacing

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
