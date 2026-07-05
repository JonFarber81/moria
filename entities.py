"""Things that live on the map and occupy a tile: the Player and Monsters.

Combat stats live on Entity now that Step 4 exists. Monster stats are NOT
hardcoded here — they're loaded from data/monsters.json and stamped onto
Monster instances, so adding a creature is a data change, not a code change.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import tcod.path

import combat
import config
from inventory import Equipment, Inventory

if TYPE_CHECKING:
    from game_map import GameMap


class Entity:
    """Anything drawn at an (x, y) position with a glyph, color, and (now)
    combat stats. Non-combatants simply leave the stats at zero."""

    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: tuple[int, int, int],
        name: str,
        max_hp: int = 0,
        power: int = 0,
        defense: int = 0,
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        # Base combat stats; effective power/defense (below) add equipment.
        self.base_power = power
        self.base_defense = defense
        # Only the Player wears gear; monsters leave this None (no bonus).
        self.equipment: Equipment | None = None

    @property
    def power(self) -> int:
        """Effective attack: base plus any equipped weapon bonus."""
        bonus = self.equipment.power_bonus if self.equipment else 0
        return self.base_power + bonus

    @property
    def defense(self) -> int:
        """Effective defense: base plus any equipped armor bonus."""
        bonus = self.equipment.defense_bonus if self.equipment else 0
        return self.base_defense + bonus

    @property
    def is_alive(self) -> bool:
        """Dead things have run out of hp. Things with no max_hp (items,
        decorations) are never 'alive' in the combat sense."""
        return self.hp > 0

    def move(self, dx: int, dy: int) -> None:
        """Shift position by a delta. Callers check legality first."""
        self.x += dx
        self.y += dy

    def distance_to(self, other: Entity) -> int:
        """Chebyshev distance in tiles — 1 means orthogonally or diagonally
        adjacent, i.e. within melee reach."""
        return max(abs(other.x - self.x), abs(other.y - self.y))


class Player(Entity):
    """The dwarf the human controls."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__(
            x=x,
            y=y,
            char=config.CHAR_PLAYER,
            color=config.COLOR_PLAYER,
            name="Dwarf",
            max_hp=30,
            power=3,   # unarmed is weak; a weapon is a real upgrade
            defense=1,  # base toughness; armor stacks meaningfully on top
        )
        self.inventory = Inventory(config.INVENTORY_CAPACITY)
        self.equipment = Equipment()


class Monster(Entity):
    """A hostile creature. Chases the player when it can see them and strikes
    when adjacent. Built from a data/monsters.json entry via `spawn`."""

    def take_turn(
        self, target: Entity, game_map: GameMap, monsters: list[Monster]
    ) -> list[str]:
        """Act for one turn against `target` (the player).

        Only acts while in the player's field of view — off-screen monsters
        idle, which keeps the dungeon quiet and pathfinding cheap. When
        adjacent it attacks; otherwise it steps one tile along the shortest
        path toward the player.
        """
        if not game_map.visible[self.y, self.x]:
            return []  # can't see the dwarf's torchlight; stay put

        if self.distance_to(target) <= 1:
            return combat.resolve_attack(self, target)

        path = self._path_to(target.x, target.y, game_map, monsters)
        if path:
            next_x, next_y = path[0]
            self.x, self.y = next_x, next_y
        return []

    def _path_to(
        self, dest_x: int, dest_y: int, game_map: GameMap, monsters: list[Monster]
    ) -> list[tuple[int, int]]:
        """Shortest 4-directional path to (dest_x, dest_y) as a list of
        (x, y) steps, excluding the monster's own tile. Empty if unreachable.

        Uses tcod's pathfinder over a cost grid: walkable tiles cost 1, walls
        are impassable (cost 0), and tiles occupied by *other* living monsters
        get a high cost so orcs route around each other instead of stacking.
        """
        cost = np.where(game_map.tiles == 1, 1, 0).astype(np.int8)  # 1 == FLOOR

        for other in monsters:
            if other is not self and other.is_alive and cost[other.y, other.x]:
                cost[other.y, other.x] += 10  # passable but strongly avoided

        # cardinal=1, diagonal=0 -> orthogonal movement, matching the player.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=1, diagonal=0)
        pathfinder = tcod.path.Pathfinder(graph)
        pathfinder.add_root((self.y, self.x))  # (y, x) index order

        # path_to includes the start; drop it and convert (y, x) -> (x, y).
        path = pathfinder.path_to((dest_y, dest_x))[1:].tolist()
        return [(x, y) for (y, x) in path]

    @classmethod
    def spawn(cls, type_key: str, x: int, y: int) -> Monster:
        """Build a monster of the given type from loaded JSON data."""
        data = MONSTER_TYPES[type_key]
        return cls(
            x=x,
            y=y,
            char=data["char"],
            color=tuple(data["color"]),
            name=data["name"],
            max_hp=data["max_hp"],
            power=data["power"],
            defense=data["defense"],
        )


class Item(Entity):
    """A pickup lying on the floor or carried in a pack. Not a combatant, so
    it leaves the hp/power/defense stats at zero; its useful numbers are the
    kind-specific bonuses below, loaded from data/items.json."""

    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: tuple[int, int, int],
        name: str,
        kind: str,
        power_bonus: int = 0,
        defense_bonus: int = 0,
        heal: int = 0,
    ) -> None:
        super().__init__(x=x, y=y, char=char, color=color, name=name)
        self.kind = kind  # "weapon" | "armor" | "potion"
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.heal = heal

    @classmethod
    def spawn(cls, type_key: str, x: int, y: int) -> Item:
        """Build an item of the given type from loaded JSON data. Missing
        numeric fields default to 0, so a potion needs no power_bonus etc."""
        data = ITEM_TYPES[type_key]
        return cls(
            x=x,
            y=y,
            char=data["char"],
            color=tuple(data["color"]),
            name=data["name"],
            kind=data["kind"],
            power_bonus=data.get("power_bonus", 0),
            defense_bonus=data.get("defense_bonus", 0),
            heal=data.get("heal", 0),
        )


def _load_data(filename: str) -> dict[str, dict]:
    """Read a JSON definition file from data/ once, at import time."""
    path = Path(__file__).parent / "data" / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


MONSTER_TYPES: dict[str, dict] = _load_data("monsters.json")
ITEM_TYPES: dict[str, dict] = _load_data("items.json")


def blocking_monster_at(monsters: list[Monster], x: int, y: int) -> Monster | None:
    """Return the living monster standing on (x, y), if any. Used to turn a
    move into a bump-attack."""
    for monster in monsters:
        if monster.is_alive and monster.x == x and monster.y == y:
            return monster
    return None
