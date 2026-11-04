from src.map.map_state import MapState

class SolverSolution:
    def __init__(self, iterations: list[MapState] = [], path: list[MapState] = []):
        self.iterations = iterations
        self.path = path