from typing import Any

from .models import Connects, Hub


class Parser:
    def check_mandatory(self, data: dict[str, Any]) -> None:
        """Ensure the parsed file contains the required sections."""
        if not any(hub.type == "start_hub" for hub in data["hubs"].values()):
            raise AttributeError("Missing start_hub input")
        if not any(hub.type == "end_hub" for hub in data["hubs"].values()):
            raise AttributeError("Missing end_hub input")
        if data.get("connections") is None:
            raise AttributeError("Missing connections input")
        if data.get("nb_drones") is None:
            raise AttributeError("Missing the number of drones")

    def parse(self, path: str) -> dict[str, Any]:
        """Parse a map file into hubs, connections, and drone count."""
        try:
            data: dict[str, Any] = {}
            hubs: dict[str, Hub] = {}
            used_names: list[str] = []
            used_labels: list[str] = []
            con = Connects()
            line_n = 0

            with open(path, "r") as file:
                for line_n, line in enumerate(file, start=1):
                    if line_n == 1:
                        if "nb_drones:" not in line:
                            raise ValueError(
                                "The first line must define the number of "
                                "drones using nb_drones:"
                            )
                        k, v = line.strip().split(":", 1)
                        v = v.strip()
                        if not v.isdigit() or int(v) < 0:
                            raise ValueError(
                                "The number of drones have has to be a "
                                "positive integer"
                            )
                        data.update({k: int(v)})
                        continue

                    if not line.strip() or line.startswith("#"):
                        continue

                    if ":" not in line:
                        raise ValueError("Invalid input type")

                    type, info = line.split(":", 1)

                    if type in ("hub", "start_hub", "end_hub"):
                        if (
                            type in ("start_hub", "end_hub")
                            and type in data
                        ):
                            raise ValueError(
                                f"There can’t be more than one {type}"
                            )

                        temp = Hub(type)
                        temp.parse_hub(info, used_names, used_labels)

                        if type == "start_hub":
                            temp.max_drones = data["nb_drones"]
                        elif type == "end_hub":
                            temp.max_drones = data["nb_drones"]

                        hubs.update({temp.name: temp})
                    elif type == "connection":
                        con.verify(info, used_names)
                    else:
                        raise ValueError("Unknown input type(allowed types:"
                                         "hub,connection, end_hub, start_hub)")

            data.update({"hubs": hubs, "connections": con.connections})

            self.check_mandatory(data)

            return data

        except ValueError as e:
            print("ERROR:", e, f"at line {line_n}")
            raise SystemExit(0)
        except AttributeError as e:
            print("ERROR:", e)
            raise SystemExit(0)
        except PermissionError:
            print("Unable to access file")
            raise SystemExit(0)
        except FileNotFoundError:
            print("Unable to find file")
            raise SystemExit(0)
        except Exception as e:
            print("ERROR P:", e, f"at line {line_n}")
            raise SystemExit(0)


__all__ = ["Parser", "Hub", "Connects"]
