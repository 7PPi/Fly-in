from src import Graph, Parser, Engine
import sys


def main() -> None:
    """Parse the map file and run the simulation."""
    try:
        if len(sys.argv) != 2:
            raise ValueError(
                "Map file missing (eg. python3 fly-in.py file_name)"
            )
        parser = Parser()
        data = parser.parse(sys.argv[1])
        graph = Graph(data)
        paths = graph.find_paths()
        simulator = Engine()

        simulator.simulate_turns(data, paths)
    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    main()
