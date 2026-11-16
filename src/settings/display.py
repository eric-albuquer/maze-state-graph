# Configurações visuais da interface (src/ui.py).

FPS = 60

# Largura do menu lateral, como fração da largura da janela (0.22 = 22%)
MENU_WIDTH_RATIO = 0.22

# Cores em RGB (o último valor de COLOR_PLAYER é a transparência, 0..255)
COLOR_BACKGROUND = (8, 8, 24)
COLOR_GRID_BORDER = (30, 30, 70)
COLOR_TEXT = (20, 20, 20)
COLOR_PLAYER = (255, 0, 255, 150)
COLOR_MENU_BG = (14, 14, 40)
COLOR_MENU_TEXT = (230, 230, 230)

# True usa os sprites da pasta sprites/; False usa as cores sólidas
USE_SPRITES = True

# [IA] Claude Code (Claude Sonnet 5.5) – constantes visuais da UI (estilo arcade, fonte)
# Estilo arcade das caixas e textos
COLOR_ACCENT = (255, 221, 0)  # amarelo do Pac-Man (item selecionado)
COLOR_BOX_BORDER = (33, 33, 222)  # azul das paredes do Pac-Man
COLOR_SHADOW = (0, 0, 0)

# Fonte .ttf do projeto (ex.: "assets/fonts/PressStart2P.ttf"). Se for None ou o
# arquivo não existir, usa uma fonte monoespaçada em negrito do sistema.
FONT_PATH = "assets/fonts/PressStart2P.ttf"

# [IA] Claude Code (Claude Sonnet 5.5) – constantes da opacidade progressiva do percurso
# Rastro do percurso: uma só cor, e a opacidade (0..255) aumenta a cada passagem pela célula.
# (Se a lista tiver mais de uma cor, a cor também muda por passagem.)
VISIT_COLORS = [(0, 0, 255)]
VISIT_ALPHA_FIRST = 0
VISIT_ALPHA_STEP = 0
VISIT_ALPHA_MAX = 0

# [IA] Claude Code (Claude Sonnet 5.5) – constantes da etapa de iterações do algoritmo
# Etapa de exploração (iterações do algoritmo): roxo que fica mais forte a cada nova
# iteração na mesma célula. Passos menores que os do caminho, pois podem passar 5+ vezes.
ITER_COLOR = (255, 0, 255)
ITER_ALPHA_FIRST = 45
ITER_ALPHA_STEP = 32
ITER_ALPHA_MAX = 235

# [IA] Claude Code (Claude Sonnet 5.5) – paleta do modo "cor por camada" (tecla L)
# Camada = conjunto de chaves em posse do jogador. Uma cor por camada, na ordem
# (menos chaves primeiro); se houver mais camadas que cores, a paleta se repete.
LAYER_COLORS = [
    (255, 20, 147),   # rosa choque
    (170, 255, 0),    # verde limão
    (0, 229, 255),    # ciano
    (176, 96, 255),   # violeta
    (255, 235, 59),   # amarelo
    (0, 255, 160),    # verde menta
    (255, 255, 255),  # branco
    (0, 80, 255),     # azul royal
]

# [IA] Claude Code (Claude Sonnet 5.5) – opacidade fixa (0..255) no modo cor por camada,
# para a cor da camada não ficar escura/misturada pela opacidade progressiva das visitas.
LAYER_ITER_ALPHA = 80
LAYER_PATH_ALPHA = 150


# [IA] Claude Code (Claude Sonnet 5.5) – gera cores para qualquer quantidade de camadas
def layer_palette(n: int) -> list[tuple[int, int, int]]:
    """Devolve n cores distintas: primeiro as de LAYER_COLORS; as extras são geradas
    espaçando o matiz pelo ângulo áureo (cores vizinhas ficam bem separadas) e
    alternando brilho e saturação para não repetir tons parecidos."""
    import colorsys

    colors = list(LAYER_COLORS[:n])
    hue = 0.0
    for k in range(n - len(colors)):
        hue = (hue + 0.61803398875) % 1.0
        sat = (1.0, 0.65)[k % 2]
        val = (1.0, 0.8, 0.9)[k % 3]
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        colors.append((round(r * 255), round(g * 255), round(b * 255)))
    return colors
