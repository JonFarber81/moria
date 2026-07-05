"""Drawing functions. Nothing here mutates game state — it only reads the
map/entities and paints them onto a tcod console.

render.py is the *only* module that knows what a tile looks like. game_map.py
stores tile types as integers; the table below turns those into glyphs+colors.
"""
from __future__ import annotations

import tcod.console

import config
from entities import Entity, Player
from game_map import DOWN_STAIRS, FLOOR, WALL, GameMap
from levels import level_name
from message_log import MessageLog

# Tile type -> (character, lit color, dark/remembered color). Adding a new
# tile type is a one-row change here plus a constant in game_map.py.
TILE_GRAPHICS: dict[int, tuple[str, tuple[int, int, int], tuple[int, int, int]]] = {
    WALL: (config.CHAR_WALL, config.COLOR_WALL, config.COLOR_WALL_DARK),
    FLOOR: (config.CHAR_FLOOR, config.COLOR_FLOOR, config.COLOR_FLOOR_DARK),
    DOWN_STAIRS: (config.CHAR_DOWN_STAIRS, config.COLOR_STAIRS, config.COLOR_STAIRS_DARK),
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


def render_ui(console: tcod.console.Console, player: Player, depth: int) -> None:
    """Draw HP, effective attack/defense, and the named dungeon level on the
    bottom panel. Showing Atk/Def here makes equipment changes legible."""
    console.print(
        x=config.LOG_X,
        y=config.UI_HP_Y,
        text=(
            f"HP: {player.hp}/{player.max_hp}   "
            f"Atk: {player.power}   Def: {player.defense}   "
            f"Depth {depth}: {level_name(depth)}"
        ),
        fg=config.COLOR_PLAYER,
    )


def render_inventory_menu(
    console: tcod.console.Console, player: Player, title: str
) -> None:
    """Draw the inventory as a bordered overlay listing carried items by
    letter, plus what's currently equipped. `title` says what selecting a
    letter will do ("Use / equip" or "Drop")."""
    items = player.inventory.items
    equipment = player.equipment

    # +2 rows for the two equipment lines, +1 header spacing; min size for a
    # readable empty menu.
    width = 40
    height = max(len(items), 1) + 5
    x = (config.SCREEN_WIDTH - width) // 2
    y = (config.MAP_HEIGHT - height) // 2

    console.draw_frame(x, y, width, height, title=title, fg=config.COLOR_TEXT, bg=config.COLOR_BLACK)

    def name_or_none(item) -> str:
        return item.name if item else "(none)"

    console.print(x + 1, y + 1, f"Weapon: {name_or_none(equipment.weapon)}", fg=config.COLOR_PLAYER)
    console.print(x + 1, y + 2, f"Armor:  {name_or_none(equipment.armor)}", fg=config.COLOR_PLAYER)

    if not items:
        console.print(x + 1, y + 4, "(pack is empty)", fg=config.COLOR_TEXT)
        return

    for i, item in enumerate(items):
        letter = chr(ord("a") + i)
        console.print(x + 1, y + 4 + i, f"{letter}) {item.name}", fg=config.COLOR_TEXT)


def render_messages(console: tcod.console.Console, log: MessageLog) -> None:
    """Draw the most recent messages in the bottom panel, newest at the
    bottom. Only the last LOG_HEIGHT lines are shown; older history scrolls
    off but is retained in the log."""
    recent = log.messages[-config.LOG_HEIGHT :]
    for i, message in enumerate(recent):
        console.print(
            x=config.LOG_X,
            y=config.LOG_Y + i,
            text=message.text,
            fg=message.fg,
        )
