from src.map.map import *
import random
from threading import Event
from collections import deque, defaultdict
from typing import Callable, Literal

DIR_DOUBLE = [(0, -2), (2, 0), (0, 2), (-2, 0)]
DIR = [(0, -1), (1, 0), (0, 1), (-1, 0)]
SearchState = tuple[tuple[int, int], int]


class MapGenerationCancelled(Exception):
    """Raised when map generation is cancelled by the caller."""


def _check_cancel(cancel_event: Event | None):
    if cancel_event is not None and cancel_event.is_set():
        raise MapGenerationCancelled("Map generation cancelled")


def _report_progress(
    progress_callback: Callable[[str, float, int, int], None] | None,
    stage: str,
    estimate: float,
    stage_number: int,
    stage_count: int,
):
    if progress_callback is not None:
        progress_callback(stage, estimate, stage_number, stage_count)


class DisjointSet:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, val):
        if val not in self.parent:
            self.parent[val] = val
            self.rank[val] = 0
            return val

        if val != self.parent[val]:
            self.parent[val] = self.find(self.parent[val])
        return self.parent[val]

    def union(self, a, b) -> bool:
        root_a = self.find(a)
        root_b = self.find(b)

        if root_a == root_b:
            return False

        if self.rank[root_a] < self.rank[root_b]:
            self.parent[root_b] = root_a
        elif self.rank[root_b] < self.rank[root_a]:
            self.parent[root_a] = root_b
        else:
            self.rank[root_a] += 1
            self.parent[root_b] = root_a

        return True


