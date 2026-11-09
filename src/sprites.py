# [IA] Claude Code (Claude Sonnet 5.5) – arquivo inteiro: carregamento, cache e escolha dos sprites usados pela UI em pygame
from pathlib import Path

import pygame

from src.map.map_nodes import *

SPRITES_DIR = Path(__file__).resolve().parent.parent / "sprites"

# Cada tipo de célula vira uma lista de camadas (da de baixo para a de cima).
FLOOR = "luxuria/chao.png"
TILE_LAYERS = {
    MapWall: ["luxuria/parede.png"],
    MapDotFloor: [FLOOR],
    MapStart: [FLOOR],
    MapEnd: [FLOOR, "icon.png"],
    MapMud: ["gula/lama.png"],
    MapWater: ["common_cells/ice.png"],
    MapSource: [FLOOR, "common_cells/fonte.png"],
    MapBonus: [FLOOR, "itens/coin1.png"],
    MapKey: [FLOOR, "itens/newKey.png"],
    MapPort: ["common_cells/cobblestone.png"],
}
ARROWS = {
    (0, -1): "luxuria/UpArrow1.png",
    (0, 1): "luxuria/DownArrow1.png",
    (-1, 0): "luxuria/LeftArrow1.png",
    (1, 0): "luxuria/RightArrow1.png",
}
PLAYER_NAMES = {
    (0, -1): "Up",
    (0, 1): "Down",
    (-1, 0): "Left",
    (1, 0): "Right",
}

_originals: dict[str, pygame.Surface | None] = {}
_scaled: dict[tuple[str, int], pygame.Surface | None] = {}


def _load(name: str) -> pygame.Surface | None:
    if name not in _originals:
        try:
            _originals[name] = pygame.image.load(SPRITES_DIR / name).convert_alpha()
        except (FileNotFoundError, pygame.error):
            _originals[name] = None
    return _originals[name]


def get_sprite(name: str, size: int) -> pygame.Surface | None:
    """Sprite redimensionado para size x size (cacheado). None se não existir."""
    key = (name, size)
    if key not in _scaled:
        img = _load(name)
        _scaled[key] = pygame.transform.smoothscale(img, (size, size)) if img else None
    return _scaled[key]


def tile_sprites(cell: MapTile, size: int) -> list[pygame.Surface] | None:
    """Camadas do tile, ou None se algum sprite faltar (usa-se a cor)."""
    if isinstance(cell, MapFloorDirected):
        names = [FLOOR, ARROWS[cell.dir_vec]]
    else:
        names = next((n for cls, n in TILE_LAYERS.items() if isinstance(cell, cls)), None)
    if not names:
        return None
    layers = [get_sprite(n, size) for n in names]
    return None if any(l is None for l in layers) else layers


def player_sprite(direction: tuple[int, int], frame: int, size: int):
    name = f"pacman/pacman{PLAYER_NAMES.get(direction, 'Right')}{frame % 2 + 1}.png"
    return get_sprite(name, size)
