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
CHAR_DOWN_STAIRS = ">"

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

COLOR_STAIRS = (255, 225, 140)   # down-stairs, bright gold (lit)
COLOR_STAIRS_DARK = (70, 62, 38)  # remembered

# UI text
COLOR_TEXT = (200, 200, 200)     # default message-log color
COLOR_DEATH = (191, 0, 0)        # death / game-over red

# --- UI layout (bottom panel, in the rows below the map) ------------------
# Map occupies rows 0..MAP_HEIGHT-1; these rows sit beneath it.
UI_HP_Y = MAP_HEIGHT             # HP readout row
LOG_X = 1                        # left margin for message lines
LOG_Y = MAP_HEIGHT + 1           # first message row
LOG_HEIGHT = SCREEN_HEIGHT - LOG_Y  # how many recent messages fit on screen

# --- FOV ------------------------------------------------------------------
FOV_RADIUS = 8  # how many tiles the dwarf's torch reaches

# --- Dungeon generation ---------------------------------------------------
MAX_ROOMS = 30            # upper bound on placement attempts; overlaps are skipped
ROOM_MIN_SIZE = 6
ROOM_MAX_SIZE = 10
MAX_MONSTERS_PER_ROOM = 2  # 0..this monsters scattered per room (never the first)
MAX_ITEMS_PER_ROOM = 1     # 0..this items scattered per room (first included)

# Spawn weighting: a monster's spawn weight is multiplied by this factor for
# every level deeper than its min_depth. <1 means shallow (low-min_depth)
# creatures fade as you descend, so deep levels fill with the tougher foes that
# unlocked most recently. Lower = sharper difficulty ramp.
SPAWN_DEPTH_DECAY = 0.55

# --- Inventory ------------------------------------------------------------
INVENTORY_CAPACITY = 26    # a-z selectable slots

# --- Keybinds -------------------------------------------------------------
# Movement keys -> (dx, dy) deltas. Arrow keys for now; vi-keys / diagonals
# can be added as extra rows here without touching the input loop.
MOVE_KEYS: dict[tcod.event.KeySym, tuple[int, int]] = {
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
}

# Keys that quit the game (in normal play).
QUIT_KEYS = (tcod.event.KeySym.ESCAPE, tcod.event.KeySym.q)

# Item / inventory keys.
KEY_PICKUP = tcod.event.KeySym.g       # pick up item under the player
KEY_INVENTORY = tcod.event.KeySym.i    # open inventory to use/equip
KEY_DROP = tcod.event.KeySym.d         # open inventory to drop
KEY_CANCEL = tcod.event.KeySym.ESCAPE  # close a menu

# Descend the down-stairs. '>' is Shift + '.', so we match the PERIOD key with
# Shift held (checked in the input loop).
KEY_DESCEND = tcod.event.KeySym.PERIOD
