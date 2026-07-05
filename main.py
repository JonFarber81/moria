"""Entry point and main loop.

Kept intentionally thin: it wires modules together and pumps events. Real work
lives elsewhere — map in game_map, drawing in render, FOV in fov, and attack
resolution in combat.
"""
from __future__ import annotations

import tcod

import combat
import config
from entities import Monster, Player, blocking_monster_at
from fov import update_fov
from game_map import GameMap, RectangularRoom
from render import render_entity, render_map, render_ui


def build_map() -> tuple[GameMap, RectangularRoom]:
    """Step 1: a single hardcoded room in the middle of the map."""
    game_map = GameMap(config.MAP_WIDTH, config.MAP_HEIGHT)
    room = RectangularRoom(x=30, y=18, width=20, height=10)
    game_map.carve_room(room)
    return game_map, room


def spawn_monsters() -> list[Monster]:
    """Step 4: a couple of hardcoded orcs to fight. Procedural placement
    arrives with the dungeon generator in Step 5."""
    return [
        Monster.spawn("orc", x=45, y=25),
        Monster.spawn("orc", x=34, y=20),
    ]


def player_action(
    player: Player, game_map: GameMap, monsters: list[Monster], dx: int, dy: int
) -> list[str]:
    """Resolve the player's intent in direction (dx, dy) and report whether a
    turn was actually spent via the returned messages / caller logic.

    Bumping a monster attacks it; bumping a walkable tile moves (and updates
    FOV); bumping a wall does nothing and costs no turn.
    Returns the list of messages produced (empty list is still a valid turn
    for a move; None means no turn was taken).
    """
    dest_x, dest_y = player.x + dx, player.y + dy

    target = blocking_monster_at(monsters, dest_x, dest_y)
    if target is not None:
        return combat.resolve_attack(player, target)

    if game_map.walkable(dest_x, dest_y):
        player.move(dx, dy)
        update_fov(game_map, player.x, player.y, config.FOV_RADIUS)
        return []

    return None  # bumped a wall — no turn taken


def monsters_turn(
    player: Player, game_map: GameMap, monsters: list[Monster]
) -> list[str]:
    """Let every living monster act, then clear out the dead."""
    messages: list[str] = []
    for monster in monsters:
        if monster.is_alive:
            messages += monster.take_turn(player, game_map, monsters)
    monsters[:] = [m for m in monsters if m.is_alive]
    return messages


def main() -> None:
    game_map, room = build_map()
    player = Player(*room.center)
    monsters = spawn_monsters()
    update_fov(game_map, player.x, player.y, config.FOV_RADIUS)

    console = tcod.console.Console(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, order="F")

    with tcod.context.new(
        columns=config.SCREEN_WIDTH,
        rows=config.SCREEN_HEIGHT,
        title="Moria",
    ) as context:
        while True:
            console.clear()
            render_map(console, game_map)
            for monster in monsters:
                render_entity(console, monster, game_map)
            render_entity(console, player, game_map)
            render_ui(console, player)
            if not player.is_alive:
                console.print(x=1, y=config.MAP_HEIGHT + 2, text="You have died.", fg=(191, 0, 0))
            context.present(console)

            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
                if isinstance(event, tcod.event.KeyDown):
                    if event.sym in config.QUIT_KEYS:
                        raise SystemExit()
                    # Dead dwarves take no more turns; only quitting works.
                    if not player.is_alive:
                        continue
                    if event.sym in config.MOVE_KEYS:
                        dx, dy = config.MOVE_KEYS[event.sym]
                        result = player_action(player, game_map, monsters, dx, dy)
                        if result is None:
                            continue  # bumped a wall; monsters don't get a free turn
                        for line in result:
                            print(line)
                        for line in monsters_turn(player, game_map, monsters):
                            print(line)


if __name__ == "__main__":
    main()
