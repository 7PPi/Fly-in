from typing import Any


class Graph:
    def __init__(self, data: dict[str, Any]) -> None:
        """Store the map data and build hub neighbors."""
        self.data = data
        self.find_neighbors()

    def find_neighbors(self) -> None:
        """Populate each hub with its adjacent hubs."""
        hubs = self.data["hubs"]
        connections = self.data["connections"]

        for hub in hubs.values():
            name = hub.name

            for adjacent in connections.values():
                if name not in adjacent:
                    continue
                if name == adjacent[0]:
                    hub.neighbors.append(adjacent[1])
                elif name == adjacent[1]:
                    hub.neighbors.append(adjacent[0])

    def find_paths(self) -> list[tuple[float, list[str]]]:
        """Find all valid paths from the start hub to the end hub."""
        try:
            all_paths: list[tuple[float, list[str]]] = []
            hubs = self.data["hubs"]
            used_keys: list[tuple[str, str]] = []
            start = next(
                (hub.name for hub in hubs.values() if hub.type == "start_hub"),
                None,
            )
            if start is None:
                raise ValueError("Missing start hub")
            priority_queue: list[tuple[list[str], float, set[str]]] = [
                ([start], 0.0, {start})
            ]

            while priority_queue:
                current_path, current_cost, visited = priority_queue.pop(0)
                current_hub = current_path[-1]

                if hubs[current_hub].type == "end_hub":
                    all_paths.append((current_cost, current_path))
                    continue

                for neighbor in hubs[current_hub].neighbors:
                    if (neighbor, current_hub) in used_keys:
                        continue
                    if neighbor in visited:
                        continue
                    if hubs[neighbor].type == "blocked":
                        continue

                    new_cost = float(current_cost) + float(hubs[neighbor].cost)
                    new_visited = visited.copy()
                    new_visited.add(neighbor)
                    new_path = current_path + [neighbor]

                    priority_queue.append((new_path, new_cost, new_visited))
                    priority_queue = sorted(priority_queue, key=lambda x: x[1])
                    used_keys.append((current_hub, neighbor))

            if not all_paths:
                raise ValueError("There is no path to the end hub")

            all_paths = sorted(all_paths, key=lambda x: (x[0], len(x)))
            return all_paths
        except Exception as e:
            print("ERROR G:", e)
            raise SystemExit(0)
