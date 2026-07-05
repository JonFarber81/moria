"""Entry point and main loop.

Kept intentionally thin: it wires modules together and pumps events. Real work
lives elsewhere — map in game_map, drawing in render, FOV in fov, attack
resolution in combat, and item handling in inventory.

Every player intent resolves to a (messages, took_turn) pair. `apply_result`
funnels that through one place: log the messages, and only if a turn was truly
spent do the monsters get to act. Bumping a wall or a no-op menu selection
costs no turn.
"""
from __future__ import annotations

import random

import tcod

import combat
import config
import inventory
from entities import (
    ITEM_TYPES,
    Item,
    Monster,
    Player,
    blocking_monster_at,
    monster_types_for_depth,
)
from fov import update_fov
from game_map import DOWN_STAIRS, GameMap, RectangularRoom, generate_dungeon
from levels import level_arrival, level_name
from message_log import MessageLog
from render import (
    render_entity,
    render_inventory_menu,
    render_map,
    render_messages,
    render_ui,
)

# Input modes. "play" is normal; the others show the inventory overlay and
# reinterpret letter keys as item selection.
MODE_PLAY = "play"
MODE_USE = "use"
MODE_DROP = "drop"

MENU_TITLES = {
    MODE_USE: "Use / equip - press a-z (Esc cancels)",
    MODE_DROP: "Drop - press a-z (Esc cancels)",
}


def place_monsters(
    rooms: list[RectangularRoom], game_map: GameMap, depth: int
) -> list[Monster]:
    """Scatter 0..MAX_MONSTERS_PER_ROOM monsters through every room except the
    first (the player's start stays safe). The pool of creature types widens
    with depth, so deeper levels grow more dangerous."""
    monsters: list[Monster] = []
    occupied: set[tuple[int, int]] = set()
    eligible = monster_types_for_depth(depth)

    for room in rooms[1:]:
        for _ in range(random.randint(0, config.MAX_MONSTERS_PER_ROOM)):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if (x, y) in occupied or not game_map.walkable(x, y):
                continue
            occupied.add((x, y))
            monsters.append(Monster.spawn(random.choice(eligible), x, y))

    return monsters


def place_items(rooms: list[RectangularRoom], game_map: GameMap) -> list[Item]:
    """Scatter random items through every room (the start room included, so
    the dwarf may find gear immediately)."""
    items: list[Item] = []
    occupied: set[tuple[int, int]] = set()
    item_keys = list(ITEM_TYPES.keys())

    for room in rooms:
        for _ in range(random.randint(0, config.MAX_ITEMS_PER_ROOM)):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if (x, y) in occupied or not game_map.walkable(x, y):
                continue
            occupied.add((x, y))
            items.append(Item.spawn(random.choice(item_keys), x, y))

    return items


def build_level(
    player: Player, depth: int
) -> tuple[GameMap, list[RectangularRoom], list[Monster], list[Item]]:
    """Generate a fresh dungeon level for the given depth, populate it, and drop
    the player in the first room. The player object itself persists (hp,
    inventory, equipment carry between levels) — only the surrounding level is
    new; deeper levels draw from a tougher monster pool."""
    game_map, rooms = generate_dungeon(config.MAP_WIDTH, config.MAP_HEIGHT)
    monsters = place_monsters(rooms, game_map, depth)
    floor_items = place_items(rooms, game_map)
    player.x, player.y = rooms[0].center
    update_fov(game_map, player.x, player.y, config.FOV_RADIUS)
    return game_map, rooms, monsters, floor_items


def player_action(
    player: Player,
    game_map: GameMap,
    monsters: list[Monster],
    floor_items: list[Item],
    dx: int,
    dy: int,
) -> inventory.TurnResult:
    """Resolve a movement key into (messages, took_turn).

    Bumping a monster attacks it (turn spent); bumping a walkable tile moves
    and updates FOV (turn spent, and notes any items underfoot); bumping a
    wall does nothing (no turn)."""
    dest_x, dest_y = player.x + dx, player.y + dy

    target = blocking_monster_at(monsters, dest_x, dest_y)
    if target is not None:
        return (combat.resolve_attack(player, target), True)

    if game_map.walkable(dest_x, dest_y):
        player.move(dx, dy)
        update_fov(game_map, player.x, player.y, config.FOV_RADIUS)
        return (_items_underfoot_message(player, floor_items), True)

    return ([], False)  # bumped a wall — no turn taken


