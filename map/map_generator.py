from map.map import *
import random
from collections import deque, defaultdict
from solver.solver import solve

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

def generate_backtraking(rows, cols):
    dir = [
        (0, -2),
        (2, 0),
        (0, 2),
        (-2, 0)
    ]
    
    matrix = [[MapWall(x, y) for x in range(cols)] for y in range(rows)]

    stack = [(1, 1)]
    matrix[1][1] = MapDotFloor(1, 1)

    while stack:
        x, y = stack[-1]

        neighbors = []
        for dx, dy in dir:
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

def generate_loops(matrix, loop_density):
    if loop_density == 0.0:
        return

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
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
    dir = [
        (0, -1),
        (1, 0),
        (0, 1),
        (-1, 0)
    ]

    queue = deque([(sx, sy)])
    visited = set([(sx, sy)])
    visited_ordered = [(sx, sy)]

    while queue:
        x, y = queue.popleft()

        for dx, dy in dir:
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

    dir = [
        (0, -1),
        (1, 0),
        (0, 1),
        (-1, 0)
    ]

    solution = solve(map_obj)
    if not solution:
        raise Exception("Invalid maze")
    
    dir_vec_map = {}
    cell_iter_counter = defaultdict(int)

    for i in range(len(solution) - 1):
        curr_pos = solution[i][0][0]
        next_pos = solution[i + 1][0][0]
        cell_iter_counter[curr_pos] += 1
        if cell_iter_counter[curr_pos] > 1:
            dir_vec_map.pop(curr_pos)
        else:
            dir_vec_map[curr_pos] = (next_pos[0] - curr_pos[0], next_pos[1] - curr_pos[1])

    for i in range(1, map_obj.rows - 1):
        for j in range(1, map_obj.cols - 1):
            cell = map_obj.matrix[i][j]
            if not isinstance(cell, MapDotFloor):
                continue
            pos = (j, i)
            vec = None
            if cell_iter_counter[pos] == 0:
                vec = random.choice(dir)
            elif cell_iter_counter[pos] == 1:
                vec = dir_vec_map[pos]
            else:
                continue

            if random.random() < floor_directed_density:
                map_obj.matrix[i][j] = MapFloorDirected(j, i, vec)

def generate_floor_variation(map_obj: Map, water_density, mud_density, bonus_density, source_density):
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

def generate_map(rows, cols, backtracking = True, loop_density = 0.0, water_density = 0, mud_density = 0, bonus_density = 0, source_density = 0, floor_directed_density = 0):
    rows |= 1
    cols |= 1

    if backtracking: matrix = generate_backtraking(rows, cols)
    else: matrix = generate_kruskal(rows, cols)

    generate_loops(matrix, loop_density)

    sx, sy = random.randint(0, (cols // 2) - 1) * 2 + 1, random.randint(0, (rows // 2) - 1) * 2 + 1
    matrix[sy][sx] = MapStart(sx, sy)

    cells_by_distance = get_cells_by_distance(matrix, sx, sy)

    generate_key_port(matrix, cells_by_distance)

    ex, ey = cells_by_distance[-1]
    matrix[ey][ex] = MapEnd(ex, ey)

    map_obj = Map((sx, sy), (ex, ey), matrix)

    generate_floor_direct(map_obj, floor_directed_density)

    generate_floor_variation(map_obj, water_density, mud_density, bonus_density, source_density)

    return map_obj