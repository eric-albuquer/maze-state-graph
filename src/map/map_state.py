from typing import NamedTuple

class MapState(NamedTuple):
    pos: tuple[int, int]
    keys: frozenset = frozenset()
    bonus_visited: frozenset = frozenset()

    def __repr__(self):
        return f"{self.pos}|{"".join(sorted(list(self.keys)))}|{{{",".join(map(str, self.bonus_visited))}}}"