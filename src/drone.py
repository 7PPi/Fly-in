class Drone:
    def __init__(self, id: int, path: list[str]) -> None:
        """Create a drone assigned to a specific path."""
        self.id = id
        self.path = path
        self.path_index = 0
        self.current_hub = path[0]
        self.in_transit = False
        self.turns_left = 0
        self.finished = False
        self.reserved_connection: str | None = None
