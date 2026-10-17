from map.map_nodes import *

class Map:
    def __init__(self, start: tuple[int, int], end: tuple[int, int], matrix: list[list[MapTile]]):
        self.rows = len(matrix)
        self.cols = len(matrix[0])

        self.start = start
        self.end = end

        self.matrix = matrix

    def __repr__(self):
        buffer = []
        buffer.append(f"start: {self.start}")
        buffer.append(f"end: {self.end}")
        for y, row in enumerate(self.matrix):
            row_buffer = [f"{y:02d}: "]
            for col in row:
                row_buffer.append(repr(col))
            buffer.append("".join(row_buffer))
        return "\n".join(buffer)