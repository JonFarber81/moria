"""Named dungeon levels.

Maps a numeric depth to a Moria region name and an arrival flavor line, loaded
from data/levels.json. Depths beyond the last defined level clamp to the
deepest entry (the Balrog's Throne) so the descent never runs out of names.
"""
from __future__ import annotations

import json
from pathlib import Path


def _load_levels() -> list[dict]:
    path = Path(__file__).parent / "data" / "levels.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


LEVELS: list[dict] = _load_levels()


def _entry(depth: int) -> dict:
    """The level record for a 1-based depth, clamped to the deepest defined."""
    index = min(max(depth, 1), len(LEVELS)) - 1
    return LEVELS[index]


def level_name(depth: int) -> str:
    return _entry(depth)["name"]


def level_arrival(depth: int) -> str:
    return _entry(depth)["arrival"]
