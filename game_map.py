"""The dungeon: a grid of tiles plus (for now) a single hardcoded room.

Design choice: the map is a plain 2D NumPy array of *tile-type integers*
(WALL / FLOOR), not a grid of rich objects. Presentation (glyph, color) is
NOT stored here — render.py maps tile types to how they look. This keeps the
map as pure data, which also makes the FOV step (a NumPy transparency array)
drop in cleanly later.
"""
from __future__ import annotations

import numpy as np

# --- Tile types -----------------------------------------------------------
# Small integer codes. render.py owns how each one is drawn.
WALL = 0
FLOOR = 1


class RectangularRoom:
    """A room defined by its top-left corner and size.

    Stores its bounds so we can later ask 'what's the center?' (for placing
    the player / stairs) and 'do two rooms overlap?' (for procgen in step 5).
    """

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> tuple[int, int]:
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    @property
    def inner(self) -> tuple[slice, slice]:
        """The floor area of the room as NumPy (row, col) slices.

        Note the +1 on the top-left: it leaves a one-tile wall border so
        adjacent rooms never share a wall-less edge. Returned as (y, x)
        because NumPy indexes rows (y) first.
        """
        return slice(self.y1 + 1, self.y2), slice(self.x1 + 1, self.x2)


class GameMap:
    """Owns the tile grid and answers questions about it."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        # Start solid: every tile is WALL. Rooms carve FLOOR out of the rock.
        # Shape is (height, width) so indexing reads tiles[y, x].
        self.tiles = np.full((height, width), fill_value=WALL, dtype=np.int8)

        # FOV state, updated each turn by fov.update_fov:
        #   visible  — tiles the dwarf can see right now (drawn lit)
        #   explored — tiles ever seen (drawn dim when not currently visible)
        self.visible = np.full((height, width), fill_value=False, dtype=bool)
        self.explored = np.full((height, width), fill_value=False, dtype=bool)

    @property
    def transparent(self) -> np.ndarray:
        """Boolean grid: True where light passes through (floors do, walls
        don't). Derived from tile types so FOV never falls out of sync with
        the map. compute_fov consumes this each turn."""
        return self.tiles == FLOOR

    def in_bounds(self, x: int, y: int) -> bool:
        """True if (x, y) is inside the map grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def walkable(self, x: int, y: int) -> bool:
        """True if an entity may stand on (x, y): in bounds and not solid rock.

        Bounds are checked first so an off-map coordinate never indexes the
        tile array (which would wrap on negatives / raise on overflow).
        """
        return self.in_bounds(x, y) and self.tiles[y, x] == FLOOR

    def carve_room(self, room: RectangularRoom) -> None:
        """Cut a room's floor out of the surrounding rock.

        Trusts `room.inner` to define the floor region (including its one-tile
        wall border); this method stays dumb and just paints FLOOR there.
        """
        self.tiles[room.inner] = FLOOR
