from src.map.map_nodes import *

class MapStats:
    def __init__(self,
            keys: list[str] = [],
            dot_count: int = 0,
            water_count: int = 0,
            mud_count: int = 0,
            floor_directed_count: int = 0,
            source_count: int = 0,
            bonus_count: int = 0,

            wall_count: int = 0,
            floor_count: int = 0
        ):
        self.keys = keys
        self.dot_count = dot_count
        self.water_count = water_count
        self.mud_count = mud_count
        self.floor_directed_count = floor_directed_count
        self.source_count = source_count
        self.bonus_count = bonus_count

        self.floor_count = floor_count
        self.wall_count = wall_count

    def __repr__(self):
        return f""""
-----STATS------
keys: {self.keys}
dot count: {self.dot_count}
water count: {self.water_count}
mud count: {self.mud_count}
floor directed count: {self.floor_directed_count}
source count: {self.source_count}
bonus count: {self.bonus_count}

floor count: {self.floor_count}
wall count: {self.wall_count}
"""

class Map:
    def __init__(self,
            start: tuple[int, int], 
            end: tuple[int, int], 
            matrix: list[list[MapTile]],

            stats: MapStats = MapStats()
        ):
        self.rows = len(matrix)
        self.cols = len(matrix[0])

        self.start = start
        self.end = end

        self.stats = stats

        self.matrix = matrix

    def compute_stats(self):
        dot_count: int = 0
        water_count: int = 0
        mud_count: int = 0
        floor_directed_count: int = 0
        source_count: int = 0
        bonus_count: int = 0

        wall_count: int = 0

        keys = []

        for row in self.matrix:
            for cell in row:
                if isinstance(cell, MapWall):
                    wall_count += 1
                elif isinstance(cell, MapDotFloor):
                    dot_count += 1
                elif isinstance(cell, MapMud):
                    mud_count += 1
                elif isinstance(cell, MapWater):
                    water_count += 1
                elif isinstance(cell, MapBonus):
                    bonus_count += 1
                elif isinstance(cell, MapFloorDirected):
                    floor_directed_count += 1
                elif isinstance(cell, MapSource):
                    source_count += 1
                elif isinstance(cell, MapKey):
                    keys.append(cell.letter)

        floor_count = (self.rows * self.cols) - wall_count
        self.stats = MapStats(keys, dot_count, water_count, mud_count, floor_directed_count, source_count, bonus_count, wall_count, floor_count)
        return self.stats

    def __repr__(self):
        buffer = []
        buffer.append(repr(self.stats))
        buffer.append(f"start: {self.start}")
        buffer.append(f"end: {self.end}")
        for y, row in enumerate(self.matrix):
            row_buffer = [f"{y:02d}: "]
            for col in row:
                row_buffer.append(repr(col))
            buffer.append("".join(row_buffer))
        return "\n".join(buffer)