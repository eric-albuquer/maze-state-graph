class MapTile:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class MapWall(MapTile):
    def __init__(self, x, y):
        super().__init__(x, y)

    def __repr__(self): return "#"

class MapFloor(MapTile):
    def __init__(self, x, y, cost: int):
        super().__init__(x, y)
        self.cost = cost

class MapDotFloor(MapFloor):
    def __init__(self, x, y):
        super().__init__(x, y, 1)

    def __repr__(self): return "."

class MapKey(MapFloor):
    def __init__(self, x, y, letter: str):
        super().__init__(x, y, 1)
        self.letter = letter.lower()

    def __repr__(self): return self.letter

class MapPort(MapFloor):
    def __init__(self, x, y, letter: str):
        super().__init__(x, y, 1)
        self.letter = letter.lower()

    def __repr__(self): return self.letter.upper()

class MapStart(MapFloor):
    def __init__(self, x, y):
        super().__init__(x, y, 1)

    def __repr__(self): return "S"

class MapEnd(MapFloor):
    def __init__(self, x, y):
        super().__init__(x, y, 1)

    def __repr__(self): return "G"

class MapMud(MapFloor):
    def __init__(self, x, y):
        super().__init__(x, y, 3)

    def __repr__(self): return ","

class MapWater(MapFloor):
    def __init__(self, x, y):
        super().__init__(x, y, 5)

    def __repr__(self): return "~"

class MapFloorDirected(MapFloor):
    def __init__(self, x, y, dir_vec: tuple[int, int]):
        super().__init__(x, y, 1)
        self.dir_vec = dir_vec

    def __repr__(self):
        match self.dir_vec:
            case (-1, 0): return "<"
            case (1, 0): return ">"
            case (0, -1): return "^"
            case (0, 1): return "v"

class MapBonus(MapFloor):
    def __init__(self, x, y):
        super().__init__(x, y, -4)
        # if visited: cost = 1

    def __repr__(self): return "+"

class MapSource(MapFloor):
    def __init__(self, x, y):
        super().__init__(x, y, -2)

    def __repr__(self): return "*"