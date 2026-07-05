"""Drawing functions. Nothing here mutates game state — it only reads the
map/entities and paints them onto a tcod console.

render.py is the *only* module that knows what a tile looks like. game_map.py
stores tile types as integers; the table below turns those into glyphs+colors.
"""
from __future__ import annotations

import tcod.console

import config
from entities import Entity
from game_map import FLOOR, WALL, GameMap

# Tile type -> (character, lit color, dark/remembered color). Adding a new
# tile type is a one-row change here plus a constant in game_map.py.
TILE_GRAPHICS: dict[int, tuple[str, tuple[int, int, int], tuple[int, int, int]]] = {
    WALL: (config.CHAR_WALL, config.COLOR_WALL, config.COLOR_WALL_DARK),
    FLOOR: (config.CHAR_FLOOR, config.COLOR_FLOOR, config.COLOR_FLOOR_DARK),
}


def render_map(console: tcod.console.Console, game_map: GameMap) -> None:
    """Paint the map with three states per tile:
      visible  -> lit color
      explored -> dark (remembered) color
      neither  -> left black (unknown; console was cleared this frame)
    """
    for y in range(game_map.height):
        for x in range(game_map.width):
            char, lit, dark = TILE_GRAPHICS[game_map.tiles[y, x]]
            if game_map.visible[y, x]:
                console.print(x=x, y=y, text=char, fg=lit, bg=config.COLOR_BLACK)
            elif game_map.explored[y, x]:
                console.print(x=x, y=y, text=char, fg=dark, bg=config.COLOR_BLACK)
            # else: unexplored -> draw nothing, stays black


def render_entity(
    console: tcod.console.Console, entity: Entity, game_map: GameMap
) -> None:
    """Paint an entity's glyph — but only if it stands on a currently visible
    tile. You shouldn't see a monster through a wall or in the dark."""
    if game_map.visible[entity.y, entity.x]:
        console.print(x=entity.x, y=entity.y, text=entity.char, fg=entity.color)
