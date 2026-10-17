from map.map import *
import random
from collections import deque, defaultdict
from solver.solver import solve
from typing import Literal

DIR_DOUBLE = [(0, -2), (2, 0), (0, 2), (-2, 0)]
DIR = [(0, -1), (1, 0), (0, 1), (-1, 0)]
ADJ_DIR = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]

class DisjointSet:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, val):
        if val not in self.parent:
            self.parent[val] = val
            self.rank[val] = 0

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


def generate_backtracking(rows, cols):
    matrix = [[MapWall(x, y) for x in range(cols)] for y in range(rows)]

    stack = [(1, 1)]
    matrix[1][1] = MapDotFloor(1, 1)

    while stack:
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

def generate_recursive_division(rows, cols):
    matrix = [[MapDotFloor(x, y) for x in range(cols)] for y in range(rows)]

    for i in range(rows):
        matrix[i][0] = MapWall(0, i)
        matrix[i][cols - 1] = MapWall(cols - 1, i)

    for i in range(cols):
        matrix[0][i] = MapWall(i, 0)
        matrix[rows - 1][i] = MapWall(i, rows - 1)

    stack = [(1, 1, cols - 2, rows - 2)]

    while stack:
        x0, y0, x1, y1 = stack.pop()
        width = x1 - x0
        height = y1 - y0

        if width <= 1 or height <= 1:
            continue

        choose_vertical = width > height if width != height else random.choice([True, False])

        if choose_vertical:
            x_list = [x for x in range(x0 + 1, x1) if x % 2 == 0]
            if not x_list: continue
            choosed_x = random.choice(x_list)
            for i in range(y0, y1 + 1):
                matrix[i][choosed_x] = MapWall(choosed_x, i)
            y_list = [y for y in range(y0, y1 + 1) if y % 2 != 0]
            open_idx = random.choice(y_list)
            matrix[open_idx][choosed_x] = MapDotFloor(choosed_x, open_idx)
            stack.append((x0, y0, choosed_x - 1, y1))
            stack.append((choosed_x + 1, y0, x1, y1))
        else:
            y_list = [y for y in range(y0, y1 + 1) if y % 2 == 0]
            if not y_list: continue
            choosed_y = random.choice(y_list)
            for i in range(x0, x1 + 1):
                matrix[choosed_y][i] = MapWall(i, choosed_y)
            x_list = [x for x in range(x0, x1 + 1) if x % 2 != 0]
            open_idx = random.choice(x_list)
            matrix[choosed_y][open_idx] = MapDotFloor(open_idx, choosed_y)
            stack.append((x0, y0, x1, choosed_y - 1))
            stack.append((x0, choosed_y + 1, x1, y1))

    return matrix

def generate_kruskal(rows, cols):
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
        if not d_set.union(a, b):
            continue
        mid_x = (a[0] + b[0]) // 2
        mid_y = (a[1] + b[1]) // 2

        matrix[mid_y][mid_x] = MapDotFloor(mid_x, mid_y)

    return matrix


def generate_prim(rows, cols):
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

def generate_loops(matrix, loop_density):
    if loop_density == 0.0:
        return

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(1, rows - 1):
        start = (i & 1) + 1
        for j in range(start, cols - 1, 2):
            if not isinstance(matrix[i][j], MapWall):
                continue
            if random.random() < loop_density:
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


def get_cells_by_distance(matrix, sx, sy):
    queue = deque([(sx, sy)])
    visited = set([(sx, sy)])
    visited_ordered = [(sx, sy)]

    while queue:
        x, y = queue.popleft()

        for dx, dy in DIR:
            nx, ny = x + dx, y + dy
            cell = matrix[ny][nx]
            if isinstance(cell, MapWall):
                continue
            pos = (nx, ny)
            if pos in visited:
                continue
            visited.add(pos)
            visited_ordered.append(pos)
            queue.append(pos)

    return visited_ordered


def generate_key_port(matrix, visited_ordered):
    sequence = generate_valid_sequence(["a", "b", "c", "d"])

    delta = len(visited_ordered) // (len(sequence) + 2)
    i = delta
    for e in sequence:
        x, y = visited_ordered[i]
        if e == e.lower():
            matrix[y][x] = MapKey(x, y, e)
        else:
            matrix[y][x] = MapPort(x, y, e)
        i += delta


def generate_floor_direct(map_obj: Map, floor_directed_density):
    if floor_directed_density == 0.0:
        return

    solution = solve(map_obj)
    if not solution:
        raise ValueError("Unsolvable maze generated")

    dir_vec_map = {}
    cell_iter_counter = defaultdict(int)

    for i in range(len(solution) - 1):
        curr_pos = solution[i][0][0]
        next_pos = solution[i + 1][0][0]
        cell_iter_counter[curr_pos] += 1
        if cell_iter_counter[curr_pos] > 1:
            dir_vec_map.pop(curr_pos)
        else:
            dir_vec_map[curr_pos] = (
                next_pos[0] - curr_pos[0],
                next_pos[1] - curr_pos[1],
            )

    for i in range(1, map_obj.rows - 1):
        for j in range(1, map_obj.cols - 1):
            cell = map_obj.matrix[i][j]
            if not isinstance(cell, MapDotFloor):
                continue
            match cell_iter_counter[(j, i)]:
                case 0:
                    vec = random.choice(DIR)
                case 1:
                    vec = dir_vec_map[(j, i)]
                case _:
                    continue

            if random.random() < floor_directed_density:
                map_obj.matrix[i][j] = MapFloorDirected(j, i, vec)


def generate_floor_variation(
    map_obj: Map, water_density, mud_density, bonus_density, source_density
):
    mud_density += water_density
    bonus_density += mud_density
    source_density += bonus_density

    for i in range(1, map_obj.rows - 1):
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
    rows:int,
    cols:int,
    *,
    algorithm:Literal["backtracking", "recursive_division", "kruskal", "prim"]="backtracking",
    loop_density:float=0.0,
    water_density:float=0,
    mud_density:float=0,
    bonus_density:float=0,
    source_density:float=0,
    floor_directed_density:float=0,
):
    rows |= 1
    cols |= 1

    match algorithm:
        case "backtracking":
            matrix = generate_backtracking(rows, cols)
        case "recursive_division":
            matrix = generate_recursive_division(rows, cols)
        case "kruskal":
            matrix = generate_kruskal(rows, cols)
        case "prim":
            matrix = generate_prim(rows, cols)
        case _:
            raise ValueError("Invalid algorithm")

    generate_loops(matrix, loop_density)

    sx, sy = (
        random.randint(0, (cols // 2) - 1) * 2 + 1,
        random.randint(0, (rows // 2) - 1) * 2 + 1,
    )
    matrix[sy][sx] = MapStart(sx, sy)

    cells_by_distance = get_cells_by_distance(matrix, sx, sy)

    generate_key_port(matrix, cells_by_distance)

    ex, ey = cells_by_distance[-1]
    matrix[ey][ex] = MapEnd(ex, ey)

    map_obj = Map((sx, sy), (ex, ey), matrix)

    generate_floor_direct(map_obj, floor_directed_density)

    generate_floor_variation(
        map_obj, water_density, mud_density, bonus_density, source_density
    )

    return map_obj
