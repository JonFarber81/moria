"""The dungeon: a grid of tiles plus (for now) a single hardcoded room.

Design choice: the map is a plain 2D NumPy array of *tile-type integers*
(WALL / FLOOR), not a grid of rich objects. Presentation (glyph, color) is
NOT stored here — render.py maps tile types to how they look. This keeps the
map as pure data, which also makes the FOV step (a NumPy transparency array)
drop in cleanly later.
"""
from __future__ import annotations

import random

import numpy as np

import config

# --- Tile types -----------------------------------------------------------
# Small integer codes. render.py owns how each one is drawn. WALL is the only
# solid/opaque tile — everything else is walkable and lets light through, which
# is why walkable() and transparent() below test "not WALL" rather than listing
# every passable type.
WALL = 0
FLOOR = 1
DOWN_STAIRS = 2


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

    def intersects(self, other: RectangularRoom) -> bool:
        """True if this room overlaps `other` (including touching edges).
        Used to reject candidate rooms so they don't merge into blobs."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


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

        # Location of the down-stairs, set by generate_dungeon. None on a bare
        # map (e.g. tests that don't generate rooms).
        self.down_stairs: tuple[int, int] | None = None

    @property
    def transparent(self) -> np.ndarray:
        """Boolean grid: True where light passes through. Only walls block it,
        so floors and stairs are transparent. Derived from tile types so FOV
        never falls out of sync with the map. compute_fov consumes this."""
        return self.tiles != WALL

    def in_bounds(self, x: int, y: int) -> bool:
        """True if (x, y) is inside the map grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def walkable(self, x: int, y: int) -> bool:
        """True if an entity may stand on (x, y): in bounds and not solid rock.
        Floors and stairs are walkable; only walls block movement.

        Bounds are checked first so an off-map coordinate never indexes the
        tile array (which would wrap on negatives / raise on overflow).
        """
        return self.in_bounds(x, y) and self.tiles[y, x] != WALL

    def carve_room(self, room: RectangularRoom) -> None:
        """Cut a room's floor out of the surrounding rock.

        Trusts `room.inner` to define the floor region (including its one-tile
        wall border); this method stays dumb and just paints FLOOR there.
        """
        self.tiles[room.inner] = FLOOR

    def carve_tunnel(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> None:
        """Carve an L-shaped corridor between two points (room centers).

        The bend goes horizontal-then-vertical or vertical-then-horizontal,
        chosen at random, which keeps corridors from all sharing the same
        elbow orientation and makes the map feel less uniform.
        """
        x1, y1 = start
        x2, y2 = end
        if random.random() < 0.5:
            corner = (x2, y1)  # move horizontally first, then vertically
        else:
            corner = (x1, y2)  # move vertically first, then horizontally

        self._carve_straight(start, corner)
        self._carve_straight(corner, end)

    def _carve_straight(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> None:
        """Carve a single horizontal or vertical run of FLOOR between two
        points that share a row or column. Endpoints inclusive."""
        x1, y1 = start
        x2, y2 = end
        if x1 == x2:  # vertical run
            lo, hi = sorted((y1, y2))
            self.tiles[lo : hi + 1, x1] = FLOOR
        else:  # horizontal run
            lo, hi = sorted((x1, x2))
            self.tiles[y1, lo : hi + 1] = FLOOR


def generate_dungeon(width: int, height: int) -> tuple[GameMap, list[RectangularRoom]]:
    """Build a room-and-corridor dungeon.

    Attempts MAX_ROOMS placements of randomly-sized rooms, discarding any that
    intersect an already-placed room. Each accepted room is tunneled to the
    previous one, so the sequence of rooms forms a connected chain — every
    floor tile is reachable from the first room.

    Returns the map and the rooms in placement order (rooms[0] is where the
    player starts).
    """
    dungeon = GameMap(width, height)
    rooms: list[RectangularRoom] = []

    for _ in range(config.MAX_ROOMS):
        room_w = random.randint(config.ROOM_MIN_SIZE, config.ROOM_MAX_SIZE)
        room_h = random.randint(config.ROOM_MIN_SIZE, config.ROOM_MAX_SIZE)
        # Leave a 1-tile margin so rooms never touch the map border.
        x = random.randint(0, width - room_w - 1)
        y = random.randint(0, height - room_h - 1)

        candidate = RectangularRoom(x, y, room_w, room_h)
        if any(candidate.intersects(other) for other in rooms):
            continue  # overlaps an existing room; try another placement

        dungeon.carve_room(candidate)
        if rooms:  # connect to the previously placed room
            dungeon.carve_tunnel(rooms[-1].center, candidate.center)
        rooms.append(candidate)

    # Down-stairs in the last room carved — farthest along the corridor chain
    # from the player's start room, so descending means crossing the level.
    stairs_x, stairs_y = rooms[-1].center
    dungeon.tiles[stairs_y, stairs_x] = DOWN_STAIRS
    dungeon.down_stairs = (stairs_x, stairs_y)

    return dungeon, rooms
