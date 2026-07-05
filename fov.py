"""Field of view — a thin wrapper around tcod.map.compute_fov.

Roguelike FOV: given the map's transparency grid and the viewer's position,
compute which tiles are currently visible. We keep the heavy lifting in tcod
(it ships several symmetric shadowcasting algorithms) and just plumb our
GameMap's arrays in and out.
"""
from __future__ import annotations

import tcod.map

from game_map import GameMap


def update_fov(game_map: GameMap, x: int, y: int, radius: int) -> None:
    """Recompute `visible` from the viewer at (x, y), then fold it into
    `explored` so seen tiles are remembered after they leave sight.

    pov is passed as (y, x): compute_fov indexes the array row-first, matching
    our tiles[y, x] convention.
    """
    game_map.visible[:] = tcod.map.compute_fov(
        game_map.transparent,
        pov=(y, x),
        radius=radius,
    )
    # `explored` only ever grows: once seen, a tile stays remembered.
    game_map.explored |= game_map.visible
