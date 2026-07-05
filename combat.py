"""Melee combat resolution.

Kept separate from entities and the main loop so the *rule* for how an attack
plays out lives in exactly one place. Returns human-readable message strings
rather than printing, so the caller decides where they go (stdout now, an
in-game message log later).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities import Entity


def resolve_attack(attacker: Entity, defender: Entity) -> list[str]:
    """Apply one melee strike from attacker to defender.

    Damage is a flat power-minus-defense, floored at zero. Mutates the
    defender's hp; the caller is responsible for removing it if it dies
    (checked via `defender.is_alive`).
    """
    damage = max(0, attacker.power - defender.defense)
    messages: list[str] = []

    if damage > 0:
        defender.hp -= damage
        messages.append(f"{attacker.name} hits {defender.name} for {damage} damage.")
    else:
        messages.append(f"{attacker.name} hits {defender.name}, but it does no damage.")

    if not defender.is_alive:
        messages.append(f"{defender.name} dies!")

    return messages
