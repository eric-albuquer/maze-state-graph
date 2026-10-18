from map.map import *
import heapq

DIR = ((0, -1), (1, 0), (0, 1), (-1, 0))


def heuristic(pos, end):
    return abs(pos[0] - end[0]) + abs(pos[1] - end[1])


def solve_astar(map: Map) -> list[tuple[int, int]] | None:
    start_state = (map.start, frozenset(), frozenset())

    best_cost_map = {start_state: 0}
    best_step_map = {start_state: 0}
    prev_map = {start_state: None}

    h_start = heuristic(map.start, map.end)
    heap = [(h_start, 0, 0, map.start[0], map.start[1], frozenset(), frozenset())]
    # state -> (pos, keys, bonus_visited)

    while heap:
        _, cost, steps, x, y, keys, bonus_visited = heapq.heappop(heap)
        state = ((x, y), keys, bonus_visited)

        if cost > best_cost_map.get(state, float("inf")):
            continue

        curr_node = map.matrix[y][x]

        if (x, y) == map.end:
            curr = state
            path = []
            while curr:
                final_cost = best_cost_map[curr]
                path.append((curr, final_cost))
                curr = prev_map[curr]
            return path[::-1]

        next_steps = steps + 1

        for dx, dy in DIR:
            nx, ny = x + dx, y + dy

            node = map.matrix[ny][nx]
            if isinstance(node, MapWall):
                continue
            if (
                isinstance(curr_node, MapFloorDirected)
                and (dx, dy) != curr_node.dir_vec
            ):
                continue
            if isinstance(node, MapPort) and node.letter not in keys:
                continue

            new_keys = keys
            new_bonus_visited = bonus_visited
            new_cost = cost + node.cost

            if isinstance(node, MapKey):
                new_keys = keys | {node.letter}
            elif isinstance(node, MapBonus):
                if (nx, ny) in bonus_visited:
                    new_cost += 5
                else:
                    new_bonus_visited = bonus_visited | {(nx, ny)}

            new_state = ((nx, ny), new_keys, new_bonus_visited)

            if best_cost_map.get(new_state, float("inf")) <= new_cost:
                continue

            best_cost_map[new_state] = new_cost
            best_step_map[new_state] = next_steps
            prev_map[new_state] = state

            priority = new_cost + heuristic((nx, ny), map.end)
            heapq.heappush(
                heap,
                (priority, new_cost, next_steps, nx, ny, new_keys, new_bonus_visited),
            )

    return None
