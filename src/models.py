from typing import Any


class Hub:
    def __init__(self, type: str):
        """Create a hub with default capacity and zone values."""
        self.zone = "normal"
        self.cost = 1.0
        self.color = ""
        self.max_drones = 1
        self.max_drones_set = False
        self.current_drones = 0
        self.coords = (0, 0)
        self.type = type
        self.neighbors: list[str] = []
        self.label = ""

    def parse_hub(
        self,
        info: str,
        used_names: list[str],
        used_labels: list[str],
    ) -> None:
        """Parse hub coordinates and optional metadata."""
        if "[" in info:
            zone_data, metadata = info.strip().split("[", 1)
            self.check_zone(zone_data, used_names)
            self.check_metadata(metadata.strip("]"))
        else:
            self.check_zone(info, used_names)

        self.create_label(used_labels)

    def check_metadata(self, info: str) -> None:
        """Apply hub metadata values from the config line."""
        metadata = info.strip().split(" ")
        for meta in metadata:
            if "=" not in meta or " " in meta.strip():
                raise ValueError(
                    "Metadata block must be syntactically valid. "
                    "(eg. [zone=... color=...] )"
                )

            key, value = meta.strip().split("=", 1)

            if key == "zone":
                if value not in [
                    "normal",
                    "blocked",
                    "restricted",
                    "priority",
                ]:
                    raise ValueError("Invalid zone type")
                else:
                    self.zone = value
                    if value in ["restricted", "priority"]:
                        self.cost = 2 if value == "restricted" else 0.9

            elif key == "max_drones":
                if not value.isdigit() or int(value) < 0:
                    raise ValueError(
                        "Max_drones have to be a valid positive intergers"
                    )
                self.max_drones = int(value)
                self.max_drones_set = True
            elif key == "color":
                self.color = value
            else:
                raise ValueError("Unknown metadata type")

    def check_zone(self, info: str, used_names: list[str]) -> None:
        """Validate hub coordinates and register the hub name."""
        name, x, y = info.strip().split(" ", 3)
        name = name.strip()
        y = y.strip()
        x = x.strip()
        if name in used_names:
            raise ValueError("Each zone must have a unique name")
        elif " " in name or "-" in name:
            raise ValueError(
                "Zone names can use any valid characters but dashes and "
                "spaces."
            )
        else:
            used_names.append(name)
            self.name = name

        try:
            int(y)
            int(x)
        except ValueError:
            raise ValueError("The coordinates have to be valid intergers")

        self.coords = (int(y), int(x))

    def create_label(self, labels: list[str]) -> None:
        """Create a short unique label for the hub."""
        label = self.name[:2].upper()

        i = -1
        while label in labels:
            if self.name[i].isalnum():
                label = self.name[0].upper() + self.name[i].upper()
            i -= 1

        labels.append(label)
        self.label = label


class Connects:
    connections: dict[str, list[Any]] = {}

    def verify(self, info: str, used_names: list[str]) -> None:
        """Validate and store a connection definition."""
        if "[" not in info:
            conn = self.verify_connection(info, used_names)
            conn.append(1)
            conn.append(0)
            self.connections.update({conn[0] + "-" + conn[1]: conn})
        else:
            connects, metadata = info.strip().split("[")

            conn = self.verify_connection(connects, used_names)

            conn.append(self.verify_meta(metadata.strip("]")))
            conn.append(0)
            self.connections.update({conn[0] + "-" + conn[1]: conn})

    def verify_connection(
        self,
        info: str,
        used_names: list[str],
    ) -> list[Any]:
        """Check that a connection links two known and distinct hubs."""
        connects = info.strip().split("-")
        if (
            len(connects) != 2
            or connects[0] == connects[1]
            or any(" " in item for item in connects)
        ):
            raise ValueError(
                "A connection must have diferent 2 zones connected"
            )

        c1, c2 = connects

        if c1 not in used_names or c2 not in used_names:
            raise ValueError(
                "Connections must link only previously defined zones"
            )

        if (
            f"{c1}-{c2}" in self.connections
            or f"{c2}-{c1}" in self.connections
        ):
            raise ValueError(
                "The same connection must not appear more than once"
                " (e.g., a-b and b-a are considered duplicates)"
            )

        return [c1, c2]

    def verify_meta(self, info: str) -> str:
        """Validate connection metadata and return the capacity value."""
        metadata = info.strip()

        if "=" not in metadata:
            raise ValueError(
                "Metadata block must be syntactically valid. "
                "(eg. [max_link_capacity=...])"
            )

        key, value = metadata.strip().split("=", 1)

        if key != "max_link_capacity":
            raise ValueError("Unknown connection metadata")

        if not value.isdigit() or int(value) < 0:
            raise ValueError(
                "Capacity values must be valid positive integers."
            )

        return value
