"""Inventory, equipment, and the item actions (pick up / use / equip / drop).

Two small state-holding components live on the Player:
  * Inventory — items the dwarf is carrying but not wearing.
  * Equipment — the weapon and armor currently worn; its bonuses feed into the
    Entity.power / Entity.defense properties.

Equipped items are removed from the Inventory and held in the slot, so the
inventory list only ever shows loose gear you can act on.

Every action returns (messages, took_turn): the message lines to log, and
whether a game turn was actually spent (so the caller knows whether monsters
get to act). This mirrors the None-vs-move convention used for movement.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities import Entity, Item

TurnResult = tuple[list[str], bool]


class Inventory:
    """Fixed-capacity bag of carried (not worn) items."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.items: list[Item] = []

    @property
    def is_full(self) -> bool:
        return len(self.items) >= self.capacity


class Equipment:
    """The worn weapon and armor. Bonuses here are what turn base stats into
    effective stats via Entity.power / Entity.defense."""

    def __init__(self) -> None:
        self.weapon: Item | None = None
        self.armor: Item | None = None

    @property
    def power_bonus(self) -> int:
        return self.weapon.power_bonus if self.weapon else 0

    @property
    def defense_bonus(self) -> int:
        return self.armor.defense_bonus if self.armor else 0

    def slot_of(self, item: Item) -> str:
        """Which slot an item goes in, derived from its kind."""
        return "weapon" if item.kind == "weapon" else "armor"


def pick_up(player: Entity, floor_items: list[Item]) -> TurnResult:
    """Pick up the first item on the player's tile, if any."""
    for item in floor_items:
        if item.x == player.x and item.y == player.y:
            if player.inventory.is_full:
                return ([f"Your pack is full; you can't lift the {item.name}."], False)
            floor_items.remove(item)
            player.inventory.items.append(item)
            return ([f"You pick up the {item.name}."], True)
    return (["There is nothing here to pick up."], False)


def use_item(player: Entity, item: Item) -> TurnResult:
    """Dispatch on the item's kind: quaff a potion, or equip gear."""
    if item.kind == "potion":
        return _quaff(player, item)
    if item.kind in ("weapon", "armor"):
        return _equip(player, item)
    return ([f"You can't use the {item.name}."], False)


def drop_item(player: Entity, item: Item, floor_items: list[Item]) -> TurnResult:
    """Drop a carried item onto the player's tile."""
    player.inventory.items.remove(item)
    item.x, item.y = player.x, player.y
    floor_items.append(item)
    return ([f"You drop the {item.name}."], True)


def _equip(player: Entity, item: Item) -> TurnResult:
    """Move `item` from inventory into its slot. Any gear already in that slot
    goes back into the pack (a swap), so no item is ever lost."""
    slot = player.equipment.slot_of(item)
    current = getattr(player.equipment, slot)

    player.inventory.items.remove(item)
    if current is not None:
        player.inventory.items.append(current)
    setattr(player.equipment, slot, item)

    if current is not None:
        return ([f"You equip the {item.name}, stowing the {current.name}."], True)
    return ([f"You equip the {item.name}."], True)


def _quaff(player: Entity, potion: Item) -> TurnResult:
    """Drink a healing potion.

    Design choice worth tweaking: quaffing at full health is refused rather
    than wasting the potion (and costs no turn). Heal is clamped so you never
    exceed max_hp — 'overheal' is lost, not banked.
    """
    if player.hp >= player.max_hp:
        return (["You are already at full health."], False)

    healed = min(potion.heal, player.max_hp - player.hp)
    player.hp += healed
    player.inventory.items.remove(potion)
    return ([f"You quaff the {potion.name} and recover {healed} HP."], True)
