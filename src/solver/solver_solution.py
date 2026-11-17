from src.map.map_state import MapState

class SolverSolution:
    def __init__(self, iterations: list[MapState] = [], path: list[MapState] = [], parent: dict | None = None, msg: str | None = None):
        self.iterations = iterations
        self.path = path
        # [IA] Claude Code (Claude Sonnet 5.5) – árvore de busca (estado -> estado anterior), opcional; usada para desenhar a árvore BFS
        self.parent = parent
        self.msg = msg
