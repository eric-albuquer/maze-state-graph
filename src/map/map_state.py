from typing import NamedTuple

class MapState(NamedTuple):
    pos: tuple[int, int]
    keys: frozenset
    bonus_visited: frozenset

    def __repr__(self):
        return f"{self.pos}|{"".join(sorted(list(self.keys)))}|{{{",".join(map(str, self.bonus_visited))}}}"