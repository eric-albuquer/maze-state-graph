from src.settings.map_setup import load_selected_map
from src.metrics.state_degrees import state_degrees, state_degrees_csv

map = load_selected_map()

print(map)
print()
print(state_degrees(map))
print(f"\nCSV salvo em {state_degrees_csv(map)}")
