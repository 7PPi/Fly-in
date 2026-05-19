from typing import Any

from colorama import init, Fore, Style

init()


class Represent:
    def __init__(self) -> None:
        """Set up the color mapping used by the ASCII renderer."""
        self.color_map: dict[str, str] = {
                            "red": Fore.RED,
                            "green": Fore.GREEN,
                            "blue": Fore.BLUE,
                            "yellow": Fore.YELLOW,
                            "orange": Fore.YELLOW,
                            "gray": Fore.WHITE,
                            "cyan": Fore.CYAN,
                        }

    def view_graph(
        self,
        data: dict[str, Any],
        drones: list[Any],
    ) -> None:
        """Render the current map and drone positions in the terminal."""
        connections = [conn for conn in data["connections"].keys()]

        hubs: list[dict[str, Any]] = [
            {
                "name": hub.name,
                "label": hub.label,
                "color": hub.color,
                "y": int(hub.coords[0]) * 4,
                "x": int(hub.coords[1]) * 4,
                "drones": int(hub.current_drones),
            }
            for hub in data["hubs"].values()
        ]

        min_y = min(hub["y"] for hub in hubs)
        min_x = min(hub["x"] for hub in hubs)

        if min_x < 0:
            shift_x = -min_x
            for hub in hubs:
                hub["x"] += shift_x

        if min_y < 0:
            shift_y = -min_y
            for hub in hubs:
                hub["y"] += shift_y

        max_y = max(hub["y"] for hub in hubs)
        max_x = max(hub["x"] for hub in hubs)

        labels: dict[tuple[int, int], str] = {
            (hub["y"], hub["x"]): f"[{hub['label']}:{hub['drones']}]"
            for hub in hubs
        }

        colors: dict[tuple[int, int], str] = {
            (hub["y"], hub["x"]): self.color_map[hub["color"]]
            for hub in hubs if hub["color"] and hub["color"] in self.color_map
        }

        # Keep all cells same width so inline labels do not break graph shape.
        cell_width = max(len(label) for label in labels.values())
        empty_cell = " " * cell_width

        grid = [
            [empty_cell for _ in range(max_x + 1)]
            for _ in range(max_y + 1)
        ]

        for (y, x), label in labels.items():
            grid[y][x] = label.ljust(cell_width, " ")

        # Add links between hubs
        for conn_key in connections:
            hub1_name, hub2_name = conn_key.split("-")

            hub1 = next(h for h in hubs if h["name"] == hub1_name)
            hub2 = next(h for h in hubs if h["name"] == hub2_name)

            y1, x1 = hub1["y"], hub1["x"]
            y2, x2 = hub2["y"], hub2["x"]

            dy = y2 - y1
            dx = x2 - x1
            steps = max(abs(dy), abs(dx))

            if steps == 0:
                continue
            for i in range(1, steps):
                y = round(y1 + dy * i / steps)
                x = round(x1 + dx * i / steps)

                if grid[y][x].strip() == "":
                    if abs(dy) > abs(dx) * 2:
                        char = "**"
                        grid[y][x] = char.center(cell_width)
                    else:
                        char = "*"
                        grid[y][x] = char.ljust(cell_width, "*")

        # Show drones in transit
        for drone in drones:
            if drone.in_transit:
                conn_key = (
                    drone.reserved_connection.split("-")
                    if drone.reserved_connection in connections
                    else None
                )

                if conn_key:
                    hub1 = next(h for h in hubs if h["name"] == conn_key[0])
                    hub2 = next(h for h in hubs if h["name"] == conn_key[1])

                    y1, x1 = hub1["y"], hub1["x"]
                    y2, x2 = hub2["y"], hub2["x"]

                    dy = y2 - y1
                    dx = x2 - x1
                    steps = max(abs(dy), abs(dx))
                    center_y = round(dy / 2)
                    center_x = round(dx / 2)

                    if steps == 0:
                        continue

                    y = y1 + center_y
                    x = x1 + center_x

                    if "*" in grid[y][x]:
                        if abs(dy) > abs(dx) * 2:
                            char = "D" + str(drone.id)
                            grid[y][x] = char.center(cell_width)
                        else:
                            char = "D" + str(drone.id)
                            grid[y][x] = char.center(cell_width, "*")

        # Print the graph
        for r, row in enumerate(grid):
            for c, cell in enumerate(row):
                if (r, c) in colors:
                    print(colors[(r, c)] + cell, end="")
                else:
                    print(Style.RESET_ALL + cell, end="")
            # reset style at end of line
            print(Style.RESET_ALL)
