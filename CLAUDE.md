# Moria — A Dwarven Roguelike

## Project Summary
A traditional ASCII/tile roguelike set in the Mines of Moria (Middle Earth). The player controls a lone dwarf descending into Khazad-dûm to find out what happened to Balin's colony. Permadeath, procedural dungeons, turn-based combat.

**Current phase: core skeleton only.** No Shadow/corruption mechanic, no narrative content, no Moria-specific flavor yet — that comes after the base loop works. Do not build hooks, stubs, or placeholder systems for future mechanics unless explicitly asked. Build only what's specified below.

## Tech Stack
- Python 3.11+
- `tcod` (maintained libtcod fork) for rendering, FOV, and map primitives
- No other external dependencies unless discussed first — ask before adding a library
- Data-driven design: monster and item definitions live in JSON under `data/`, not hardcoded as Python classes/dicts in game logic

## Architecture
```
moria/
├── main.py              # game loop, input handling
├── entities.py          # Entity, Player, Monster classes
├── game_map.py          # tile grid, room/corridor generation
├── fov.py               # field of view (thin wrapper around tcod.map.compute_fov)
├── render.py             # draw functions
├── data/
│   ├── monsters.json    # monster stats: hp, attack, symbol, color, name
│   └── items.json       # item stats
└── config.py            # constants: screen size, colors, keybinds, tile chars
```

### Conventions
- Keep `main.py` thin — it should orchestrate, not contain game logic. Map generation, combat resolution, and rendering all live in their own modules.
- Entity behavior and stats should be data-driven where possible (read from JSON), not hardcoded in `if` chains.
- Favor small, single-purpose functions over large ones. This is a game loop — clarity matters more than cleverness, since we'll be extending this incrementally over many sessions.
- Use type hints throughout. I read Python daily for work and will be reviewing this code closely — don't obscure logic to be "clever" or overly abstracted.
- No premature optimization or generalization. Build the simplest thing that satisfies the current milestone.

## Build Order (do not skip ahead)
1. `game_map.py`: single hardcoded room, walls vs. floor tiles, render to screen
2. `main.py`: render the map, move an `@` symbol with arrow keys, collision against walls
3. Add FOV using `tcod.map.compute_fov`
4. Add one monster type, bump-to-attack melee combat, HP, death
5. Replace the hardcoded room with procedural room-and-corridor generation

Each step should be a working, playable state before moving to the next. Don't combine steps in one pass — I want to test and understand each layer before the next is added.

## What NOT to do right now
- No Shadow/corruption/despair mechanics yet — these are planned but not designed. Do not create placeholder fields, stat trackers, or comments implying this system exists.
- No inventory/item system until after step 5.
- No multiple dungeon levels/floor transitions until after step 5.
- No sound, no save/load, no menus beyond what's needed to quit the game.
- Don't invent lore, names, or flavor text beyond "dwarf" and "Moria" as the setting — that's a separate content pass later.

## Working Style
- I'm a data engineer comfortable in Python and SQL. Explain roguelike-specific concepts (FOV algorithms, dungeon generation approaches) briefly if you use a technique I haven't specified, but don't over-explain basic Python.
- Push back if a request from me conflicts with the build order above or reintroduces scope we've deferred — flag it rather than just complying.
- Prefer editing/extending existing files over creating new ones unless a new module is clearly warranted by the architecture above.
