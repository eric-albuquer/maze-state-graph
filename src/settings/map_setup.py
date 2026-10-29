from src.map.map import Map
from src.map.map_generator import generate_map
from src.map.map_loader import map_load, map_save

# Legenda do MAP_CHOICE (qual mapa será usado):
#   0 = mapa gerado (usa GENERATOR_PARAMS)
#   1 = m01_terreno.txt
#   2 = m02_uma_chave.txt
#   3 = m03_tres_chaves.txt
#   4 = m04_esteiras.txt
#   5 = m05_bonus.txt
#   6 = m06_fonte.txt
#   7 = m07_impossivel.txt
#   8 = m08_grande.txt

GENERATED = 0  # não altere: é o valor do MAP_CHOICE que significa "mapa gerado"
MAP_CHOICE = 6

# Legenda do SAVE_GENERATED (só vale quando MAP_CHOICE == GENERATED):
#   0 = não salva o mapa gerado
#   1 = salva o mapa gerado em maps/ (chama map_save)
SAVE_GENERATED = 0

MAPS = {
    1: "m01_terreno.txt",
    2: "m02_uma_chave.txt",
    3: "m03_tres_chaves.txt",
    4: "m04_esteiras.txt",
    5: "m05_bonus.txt",
    6: "m06_fonte.txt",
    7: "m07_impossivel.txt",
    8: "m08_grande.txt",
}

# Legenda do GENERATOR_PARAMS (só vale quando MAP_CHOICE == GENERATED):
#   rows, cols              = tamanho do mapa (linhas x colunas)
#   strategy                = algoritmo que gera o labirinto (ex.: "backtracking")
#   keys                    = chaves do mapa; cada uma cria a porta correspondente
#   braid_factor            = 0..1, fração de becos sem saída removidos (0 = labirinto perfeito)
#   water_density           = 0..1, fração de células de água
#   mud_density             = 0..1, fração de células de lama
#   source_density          = 0..1, fração de células de fonte
#   bonus_density           = 0..1, fração de células de bônus
#   floor_directed_density  = 0..1, fração de esteiras direcionadas
GENERATOR_PARAMS = dict(
    rows=31,
    cols=43,
    strategy="backtracking",
    keys=["a", "b", "c", "d"],
    braid_factor=0.00,
    water_density=0.04,
    mud_density=0.04,
    source_density=0.0,
    bonus_density=0.005,
    floor_directed_density=0.01,
)


def load_selected_map() -> Map:
    if MAP_CHOICE == GENERATED:
        map = generate_map(**GENERATOR_PARAMS)
        if SAVE_GENERATED:
            map_save(map)
        return map
    if MAP_CHOICE in MAPS:
        return map_load(MAPS[MAP_CHOICE])
    raise ValueError(
        f"MAP_CHOICE inválido: {MAP_CHOICE} (use {GENERATED} ou 1..{len(MAPS)})"
    )
