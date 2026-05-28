from typing import Any

from colorama import Fore, Style, init
from .visualization import Represent
from .drone import Drone
from os import system
from time import sleep


init()


class Engine:
    def simulate_turns(
        self,
        data: dict[str, Any],
        all_paths: list[tuple[float, list[str]]],
    ) -> None:
        """Run the turn-by-turn drone simulation."""
        drones: list[Drone] = []
        finished = 0
        turns = 0
        view = Represent()

        assignments = self.assign_paths(all_paths, data)

        for route in assignments:
            drones.append(Drone(route[0], route[1]))

        # initialize hub occupancies for starting drones
        for drone in drones:
            data["hubs"][drone.current_hub].current_drones += 1

        while finished < len(drones):
            progress_made = False

            # PHASE 0: process arrivals from previously started transits
            moviments: list[dict[str, Any]] = []
            reserved_hubs: dict[str, int] = {}
            reserved_conns: dict[str, int] = {}

            for drone in drones:
                if drone.in_transit:
                    drone.turns_left -= 1
                    if drone.turns_left == 0:
                        conn_key = drone.reserved_connection
                        if conn_key:
                            conn = data["connections"][conn_key]
                            conn[-1] = int(conn[-1]) - 1
                            drone.reserved_connection = None

                        drone.in_transit = False
                        drone.path_index += 1
                        drone.current_hub = drone.path[drone.path_index]
                        data["hubs"][drone.current_hub].current_drones += 1
                        progress_made = True

                        if drone.current_hub == drone.path[-1]:
                            drone.finished = True
                            finished += 1

            # PHASE 1: decide who can move and reserve spots
            for drone in drones:
                if drone.finished or drone.in_transit:
                    continue

                if drone.current_hub == drone.path[-1]:
                    drone.finished = True
                    finished += 1
                    continue

                next_hub_name = drone.path[drone.path_index + 1]
                next_hub = data["hubs"][next_hub_name]

                reserved_for_hub = reserved_hubs.get(next_hub_name, 0)
                if (
                    next_hub.current_drones + reserved_for_hub
                    >= next_hub.max_drones
                ):
                    continue

                connection_key = drone.current_hub + "-" + next_hub_name
                if connection_key not in data["connections"]:
                    connection_key = next_hub_name + "-" + drone.current_hub
                connection = data["connections"][connection_key]

                max_link = int(connection[-2])
                curr_link = int(connection[-1])
                reserved_link = reserved_conns.get(connection_key, 0)

                will_transit = next_hub.zone == "restricted"
                if (curr_link + reserved_link) >= max_link:
                    continue

                reserved_hubs[next_hub_name] = reserved_for_hub + 1
                reserved_conns[connection_key] = reserved_link + 1

                data["hubs"][drone.current_hub].current_drones -= 1

                moviments.append({
                    "drone": drone,
                    "from": drone.current_hub,
                    "to": next_hub_name,
                    "connection_key": connection_key,
                    "transit": will_transit,
                })

            # PHASE 2: execute reserved movements
            line = ""
            for mv in moviments:
                drone = mv["drone"]
                to = mv["to"]
                conn_key = mv["connection_key"]
                progress_made = True

                if mv["transit"]:
                    data["connections"][conn_key][-1] = int(
                        data["connections"][conn_key][-1]
                    ) + 1
                    drone.reserved_connection = conn_key
                    drone.in_transit = True
                    drone.turns_left = 1
                    line += f"D{drone.id}-{drone.current_hub}-{to}  "
                else:
                    drone.path_index += 1
                    drone.current_hub = to
                    data["hubs"][to].current_drones += 1
                    line += f"D{drone.id}-{drone.current_hub}  "

                if (
                    drone.current_hub == drone.path[-1]
                    and not drone.in_transit
                ):
                    drone.finished = True
                    finished += 1

            # Avoid infinite loop when all remaining drones are blocked.
            if not progress_made and finished < len(drones):
                blocked = [
                    (d.id, d.path[d.path_index]) for d in drones
                    if not d.finished and not d.in_transit
                ]
                raise RuntimeError(
                    "Deadlock detected: no drone can move this turn. "
                    f"Blocked drones: {blocked}"
                )

            view.view_graph(data, drones)
            print("\n\n", line)
            turns += 1
            if finished < len(drones):
                print("Turn number", turns)
                sleep(1.2)
                system("clear")

        print(
            Style.BRIGHT
            + Fore.GREEN
            + f"All drones reached the end hub in {turns} turns."
            + Style.RESET_ALL
        )

    def path_bottleneck(
        self,
        path: list[str],
        data: dict[str, Any],
    ) -> int:
        """Return the smallest capacity along a path."""
        links = data["connections"]
        hubs = data["hubs"]

        min_hub = min(path, key=lambda x: hubs[x].max_drones)
        min_capacity = int(hubs[min_hub].max_drones)

        for i in range(len(path) - 1):
            key = path[i] + "-" + path[i + 1]
            if key not in links:
                key = path[i + 1] + "-" + path[i]
            capacity = int(links[key][-2])
            min_capacity = (
                capacity if capacity < min_capacity else min_capacity
            )

        return min_capacity

    def assign_paths(
        self,
        all_paths: list[tuple[float, list[str]]],
        data: dict[str, Any],
    ) -> list[tuple[int, list[str]]]:
        """Assign each drone to a path based on path bottlenecks."""
        assignments: list[tuple[int, list[str]]] = []
        nb_drones = data["nb_drones"]

        drone_id = 0
        path_index = 0

        while drone_id < nb_drones:
            current_path = all_paths[path_index % len(all_paths)][1]
            bottleneck = self.path_bottleneck(current_path, data)

            for _ in range(bottleneck):
                if drone_id >= nb_drones:
                    break
                assignments.append((drone_id, current_path))
                drone_id += 1

            path_index += 1
        return assignments
