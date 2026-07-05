"""Entry point and main loop.

Kept intentionally thin: it wires modules together and pumps events. All real
work (map layout, drawing, collision) lives in the other modules.
"""
from __future__ import annotations

import tcod

import config
from entities import Player
from fov import update_fov
from game_map import GameMap, RectangularRoom
from render import render_entity, render_map


def build_map() -> tuple[GameMap, RectangularRoom]:
    """Step 1: a single hardcoded room in the middle of the map."""
    game_map = GameMap(config.MAP_WIDTH, config.MAP_HEIGHT)
    room = RectangularRoom(x=30, y=18, width=20, height=10)
    game_map.carve_room(room)
    return game_map, room


def handle_move(player: Player, game_map: GameMap, dx: int, dy: int) -> None:
    """Move the player by (dx, dy) only if the destination is walkable.

    Collision lives here, not in Player.move: the entity owns its position,
    the map owns what's passable, and main orchestrates the two.
    """
    dest_x, dest_y = player.x + dx, player.y + dy
    if game_map.walkable(dest_x, dest_y):
        player.move(dx, dy)
        update_fov(game_map, player.x, player.y, config.FOV_RADIUS)


def main() -> None:
    game_map, room = build_map()
    player = Player(*room.center)  # drop the dwarf in the middle of the room
    update_fov(game_map, player.x, player.y, config.FOV_RADIUS)  # see before first frame

    console = tcod.console.Console(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, order="F")

    # No tileset argument -> tcod uses its built-in default font.
    with tcod.context.new(
        columns=config.SCREEN_WIDTH,
        rows=config.SCREEN_HEIGHT,
        title="Moria",
    ) as context:
        while True:
            console.clear()
            render_map(console, game_map)
            render_entity(console, player, game_map)
            context.present(console)

            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
                if isinstance(event, tcod.event.KeyDown):
                    if event.sym in config.QUIT_KEYS:
                        raise SystemExit()
                    if event.sym in config.MOVE_KEYS:
                        dx, dy = config.MOVE_KEYS[event.sym]
                        handle_move(player, game_map, dx, dy)


if __name__ == "__main__":
    main()
