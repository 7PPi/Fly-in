*This project has been created as part of the 42 curriculum by etchipoq.*

# 🚁 Fly-In — Drone Traffic Simulation

Route a fleet of drones through a network of zones, respecting capacity constraints and movement rules — in as few turns as possible.

---

## 📖 Description

**Fly-In** is a turn-based drone routing simulation built in Python as part of the 42 curriculum.

Given a map of interconnected hubs, the program must transport all drones from a **start hub** to an **end hub** as efficiently as possible, while respecting:

- 🏗️ **Hub capacities** — zones have a maximum number of drones allowed simultaneously
- 🔗 **Connection capacities** — links between hubs limit simultaneous drone traversal
- 🚧 **Zone restrictions** — blocked zones are impassable, restricted zones cost 2 turns
- ⭐ **Priority zones** — preferred routes that cost 1 turn and are favoured by the pathfinder
- 🔄 **Turn-based movement** — all drones move simultaneously each turn

The simulation parses and validates map files, discovers all valid paths, ranks them by cost, assigns drones intelligently across routes, and renders their movement step by step in the terminal.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗺️ **Map Parsing** | Validates input files with clear error messages and line numbers |
| 🔍 **Pathfinding** | Finds all valid paths using weighted graph traversal (Dijkstra-based) |
| 📊 **Path Ranking** | Sorts paths by cost, accounting for zone types and bottlenecks |
| 🤖 **Smart Assignment** | Distributes drones across paths to minimise total simulation turns |
| ⚙️ **Turn Simulation** | Two-phase movement engine with capacity and deadlock management |
| 🔒 **Deadlock Detection** | Raises a clear error if the simulation gets stuck |
| 🎨 **Terminal Visualisation** | Live coordinate-grid display with hub colours and drone positions |
| ✅ **Static Analysis** | Fully typed and linted with `flake8` and `mypy` |


## 🚀 Instructions

### 📦 Installation

Create the virtual environment and install all dependencies:

```bash
make install
```

This sets up a `fly_env` virtual environment and installs:
- `colorama` — terminal colour rendering
- `flake8` — style linting
- `mypy` — static type checking
- `types-colorama` — type stubs for colorama

---

### ▶️ Running the Simulation

```bash
make run MAP=maps/example.map
```

### 🐛 Debug Mode

```bash
make debug MAP=maps/example.map
```

### 🧹 Clean Temporary Files

```bash
make clean
```

---

## 🔍 Static Analysis

Run linting and type checking:

```bash
make lint
```

Strict mode (recommended):

```bash
make lint_strict
```

---

## 🗺️ Map File Format

```
nb_drones: 5

start_hub: hub 0 0 [color=green]
end_hub:   goal 10 10 [color=yellow]

hub: roof1     3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: obstacleX 5 5 [zone=blocked color=gray]

connection: hub-roof1
connection: corridorA-tunnelB [max_link_capacity=2]
```

### Zone Types

| Zone | Cost | Behaviour |
|---|---|---|
| `normal` | 1 turn | Standard movement |
| `priority` | 1 turn | Preferred by pathfinder |
| `restricted` | 2 turns | Drone spends 1 turn in transit + 1 turn arriving |
| `blocked` | ∞ | Impassable — never entered |

---

## ⚙️ How It Works

```
1. 📄 Parse & validate the map file
2. 🔗 Build hub neighbour lists from connections
3. 🔍 Find all valid paths from start to end (no blocked zones)
4. 📊 Sort paths by total movement cost
5. 🤖 Assign drones across paths using bottleneck analysis
6. 🔄 Simulate turn by turn:
      Phase 0 — resolve in-transit arrivals (restricted zones)
      Phase 1 — reserve movements for this turn
      Phase 2 — execute movements and update state
7. 🎨 Render the graph and drone positions after each turn
8. 🏁 Print final turn count when all drones reach the end
```

---

## 🎨 Visualisation

The terminal visualisation uses a **coordinate grid** to position hubs spatially, based on their `x y` values from the map file.

Each turn displays:
- 🟢 **Hubs** rendered in their configured colour with current drone count `[name:N]`
- 🔗 **Connections** drawn as lines between hubs
- 🚁 **Drone positions** shown inside their current hub label
- 📋 **Movement log** listing which drones moved and where

Colors are mapped from hub metadata (e.g. `color=red`) directly to `Colorama` terminal colours.

Output example :
```
[ST:2]****************[JU:2]****************[CO:1]****************[IN:0]****************[GO:0]
                          **
                          **
                          **
                        [DE:0]


 D0-correct_path  D2-junction  
```

---

## 📚 Resources

- [Fly-in Documentation](https://docs.python.org/3/)
- [Geek for Geeks](https://pypi.org/project/colorama/)
- [Dijkstra's Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Bresenham's Line Algorithm](https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm)

---

## 🤖 AI Usage

AI tools (Claude) were used during this project for:

- 💡 **Brainstorming** algorithm approaches (Dijkstra, path assignment strategies)
- 🐛 **Debugging** simulation logic and capacity management
- 📖 **Explaining** concepts like priority queues, bottleneck analysis, and Bresenham's algorithm
- 🎨 **Rendering ideas** for the terminal visualisation system

All implementation, integration, and understanding of the code was done manually. AI-generated suggestions were always reviewed, tested, and adapted before use.

