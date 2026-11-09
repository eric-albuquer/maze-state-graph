from src.map.map_generator import generate_map
from src.map.map_loader import map_save

GENERATOR_PARAMS = dict(
    rows=15,
    cols=11,
    strategy="backtracking",
    keys=["a", "b", "c"],
    braid_factor=0.00,
    water_density=0.03,
    mud_density=0.03,
    source_density=0.0,
    bonus_density=0.01,
    floor_directed_density=0.20,
)


def gerar_mapa():
    map = generate_map(**GENERATOR_PARAMS)
    map_save(map)
    print(f"Mapa salvo em maps/generated_{map.rows}x{map.cols}_{map.start}_{map.end}.txt")
    return map


if __name__ == "__main__":
    gerar_mapa()
