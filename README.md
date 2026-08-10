# Planisuss

A small ecosystem simulation — Vegetob grows, Erbast graze, Carviz hunt — built from scratch in Python and animated with matplotlib. Final exam project for *Computer Programming, Algorithms and Data Structures, Mod. 1*, Bachelor in Artificial Intelligence, Università degli Studi di Pavia (A.Y. 2022/23).

Based on the [v0.95 specification](docs/assignment_spec.pdf) by Prof. Stefano Ferrari, freely inspired by Conway's Game of Life and Wa-Tor.

**Author:** Marco Zennaro 
**Suggestions and support:** Fabio Bruschi

---

## The world

Planisuss is a `NUMCELL × NUMCELL` grid of cells, either water or ground. Three species share it:

| Species | Role | Behaviour |
|---|---|---|
| **Vegetob** | Passive | Grows on ground cells (density 0–100), regrows slower where it's been grazed |
| **Erbast** | Herbivore | Eats Vegetob, forms herds, flees Carviz |
| **Carviz** | Carnivore | Hunts Erbast, forms prides, fears large herds and rival prides |

Every day runs through five phases in order: **Growing → Movement → Grazing → Struggle → Spawning**. Full rules and design decisions are written up in the [report](docs/report.pdf).

## Running it

```bash
git clone <this-repo-url>
cd planisuss
pip install -r requirements.txt
python src/main.py
```

A startup menu appears first — close the window to begin a new simulation, or press `L` to load a previous save if one is found in the working directory.

## Controls

| Key | Action |
|---|---|
| `SPACE` | Pause / resume the simulation |
| `W` | World view (paused) |
| `V` | Vegetob density graph (paused) |
| `P` | Population graphs (paused) |
| `G` | General stats graph (paused) |
| `X` | Save screen (paused) |
| `←` / `→` | Step back / forward through saved days (paused) |
| `L` | Load a previous save (startup menu) |
| `D` | Developer options — pick from 14 preset worlds (startup menu, requires `NUMCELL = 5`) |
| `S` | Save the current screen as a `.png` (matplotlib built-in) |

## Project structure

```
planisuss/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── main.py              # entry point, animation loop
│   ├── Classes.py           # Cell, Animal (Carviz/Erbast), Group (Pride/Herd)
│   ├── Functions.py         # simulation logic — movement, struggle, spawning
│   ├── GlobalVariables.py   # shared runtime state
│   ├── settings.py          # tunable constants (world size, energy, colours...)
│   └── DoublyLinkedList.py  # bounded day-by-day history, used for rewind/replay
└── docs/
    ├── assignment_spec.pdf  # original v0.95 brief
    ├── report.pdf           # full write-up of the design and implementation
    └── presentation.pptx    # project presentation slides
```

## How it's built

- **World & storage** — a NumPy matrix of `Cell` objects, each tracking coordinates, Vegetob density, current population, and a cached RGB colour.
- **Entities** — `Animal` subclasses into `Carviz`/`Erbast`; `Group` subclasses into `Pride`/`Herd`. Group decisions are weighted by the average state of their members, and individuals can split off based on their own energy and social attitude.
- **History** — a custom doubly linked list caps day-by-day history at `MAX_DAY_STORAGE` entries across three parallel streams (world state, rendered images, stats), powering the rewind/replay controls.
- **Visualisation** — everything renders through `matplotlib.animation.FuncAnimation`; each cell's population and Vegetob density map to a fixed RGB colour, composited into a single image per frame.
- **IDs** — every animal gets a code like `0C32-4\` (day of birth, species, birth cell, litter order); every group gets a code like `H100` (type + running count since day zero) — handy for following an individual through the console output.

## Notes

Values in this implementation (colours, some constants, minor rule tweaks) differ slightly from the original v0.95 spec by design choice — none affect the core mechanics. Details on every deviation are in the report.

## License

Academic project — shared for portfolio and reference purposes.
