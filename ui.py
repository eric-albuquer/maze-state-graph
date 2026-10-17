import sys
import pygame

from map.map import *
from map.map_generator import generate_map
from map.map_loader import map_load
from solver.solver import solve

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visualizador de Grafos / Mapas")

COLOR_BACKGROUND = (24, 28, 36)
COLOR_GRID_BORDER = (40, 44, 52)
COLOR_TEXT = (20, 20, 20)

COLOR_MAP = {
    MapStart: (46, 204, 113),           # Verde Suave
    MapEnd: (231, 76, 60),              # Vermelho / Laranja
    MapSource: (155, 89, 182),          # Roxo
    MapKey: (241, 196, 15),             # Amarelo Ouro
    MapPort: (127, 140, 141),           # Cinza
    MapMud: (160, 82, 45),              # Marrom Terra
    MapWater: (52, 152, 219),           # Azul
    MapBonus: (230, 126, 34),           # Laranja
    MapDotFloor: (236, 240, 241),       # Branco Off-white
    MapFloorDirected: (26, 188, 156)    # Verde Turquesa / Ciano
}

def cell_to_color(cell: MapTile) -> tuple[int, int, int]:
    """Retorna a cor associada à classe da célula respeitando a hierarquia de herança."""
    for cls, color in COLOR_MAP.items():
        if isinstance(cell, cls):
            return color
    return (0, 0, 0)

#map = map_load("m03_tres_chaves.txt")
map = generate_map(
    rows=41,
    cols=41, 
    algorithm="recursive_division", 
    keys=["a","b","c","d","e","f"],
    loop_density = 0.05,
    water_density= 0.05, 
    mud_density= 0.05, 
    source_density= 0, 
    bonus_density= 0.02, 
    floor_directed_density=0.05
)

cell_size = min(WIDTH / map.cols, HEIGHT / map.rows)

offset_x = (WIDTH - (map.cols * cell_size)) / 2
offset_y = (HEIGHT - (map.rows * cell_size)) / 2

font_size = int(cell_size * 1.2)
font = pygame.font.SysFont(None, font_size)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill(COLOR_BACKGROUND)

    for i, row in enumerate(map.matrix):
        for j, cell in enumerate(row):
            color = cell_to_color(cell)
            x = offset_x + (j * cell_size)
            y = offset_y + (i * cell_size)

            cell_rect = pygame.Rect(x, y, cell_size, cell_size)
            
            pygame.draw.rect(screen, color, cell_rect)
            pygame.draw.rect(screen, COLOR_GRID_BORDER, cell_rect, width=1)

            char_str = repr(cell)
            text_surface = font.render(char_str, True, COLOR_TEXT)
            text_rect = text_surface.get_rect()
            
            text_rect.center = cell_rect.center
            
            screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()