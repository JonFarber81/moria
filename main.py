"""Entry point and main loop.

Kept intentionally thin: it wires modules together and pumps events. Real work
lives elsewhere — map in game_map, drawing in render, FOV in fov, and attack
resolution in combat.
"""
from __future__ import annotations

import random

import tcod

import combat
import config
from entities import Monster, Player, blocking_monster_at
from fov import update_fov
from game_map import GameMap, RectangularRoom, generate_dungeon
from message_log import MessageLog
from render import render_entity, render_map, render_messages, render_ui


def place_monsters(
    rooms: list[RectangularRoom], game_map: GameMap
) -> list[Monster]:
    """Scatter 0..MAX_MONSTERS_PER_ROOM orcs through every room except the
    first (the player's start stays safe). Skips tiles already taken so two
    orcs never share a square."""
    monsters: list[Monster] = []
    occupied: set[tuple[int, int]] = set()

    for room in rooms[1:]:
        for _ in range(random.randint(0, config.MAX_MONSTERS_PER_ROOM)):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if (x, y) in occupied or not game_map.walkable(x, y):
                continue
            occupied.add((x, y))
            monsters.append(Monster.spawn("orc", x, y))

    return monsters


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
    game_map, rooms = generate_dungeon(config.MAP_WIDTH, config.MAP_HEIGHT)
    player = Player(*rooms[0].center)  # start in the first room
    monsters = place_monsters(rooms, game_map)
    update_fov(game_map, player.x, player.y, config.FOV_RADIUS)

    message_log = MessageLog()

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
            render_messages(console, message_log)
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
                        message_log.add_all(result)
                        message_log.add_all(monsters_turn(player, game_map, monsters))
                        if not player.is_alive:
                            message_log.add("You have died.", config.COLOR_DEATH)


if __name__ == "__main__":
    main()
