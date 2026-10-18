from collections import deque
from map.map import *

DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))

def solve_bfs(map: Map):
    initial_state = (map.start, frozenset(), frozenset())

    queue = deque([(0, initial_state)])
    prev_map = {initial_state: None}
    cost_map = {initial_state: 0}

    while queue:
        cost, state = queue.popleft()
        (x, y), keys, bonus_visited = state

        node = map.matrix[y][x]

        if (x, y) == map.end:
            if state not in prev_map:
                return []
            
            curr = state
            path = []
        
            while curr:
                cost = cost_map[curr]
                path.append((curr, cost))
                curr = prev_map[curr]
        
            return path[::-1]

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

            if next_state in prev_map:
                continue

            prev_map[next_state] = state
            cost_map[next_state] = next_cost

            queue.append((next_cost, next_state))

    return []