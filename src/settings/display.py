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

# Estilo arcade das caixas e textos
COLOR_ACCENT = (255, 221, 0)  # amarelo do Pac-Man (item selecionado)
COLOR_BOX_BORDER = (33, 33, 222)  # azul das paredes do Pac-Man
COLOR_SHADOW = (0, 0, 0)

# Fonte .ttf do projeto (ex.: "assets/fonts/PressStart2P.ttf"). Se for None ou o
# arquivo não existir, usa uma fonte monoespaçada em negrito do sistema.
FONT_PATH = "assets/fonts/PressStart2P.ttf"

# Rastro do percurso: uma só cor, e a opacidade (0..255) aumenta a cada passagem pela célula.
# (Se a lista tiver mais de uma cor, a cor também muda por passagem.)
VISIT_COLORS = [(0, 0, 255)]
VISIT_ALPHA_FIRST = 60
VISIT_ALPHA_STEP = 45
VISIT_ALPHA_MAX = 255

# Etapa de exploração (iterações do algoritmo): roxo que fica mais forte a cada nova
# iteração na mesma célula. Passos menores que os do caminho, pois podem passar 5+ vezes.
ITER_COLOR = (255, 0, 255)
ITER_ALPHA_FIRST = 45
ITER_ALPHA_STEP = 32
ITER_ALPHA_MAX = 235
