# [IA] Claude Code (Claude Sonnet 5.5) – arquivo inteiro: layout e tela da árvore de busca em pygame
"""Árvore de busca: cada nó é um estado (posição, chaves, bônus).

O layout é uma função pura (`tree_layout`), sem pygame, para poder ser testada.
A tela (`run_tree_screen`) recebe `screen`, `clock` e as fontes de quem a chama
para não depender do `ui.py` (evita import circular).
"""
import sys
from dataclasses import dataclass

import pygame

from src.map.map_state import MapState

LEVEL_GAP = 40  # distância horizontal entre níveis (unidades do mundo)
LEAF_GAP = 14   # distância vertical entre folhas


@dataclass
class TreeLayout:
    root: MapState
    depth: dict          # estado -> profundidade (raiz = 0)
    y: dict              # estado -> posição ao longo das folhas (eixo vertical na tela)
    children: dict       # estado -> lista de filhos (na ordem de descoberta)
    max_depth: int
    slots: int           # número de folhas (altura total)


def tree_layout(parent: dict) -> TreeLayout:
    """Layout por profundidade (árvore na horizontal): o nível do nó vai da esquerda para a direita;
    as folhas ficam em sequência na vertical, cada pai centralizado entre o primeiro e o último filho. `parent` mapeia estado -> pai
    (raiz -> None) e deve listar cada pai antes dos filhos (ordem de descoberta do algoritmo)."""
    children: dict = {}
    depth: dict = {}
    root = None
    for state, par in parent.items():
        if par is None:
            root = state
            depth[state] = 0
        else:
            depth[state] = depth[par] + 1
            children.setdefault(par, []).append(state)
    if root is None:
        raise ValueError("árvore sem raiz")

    y: dict = {}
    slot = 0
    stack = [(root, False)]  # pós-ordem iterativa (a árvore pode ser profunda)
    while stack:
        node, visited = stack.pop()
        kids = children.get(node)
        if not kids:
            y[node] = float(slot)
            slot += 1
        elif visited:
            y[node] = (y[kids[0]] + y[kids[-1]]) / 2
        else:
            stack.append((node, True))
            for kid in reversed(kids):
                stack.append((kid, False))
    return TreeLayout(root, depth, y, children, max(depth.values()), slot)


def _dim(color, factor=0.45, bg=(14, 14, 40)):
    """Mistura a cor com o fundo (nós fora do caminho ficam esmaecidos)."""
    return tuple(int(c * factor + b * (1 - factor)) for c, b in zip(color, bg))


def run_tree_screen(screen, clock, fps, font, parent, path, node_color, title, legend_draw=None, legend_h=0):
    """Mostra a árvore até ESC. Arrastar com o mouse move; a roda dá zoom; R reenquadra.

    parent: estado -> pai; path: estados do caminho final; node_color(keys) -> RGB;
    legend_draw(y): desenha a legenda das camadas a partir da linha y.
    """
    lay = tree_layout(parent)
    path_set = set(path)
    end_state = path[-1] if path else None
    width, height = screen.get_size()
    header_h = font.get_height() * 2 + 18 + legend_h
    view = pygame.Rect(0, header_h, width, height - header_h)
    colors = {}  # chaves -> (cor cheia, cor esmaecida)

    def colors_of(keys):
        if keys not in colors:
            full = node_color(keys)
            colors[keys] = (full, _dim(full))
        return colors[keys]

    def fit():
        margin = 30
        zx = (view.width - 2 * margin) / max(1, lay.max_depth * LEVEL_GAP)
        zy = (view.height - 2 * margin) / max(1, (lay.slots - 1) * LEAF_GAP)
        return [zx, zy, view.x + margin, view.y + margin]

    cam = fit()  # zoom x, zoom y, deslocamento x, deslocamento y
    dragging = False

    def to_screen(state):
        return (cam[2] + lay.depth[state] * LEVEL_GAP * cam[0], cam[3] + lay.y[state] * LEAF_GAP * cam[1])

    def elbow(par, state):
        """Aresta em ângulo reto: sai do pai para a direita, sobe/desce e segue até o filho."""
        (px, py), (cx, cy) = to_screen(par), to_screen(state)
        mid = (px + cx) / 2
        return [(px, py), (mid, py), (mid, cy), (cx, cy)]

    while True:
        clock.tick(fps)
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key in (pygame.K_r, pygame.K_f):
                    cam = fit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                cam[2] += event.rel[0]
                cam[3] += event.rel[1]
            elif event.type == pygame.MOUSEWHEEL:
                factor = 1.15 ** event.y
                mx, my = mouse
                for axis, m in ((0, mx), (1, my)):  # zoom em torno do mouse
                    cam[axis] *= factor
                    cam[axis + 2] = m - (m - cam[axis + 2]) * factor

        screen.fill((8, 8, 24))
        screen.set_clip(view)
        radius = max(2, min(8, int(min(LEVEL_GAP * cam[0], LEAF_GAP * cam[1]) * 0.35)))
        pos = {}
        for state in parent:
            x, y = to_screen(state)
            if -20 <= x <= width + 20 and view.y - 20 <= y <= view.bottom + 20:
                pos[state] = (x, y)

        # arestas (as do caminho por cima, em destaque)
        for state, par in parent.items():
            if par is None or par in path_set and state in path_set:
                continue
            if state in pos or par in pos:
                pygame.draw.lines(screen, (45, 45, 95), False, elbow(par, state), 1)
        for state in path:
            par = parent.get(state)
            if par is not None and (state in pos or par in pos):
                pygame.draw.lines(screen, (255, 255, 255), False, elbow(par, state), 3)

        hover = None
        best = (radius + 5) ** 2
        for state, (x, y) in pos.items():
            on_path = state in path_set
            full, dim = colors_of(state.keys)
            pygame.draw.circle(screen, full if on_path else dim, (x, y), radius + (2 if on_path else 0))
            d = (x - mouse[0]) ** 2 + (y - mouse[1]) ** 2
            if view.collidepoint(mouse) and d < best:
                best, hover = d, state
        for state, text in ((lay.root, "S"), (end_state, "F")):
            if state in pos:
                x, y = pos[state]
                pygame.draw.circle(screen, (255, 255, 255), (x, y), radius + 5, 2)
                label = font.render(text, True, (255, 255, 255))
                screen.blit(label, (x - label.get_width() // 2, y - radius - 8 - label.get_height()))
        if hover:
            x, y = pos[hover]
            pygame.draw.circle(screen, (255, 255, 255), (x, y), radius + 4, 2)
        screen.set_clip(None)

        # cabeçalho
        pygame.draw.rect(screen, (14, 14, 40), (0, 0, width, header_h))
        pygame.draw.line(screen, (33, 33, 222), (0, header_h), (width, header_h), 2)
        screen.blit(font.render(f"{title} - {len(parent)} estados, profundidade {lay.max_depth}", True, (255, 221, 0)), (10, 6))
        if hover:
            keys = "".join(sorted(hover.keys)) or "-"
            info = f"Nó {hover.pos}  chaves {keys}  nível {lay.depth[hover]}  filhos {len(lay.children.get(hover, []))}"
        else:
            info = "Arraste: mover   Roda: zoom   R: reenquadrar   ESC: voltar   (caminho final em branco)"
        screen.blit(font.render(info, True, (230, 230, 230)), (10, 10 + font.get_height()))
        if legend_draw:
            legend_draw(10 + font.get_height() * 2)
        pygame.display.flip()
