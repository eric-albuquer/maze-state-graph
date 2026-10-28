from src.settings.map_setup import load_selected_map
from src.metrics.state_degrees import state_degrees

map = load_selected_map()

print(map)
print()
print(state_degrees(map))
