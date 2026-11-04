from typing import NamedTuple

class MapState(NamedTuple):
    pos: tuple[int, int]
    keys: frozenset = frozenset()
    bonus_visited: frozenset = frozenset()

    def __repr__(self):
        keys_str = "".join(sorted(self.keys))
        bonus_str = ",".join(map(str, self.bonus_visited))
        return f"{self.pos}|{keys_str}|{{{bonus_str}}}" 