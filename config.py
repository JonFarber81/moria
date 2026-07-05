"""Game-wide constants: screen dimensions, colors, and tile characters.

Kept deliberately flat and simple — this is the single place to tweak the
look and size of the game. As systems grow (keybinds, more colors), they get
their own clearly-labeled section here rather than being scattered.
"""
from __future__ import annotations

import tcod.event

# --- Screen ---------------------------------------------------------------
# Measured in tiles (character cells), not pixels. tcod maps one cell per glyph.
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

# --- Map ------------------------------------------------------------------
MAP_WIDTH = 80
MAP_HEIGHT = 45  # a few rows reserved at the bottom for a future message log

# --- Tile glyphs ----------------------------------------------------------
CHAR_WALL = "#"
CHAR_FLOOR = "."
CHAR_PLAYER = "@"

# --- Colors (R, G, B) -----------------------------------------------------
# tcod accepts (r, g, b) tuples in 0-255. Distinct fg/bg per tile type lets us
# render explored-but-not-visible tiles dimmer later without touching glyphs.
COLOR_WALL = (130, 110, 50)      # dwarven stone, warm ochre (lit)
COLOR_FLOOR = (60, 60, 70)       # cool grey floor (lit)
COLOR_PLAYER = (255, 255, 255)   # bright white @
COLOR_BLACK = (0, 0, 0)

# Dim variants for explored-but-not-currently-visible tiles (memory of the
# mine). Same glyphs, muted color, so the map you've walked stays as a ghost.
COLOR_WALL_DARK = (45, 40, 25)
COLOR_FLOOR_DARK = (25, 25, 30)

# --- FOV ------------------------------------------------------------------
FOV_RADIUS = 8  # how many tiles the dwarf's torch reaches

# --- Keybinds -------------------------------------------------------------
# Movement keys -> (dx, dy) deltas. Arrow keys for now; vi-keys / diagonals
# can be added as extra rows here without touching the input loop.
MOVE_KEYS: dict[tcod.event.KeySym, tuple[int, int]] = {
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
}

# Keys that quit the game.
QUIT_KEYS = (tcod.event.KeySym.ESCAPE, tcod.event.KeySym.q)
