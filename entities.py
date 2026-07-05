"""Things that live on the map and occupy a tile.

For now that's just the Player. Monsters (Step 4) will share the Entity base
but be built from JSON data rather than constructed directly like Player is.
"""
from __future__ import annotations

import config


class Entity:
    """Anything drawn at an (x, y) position with a glyph and color.

    Deliberately thin — no stats, no behavior. Combat/HP arrive in Step 4.
    """

    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: tuple[int, int, int],
        name: str,
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name

    def move(self, dx: int, dy: int) -> None:
        """Shift position by a delta. Callers decide if the move is legal
        first — the entity itself doesn't know about walls."""
        self.x += dx
        self.y += dy


class Player(Entity):
    """The dwarf the human controls."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__(
            x=x,
            y=y,
            char=config.CHAR_PLAYER,
            color=config.COLOR_PLAYER,
            name="Dwarf",
        )
