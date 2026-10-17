from map.map import *
import heapq

dir = (
    (0, -1),
    (1, 0),
    (0, 1),
    (-1, 0)
)

def solve(map: Map) -> list[tuple[int, int]] | None:
    best_cost_map = {(map.start, frozenset(), frozenset()): 0}
    prev_map = {(map.start, frozenset(), frozenset()): None}
    heap = [(0, map.start, frozenset(), frozenset())]
    # state -> (pos, keys, bonus_visited)

    while heap:
        cost, (x, y), keys, bonus_visited = heapq.heappop(heap)
        state = ((x, y), keys, bonus_visited)

        curr_node = map.matrix[y][x]

        if (x, y) == map.end and best_cost_map[state] == cost:
            cur = state
            path = []
            while cur:
                path.append((cur, best_cost_map[cur]))
                cur = prev_map[cur]
            return path[::-1]

        for dx, dy in dir:
            nx, ny = x + dx, y + dy
            node = map.matrix[ny][nx]
            if isinstance(node, MapWall):
                continue
            if isinstance(curr_node, MapFloorDirected) and (dx, dy) != curr_node.dir_vec:
                continue
            if isinstance(node, MapPort) and node.letter not in keys:
                continue
            new_keys = keys
            new_bonus_visited = bonus_visited
            new_cost = cost + node.cost
            if isinstance(node, MapKey):
                new_keys |= {node.letter}
            elif isinstance(node, MapBonus):
                if (nx, ny) in bonus_visited:
                    new_cost += 5
                else:
                    new_bonus_visited |= {(nx, ny)}
            new_state = ((nx, ny), new_keys, new_bonus_visited)
            if best_cost_map.get(new_state, float("inf")) <= new_cost:
                continue
            best_cost_map[new_state] = new_cost
            prev_map[new_state] = state

            heapq.heappush(heap, (new_cost, *new_state))

    return None