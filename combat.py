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
    # Minimum-1 floor: armor reduces damage but never fully negates a hit, so
    # no amount of defense makes a combatant invulnerable.
    damage = max(1, attacker.power - defender.defense)
    defender.hp -= damage

    messages = [f"{attacker.name} hits {defender.name} for {damage} damage."]
    if not defender.is_alive:
        messages.append(f"{defender.name} dies!")

    return messages
