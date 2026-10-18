from map.map import *

DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))

def solve_bellman_ford(map: Map):
    initial_state = (map.start, frozenset(), frozenset())
    
    prev_map = {initial_state: None}
    cost_map = {initial_state: 0}

    end_state = None
    end_cost = float("inf")

    def bellman_ford_iteration():
        nonlocal end_state, end_cost

        changed = False
        nodes = list(cost_map.items())
        for state, cost in nodes:
            (x, y), keys, bonus_visited = state
            node = map.matrix[y][x]

            if (x, y) == map.end and cost < end_cost:
                end_cost = cost
                end_state = state

            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                cell = map.matrix[ny][nx]
                if isinstance(cell, MapWall):
                    continue
                if isinstance(cell, MapPort) and cell.letter not in keys:
                    continue
                if isinstance(node, MapFloorDirected) and node.dir_vec != (dx, dy):
                    continue

                next_cost = cost + cell.cost
                next_bonus_visited = bonus_visited
                next_keys = keys

                if isinstance(cell, MapBonus):
                    if (nx, ny) in bonus_visited:
                        next_cost = cost + 1
                    else:
                        next_bonus_visited = bonus_visited | {(nx, ny)}
                elif isinstance(cell, MapKey):
                    next_keys = keys | {cell.letter}

                next_state = ((nx, ny), next_keys, next_bonus_visited)

                if next_cost >= cost_map.get(next_state, float("inf")):
                    continue

                prev_map[next_state] = state
                cost_map[next_state] = next_cost
                changed = True

        return changed

    max_iterations = map.stats.floor_count * (2 ** len(map.stats.keys)) * (2 ** map.stats.bonus_count)

    for _ in range(max_iterations - 1):
        if not bellman_ford_iteration():
            break

    if bellman_ford_iteration():
        print("loop detected")
    
    curr = end_state
    path = []

    while curr:
        cost = cost_map[curr]
        path.append((curr, cost))
        curr = prev_map[curr]

    return path[::-1]