def _items_underfoot_message(player: Player, floor_items: list[Item]) -> list[str]:
    """A 'you see ...' line for whatever the player just stepped onto, or no
    message if the tile is bare."""
    here = [it for it in floor_items if it.x == player.x and it.y == player.y]
    if len(here) == 1:
        return [f"You see a {here[0].name} here."]
    if len(here) > 1:
        return ["You see several items here."]
    return []


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


def apply_result(
    result: inventory.TurnResult,
    player: Player,
    game_map: GameMap,
    monsters: list[Monster],
    log: MessageLog,
) -> None:
    """Single funnel for any player action: log its messages, and if it spent
    a turn, let the monsters act and check for the dwarf's death."""
    messages, took_turn = result
    log.add_all(messages)
    if took_turn:
        log.add_all(monsters_turn(player, game_map, monsters))
        if not player.is_alive:
            log.add("You have died.", config.COLOR_DEATH)


def main() -> None:
    # Player is created first so it survives level regeneration; build_level
    # only repositions it and rebuilds the world around it.
    player = Player(0, 0)
    depth = 1
    game_map, rooms, monsters, floor_items = build_level(player, depth)

    message_log = MessageLog()
    message_log.add(f"{level_name(depth)} (depth {depth}).")
    message_log.add(level_arrival(depth))
    mode = MODE_PLAY

    console = tcod.console.Console(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, order="F")

    with tcod.context.new(
        columns=config.SCREEN_WIDTH,
        rows=config.SCREEN_HEIGHT,
        title="Moria",
    ) as context:
        while True:
            console.clear()
            render_map(console, game_map)
            for item in floor_items:
                render_entity(console, item, game_map)
            for monster in monsters:
                render_entity(console, monster, game_map)
            render_entity(console, player, game_map)
            render_ui(console, player, depth)
            render_messages(console, message_log)
            if mode != MODE_PLAY:
                render_inventory_menu(console, player, MENU_TITLES[mode])
            context.present(console)

            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
                if not isinstance(event, tcod.event.KeyDown):
                    continue
                sym = event.sym

                if mode == MODE_PLAY:
                    if sym in config.QUIT_KEYS:
                        raise SystemExit()
                    if not player.is_alive:
                        continue  # dead dwarves only quit
                    if sym in config.MOVE_KEYS:
                        dx, dy = config.MOVE_KEYS[sym]
                        apply_result(
                            player_action(player, game_map, monsters, floor_items, dx, dy),
                            player, game_map, monsters, message_log,
                        )
                    elif sym == config.KEY_PICKUP:
                        apply_result(
                            inventory.pick_up(player, floor_items),
                            player, game_map, monsters, message_log,
                        )
                    elif sym == config.KEY_INVENTORY:
                        mode = MODE_USE
                    elif sym == config.KEY_DROP:
                        mode = MODE_DROP
                    elif sym == config.KEY_DESCEND and (event.mod & tcod.event.Modifier.SHIFT):
                        # '>' descends, but only while standing on the stairs.
                        if game_map.tiles[player.y, player.x] == DOWN_STAIRS:
                            depth += 1
                            game_map, rooms, monsters, floor_items = build_level(player, depth)
                            message_log.add(f"You descend to {level_name(depth)} (depth {depth}).")
                            message_log.add(level_arrival(depth))
                        else:
                            message_log.add("There are no stairs here to descend.")
                else:
                    # Inventory menu open: Esc cancels, a-z selects an item.
                    if sym == config.KEY_CANCEL:
                        mode = MODE_PLAY
                    elif tcod.event.KeySym.a <= sym <= tcod.event.KeySym.z:
                        index = sym - tcod.event.KeySym.a
                        items = player.inventory.items
                        if index < len(items):
                            item = items[index]
                            if mode == MODE_USE:
                                result = inventory.use_item(player, item)
                            else:
                                result = inventory.drop_item(player, item, floor_items)
                            mode = MODE_PLAY
                            apply_result(result, player, game_map, monsters, message_log)


if __name__ == "__main__":
    main()
