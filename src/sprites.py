# [IA] Claude Code (Claude Sonnet 5.5) – arquivo inteiro: carregamento, cache e escolha dos sprites usados pela UI em pygame
from pathlib import Path

import pygame

from src.map.map_nodes import *

SPRITES_DIR = Path(__file__).resolve().parent.parent / "sprites"

# Cada tipo de célula vira uma lista de camadas (da de baixo para a de cima).
FLOOR = "chao.png"
TILE_LAYERS = {
    MapWall: ["parede.png"],
    MapDotFloor: [FLOOR],
    MapStart: [FLOOR],
    MapEnd: [FLOOR, "saida.png"],
    MapMud: [FLOOR, "lama.png"],
    MapWater: [FLOOR, "agua.png"],
    MapSource: [FLOOR, "fonte.png"],
    MapBonus: [FLOOR, "bonus.png"],
    MapKey: [FLOOR, "chave.png"],
    MapPort: ["porta.png"],
}
ARROWS = {
    (0, -1): "seta_cima.png",
    (0, 1): "seta_baixo.png",
    (-1, 0): "seta_esquerda.png",
    (1, 0): "seta_direita.png",
}
PLAYER_NAMES = {
    (0, -1): "Up",
    (0, 1): "Down",
    (-1, 0): "Left",
    (1, 0): "Right",
}

# [IA] Claude Code (Claude Sonnet 5.5) – escala de exibição por sprite (número ou largura/altura), centralizada na célula
# Fração da célula que cada sprite ocupa (1.0 = célula inteira; padrão se omitido).
# Chave = caminho relativo a sprites/. O sprite é centralizado na célula.
# Aceita um número (mesma escala nos dois eixos) ou (largura, altura).
SPRITE_SCALE = {
    "bonus.png": 0.7,
    "chave.png": 0.8,
    "fonte.png": 0.9,
    "saida.png": 0.8,
    "lama.png": 0.6,
    "agua.png": (1.0, 0.50),  # (largura, altura)
    "seta_cima.png": 0.5,
    "seta_baixo.png": 0.5,
    "seta_esquerda.png": 0.5,
    "seta_direita.png": 0.5,
}
DEFAULT_PLAYER_SCALE = 0.8  # aplicado a pacman/*.png

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
        if img is None:
            _scaled[key] = None
        else:
            scale = SPRITE_SCALE.get(name, DEFAULT_PLAYER_SCALE if name.startswith("pacman/") else 1.0)
            sx, sy = scale if isinstance(scale, tuple) else (scale, scale)
            w, h = max(1, round(size * sx)), max(1, round(size * sy))
            scaled = pygame.transform.smoothscale(img, (w, h))
            if (w, h) == (size, size):
                _scaled[key] = scaled
            else:
                canvas = pygame.Surface((size, size), pygame.SRCALPHA)
                canvas.blit(scaled, ((size - w) // 2, (size - h) // 2))
                _scaled[key] = canvas
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