def generate_backtracking(rows, cols, cancel_event=None):
    matrix = [[MapWall(x, y) for x in range(cols)] for y in range(rows)]

    sx, sy = (
        random.randint(0, (cols // 2) - 1) * 2 + 1,
        random.randint(0, (rows // 2) - 1) * 2 + 1,
    )

    stack = [(sx, sy)]
    matrix[sy][sx] = MapDotFloor(sx, sy)

    while stack:
        _check_cancel(cancel_event)
        x, y = stack[-1]

        neighbors = []
        for dx, dy in DIR_DOUBLE:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= cols or ny < 0 or ny >= rows:
                continue
            if isinstance(matrix[ny][nx], MapDotFloor):
                continue
            neighbors.append((nx, ny))

        if not neighbors:
            stack.pop()
            continue

        cx, cy = random.choice(neighbors)
        mx, my = (x + cx) // 2, (y + cy) // 2
        matrix[cy][cx] = MapDotFloor(cx, cy)
        matrix[my][mx] = MapDotFloor(mx, my)

        stack.append((cx, cy))

    return matrix


def generate_recursive_division(rows, cols, cancel_event=None):
    matrix = [[MapDotFloor(x, y) for x in range(cols)] for y in range(rows)]

    for i in range(rows):
        matrix[i][0] = MapWall(0, i)
        matrix[i][cols - 1] = MapWall(cols - 1, i)

    for i in range(cols):
        matrix[0][i] = MapWall(i, 0)
        matrix[rows - 1][i] = MapWall(i, rows - 1)

    stack = [(1, 1, cols - 2, rows - 2)]

    while stack:
        _check_cancel(cancel_event)
        x0, y0, x1, y1 = stack.pop()
        width = x1 - x0
        height = y1 - y0

        if width <= 1 or height <= 1:
            continue

        choose_vertical = (
            width > height if width != height else random.choice([True, False])
        )

        if choose_vertical:
            min_even = x0 + 1 if (x0 + 1) % 2 == 0 else x0 + 2
            max_even = x1 - 1 if (x1 - 1) % 2 == 0 else x1 - 2
            if min_even > max_even:
                continue
            choosed_x = random.randint(min_even // 2, max_even // 2) * 2
            for i in range(y0, y1 + 1):
                _check_cancel(cancel_event)
                matrix[i][choosed_x] = MapWall(choosed_x, i)
            min_odd = y0 if y0 % 2 != 0 else y0 + 1
            max_odd = y1 if y1 % 2 != 0 else y1 - 1
            open_idx = random.randint((min_odd - 1) // 2, (max_odd - 1) // 2) * 2 + 1
            matrix[open_idx][choosed_x] = MapDotFloor(choosed_x, open_idx)
            stack.append((x0, y0, choosed_x - 1, y1))
            stack.append((choosed_x + 1, y0, x1, y1))
        else:
            min_even = y0 + 1 if (y0 + 1) % 2 == 0 else y0 + 2
            max_even = y1 - 1 if (y1 - 1) % 2 == 0 else y1 - 2
            if min_even > max_even:
                continue
            choosed_y = random.randint(min_even // 2, max_even // 2) * 2
            for i in range(x0, x1 + 1):
                _check_cancel(cancel_event)
                matrix[choosed_y][i] = MapWall(i, choosed_y)
            min_odd = x0 if x0 % 2 != 0 else x0 + 1
            max_odd = x1 if x1 % 2 != 0 else x1 - 1
            open_idx = random.randint((min_odd - 1) // 2, (max_odd - 1) // 2) * 2 + 1
            matrix[choosed_y][open_idx] = MapDotFloor(open_idx, choosed_y)
            stack.append((x0, y0, x1, choosed_y - 1))
            stack.append((x0, choosed_y + 1, x1, y1))

    return matrix


def generate_kruskal(rows, cols, cancel_event=None):
    matrix = [[MapWall(x, y) for x in range(cols)] for y in range(rows)]

    d_set = DisjointSet()
    edges = []

    for i in range(1, rows - 1, 2):
        for j in range(1, cols - 1, 2):
            matrix[i][j] = MapDotFloor(j, i)
            if j + 2 < cols:
                edges.append(((j, i), (j + 2, i)))
            if i + 2 < rows:
                edges.append(((j, i), (j, i + 2)))

    random.shuffle(edges)

    for a, b in edges:
        _check_cancel(cancel_event)
        if not d_set.union(a, b):
            continue
        mid_x = (a[0] + b[0]) // 2
        mid_y = (a[1] + b[1]) // 2

        matrix[mid_y][mid_x] = MapDotFloor(mid_x, mid_y)

    return matrix


def generate_prim(rows, cols, cancel_event=None):
    matrix = [[MapWall(x, y) for x in range(cols)] for y in range(rows)]

    sx, sy = (
        random.randint(0, (cols // 2) - 1) * 2 + 1,
        random.randint(0, (rows // 2) - 1) * 2 + 1,
    )
    matrix[sy][sx] = MapDotFloor(sx, sy)

    total_nodes = (rows // 2) * (cols // 2)

    edges_list = []
    visited_nodes = set([(sx, sy)])

    for dx, dy in DIR_DOUBLE:
        nx = sx + dx
        ny = sy + dy
        if nx < 1 or nx >= cols - 1 or ny < 1 or ny >= rows:
            continue
        edges_list.append((nx, ny, sx, sy))

    while edges_list:
        _check_cancel(cancel_event)
        idx = random.randint(0, len(edges_list) - 1)
        x, y, px, py = edges_list[idx]

        edges_list[idx] = edges_list[-1]
        edges_list.pop()

        if (x, y) in visited_nodes:
            continue
        visited_nodes.add((x, y))

        mid_x = (x + px) // 2
        mid_y = (y + py) // 2

        matrix[y][x] = MapDotFloor(x, y)
        matrix[mid_y][mid_x] = MapDotFloor(mid_x, mid_y)

        if len(visited_nodes) == total_nodes:
            break

        for dx, dy in DIR_DOUBLE:
            nx, ny = x + dx, y + dy
            if nx < 1 or nx >= cols - 1 or ny < 1 or ny >= rows - 1:
                continue
            if (nx, ny) in visited_nodes:
                continue
            edges_list.append((nx, ny, x, y))

    return matrix


def generate_loops(matrix, braid_factor, cancel_event=None):
    if braid_factor == 0.0:
        return

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(1, rows - 1):
        _check_cancel(cancel_event)
        start = (i & 1) + 1
        for j in range(start, cols - 1, 2):
            if not isinstance(matrix[i][j], MapWall):
                continue
            if random.random() < braid_factor:
                matrix[i][j] = MapDotFloor(j, i)


def generate_valid_sequence(key_pairs):
    result = []
    available_keys = key_pairs.copy()
    unlocked_doors = []

    while available_keys or unlocked_doors:
        valid_choices = available_keys + unlocked_doors
        choice = random.choice(valid_choices)

        result.append(choice)

        if choice.islower():
            available_keys.remove(choice)
            unlocked_doors.append(choice.upper())
        else:
            unlocked_doors.remove(choice)

    return result


def get_cells_by_distance(matrix, sx, sy, cancel_event=None):
    queue = deque([(sx, sy)])
    visited = set([(sx, sy)])
    visited_ordered = [(sx, sy)]

    while queue:
        _check_cancel(cancel_event)
        x, y = queue.popleft()
        visited_ordered.append((x, y))

        for dx, dy in DIR:
            nx, ny = x + dx, y + dy
            cell = matrix[ny][nx]
            if isinstance(cell, MapWall):
                continue
            pos = (nx, ny)
            if pos in visited:
                continue
            visited.add(pos)
            queue.append(pos)

    return visited_ordered


def generate_key_port(matrix, visited_ordered, keys, cancel_event=None):
    sequence = generate_valid_sequence(keys)

    delta = len(visited_ordered) // (len(sequence) + 2)
    i = delta
    for e in sequence:
        _check_cancel(cancel_event)
        x, y = visited_ordered[i]
        if e == e.lower():
            matrix[y][x] = MapKey(x, y, e)
        else:
            matrix[y][x] = MapPort(x, y, e)
        i += delta


def get_worst_cell(
    map: Map, cancel_event=None
) -> tuple[SearchState, dict[SearchState, SearchState | None]]:
    def get_key(ch: str) -> int:
        # ASCII lowercase keys map to distinct bits, making state checks constant-time.
        return 1 << (ord(ch) - 97)

    start_state = (map.start, 0)

    prev_map = {start_state: None}
    visited_positions = set()

    queue = deque([(0, map.start[0], map.start[1], 0)])
    worst_state = ((map.start[0], map.start[1]), 0)
    worst_state_steps = 0
    # state -> (pos, keys, bonus_visited)

    while queue:
        _check_cancel(cancel_event)
        steps, x, y, keys = queue.popleft()
        state = ((x, y), keys)
        if (x, y) not in visited_positions:
            visited_positions.add((x, y))
            if steps > worst_state_steps:
                worst_state_steps = steps
                worst_state = state

        new_steps = steps + 1

        for dx, dy in DIR:
            nx, ny = x + dx, y + dy

            node = map.matrix[ny][nx]
            if isinstance(node, MapWall):
                continue
            if isinstance(node, MapPort) and not get_key(node.letter) & keys:
                continue

            new_keys = keys

            if isinstance(node, MapKey):
                new_keys = keys | get_key(node.letter)

            new_state = ((nx, ny), new_keys)

            if new_state in prev_map:
                continue

            prev_map[new_state] = state
            queue.append((new_steps, nx, ny, new_keys))

    return worst_state, prev_map


def generate_floor_direct(
    map_obj: Map, prev_map, last_state, floor_directed_density, cancel_event=None
):
    if floor_directed_density == 0.0:
        return

    dir_vec_map = {}
    cell_iter_counter = defaultdict(int)
    curr = last_state

    while True:
        _check_cancel(cancel_event)
        next_pos = curr[0]
        prev_curr = prev_map[curr]
        if not prev_curr:
            break
        pos = prev_curr[0]
        cell_iter_counter[pos] += 1
        if cell_iter_counter[pos] > 1:
            dir_vec_map.pop(pos, None)
        else:
            dir_vec_map[pos] = (
                next_pos[0] - pos[0],
                next_pos[1] - pos[1],
            )
        curr = prev_curr

    for i in range(1, map_obj.rows - 1):
        _check_cancel(cancel_event)
        for j in range(1, map_obj.cols - 1):
            cell = map_obj.matrix[i][j]
            if not isinstance(cell, MapDotFloor):
                continue
            match cell_iter_counter[(j, i)]:
                case 0:
                    neighbors = []
                    for dx, dy in DIR:
                        if not isinstance(map_obj.matrix[i + dy][j + dx], MapWall):
                            neighbors.append((dx, dy))
                    vec = random.choice(neighbors)
                case 1:
                    vec = dir_vec_map[(j, i)]
                case _:
                    continue

            if random.random() < floor_directed_density:
                map_obj.matrix[i][j] = MapFloorDirected(j, i, vec)


def generate_floor_variation(
    map_obj: Map, water_density, mud_density, bonus_density, source_density,
    cancel_event=None,
):
    mud_density += water_density
    bonus_density += mud_density
    source_density += bonus_density

    if source_density == 0.0:
        return

    for i in range(1, map_obj.rows - 1):
        _check_cancel(cancel_event)
        for j in range(1, map_obj.cols - 1):
            cell = map_obj.matrix[i][j]
            if not isinstance(cell, MapDotFloor):
                continue
            prob = random.random()
            if prob < water_density:
                map_obj.matrix[i][j] = MapWater(j, i)
            elif prob < mud_density:
                map_obj.matrix[i][j] = MapMud(j, i)
            elif prob < bonus_density:
                map_obj.matrix[i][j] = MapBonus(j, i)
            elif prob < source_density:
                map_obj.matrix[i][j] = MapSource(j, i)


def generate_map(
    rows: int,
    cols: int,
    *,
    strategy: Literal[
        "backtracking", "recursive_division", "kruskal", "prim"
    ] = "backtracking",
    keys: list[str] = ["a", "b", "c", "d"],
    braid_factor: float = 0.0,
    water_density: float = 0,
    mud_density: float = 0,
    bonus_density: float = 0,
    source_density: float = 0,
    floor_directed_density: float = 0,
    cancel_event: Event | None = None,
    progress_callback: Callable[[str, float, int, int], None] | None = None,
) -> Map:
    """Generates a customizable game maze with varied terrains and structures.

    Args:
        rows: Grid height (automatically forced to odd).
        cols: Grid width (automatically forced to odd).
        strategy: Maze generation method ("backtracking", "recursive_division", "kruskal", "prim").
        keys: List of characters for collectible keys to spawn.
        braid_factor: Ratio of internal walls to remove to create loops [0.0, 1.0].
        *_density: Spawn rates [0.0, 1.0] for special floor tiles (sum <= 1.0).

    Returns:
        Map: An initialized game map object containing the tile matrix.

    Raises:
        ValueError: If strategy is invalid or total density exceeds 1.0.
        MapGenerationCancelled: If cancellation is requested during generation.
    """

    _check_cancel(cancel_event)
    total_density = (
        water_density
        + mud_density
        + bonus_density
        + source_density
        + floor_directed_density
    )

    if total_density > 1.0:
        raise ValueError(
            f"Total density constraint violated: The sum of all tile densities "
            f"({total_density:.2f}) cannot exceed 1.0."
        )

    rows |= 1
    cols |= 1

    cells_count = rows * cols
    estimated_stages = [
        (f"generate_{strategy}", cells_count),
        ("generate_loops", cells_count * 0.35),
        ("get_cells_by_distance", cells_count),
        ("generate_key_port", max(len(keys), 1)),
        ("get_worst_cell", cells_count * (1 << min(len(keys), 6))),
        ("generate_floor_direct", cells_count * 0.7),
        ("generate_floor_variation", cells_count * 0.7),
        ("compute_stats", cells_count * 0.2),
    ]
    total_estimated_work = sum(weight for _, weight in estimated_stages)
    estimated_progress = {}
    completed_work = 0.0
    for stage_number, (stage, weight) in enumerate(estimated_stages, start=1):
        estimated_progress[stage] = (
            completed_work / total_estimated_work,
            stage_number,
            len(estimated_stages),
        )
        completed_work += weight

    def report_stage(stage: str):
        estimate, stage_number, stage_count = estimated_progress[stage]
        _report_progress(
            progress_callback, stage, estimate, stage_number, stage_count
        )

    report_stage(f"generate_{strategy}")
    match strategy:
        case "backtracking":
            matrix = generate_backtracking(rows, cols, cancel_event)
        case "recursive_division":
            matrix = generate_recursive_division(rows, cols, cancel_event)
        case "kruskal":
            matrix = generate_kruskal(rows, cols, cancel_event)
        case "prim":
            matrix = generate_prim(rows, cols, cancel_event)
        case _:
            raise ValueError("Invalid strategy")

    _check_cancel(cancel_event)
    report_stage("generate_loops")
    generate_loops(matrix, braid_factor, cancel_event)

    sx, sy = (
        random.randint(0, (cols // 2) - 1) * 2 + 1,
        random.randint(0, (rows // 2) - 1) * 2 + 1,
    )
    matrix[sy][sx] = MapStart(sx, sy)

    report_stage("get_cells_by_distance")
    cells_by_distance = get_cells_by_distance(matrix, sx, sy, cancel_event)

    report_stage("generate_key_port")
    generate_key_port(matrix, cells_by_distance, keys, cancel_event)

    map_obj = Map((sx, sy), None, matrix)
    report_stage("get_worst_cell")
    last_state, prev_map = get_worst_cell(map_obj, cancel_event)
    x, y = last_state[0]
    map_obj.end = (x, y)
    map_obj.matrix[y][x] = MapEnd(x, y)

    report_stage("generate_floor_direct")
    generate_floor_direct(
        map_obj, prev_map, last_state, floor_directed_density, cancel_event
    )

    report_stage("generate_floor_variation")
    generate_floor_variation(
        map_obj, water_density, mud_density, bonus_density, source_density,
        cancel_event,
    )

    _check_cancel(cancel_event)
    report_stage("compute_stats")
    map_obj.compute_stats()
    _check_cancel(cancel_event)

    _report_progress(
        progress_callback, "Concluído", 1.0, len(estimated_stages), len(estimated_stages)
    )
    return map_obj
