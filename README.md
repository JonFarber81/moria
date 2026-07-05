# Moria — A Dwarven Roguelike

A traditional ASCII roguelike set in the Mines of Moria. You play a lone dwarf descending into Khazad-dûm to uncover what happened to Balin's colony. Permadeath, procedural dungeons, turn-based combat.

## Stack

- Python 3.11+
- [`tcod`](https://python-tcod.readthedocs.io/) for rendering, FOV, and map primitives
- Data-driven monster/item definitions in `data/` (JSON)

## Project Structure

```
moria/
├── main.py              # game loop, input handling
├── entities.py          # Entity, Player, Monster classes
├── game_map.py          # tile grid, room/corridor generation
├── fov.py               # FOV (thin wrapper around tcod.map.compute_fov)
├── render.py            # draw functions
├── data/
│   ├── monsters.json    # monster stats: hp, attack, symbol, color, name
│   └── items.json       # item stats
└── config.py            # constants: screen size, colors, keybinds, tile chars
```

## Build Order

The game is being built in deliberate layers — each step is playable before the next begins:

1. **Map** — single hardcoded room, walls vs. floor, render to screen
2. **Player movement** — move `@` with arrow keys, wall collision
3. **FOV** — field of view via `tcod.map.compute_fov`
4. **Combat** — one monster type, bump-to-attack melee, HP, death
5. **Procedural generation** — replace hardcoded room with room-and-corridor dungeon

> Current phase: core skeleton. No inventory, no multi-level dungeons, no narrative content yet.

## Running

```bash
pip install tcod
python main.py
```

## Design Notes

- `main.py` stays thin — game logic lives in dedicated modules
- Entity stats are data-driven (JSON), not hardcoded
- Small, single-purpose functions throughout; clarity over cleverness
- No premature optimization or generalization
