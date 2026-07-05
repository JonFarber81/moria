# Moria Lore Notes

Background/world reference for the roguelike, mined from the official tabletop sourcebook ***The One Ring 2e — Moria: Through the Doors of Durin*** (Free League, 2024). These are **notes for a later content pass** — naming, flavor, and world background. They are *not* a directive to build Shadow/corruption, narrative, or any deferred system now (see `../CLAUDE.md`).

Tabletop mechanics (dice, target numbers, stat blocks) were deliberately excluded; only lore, names, descriptions, and atmosphere were kept.

> The source PDF lives in `../source/` (gitignored — copyrighted, not for distribution). These notes are original summaries written for this project's use.

## Files

| File | What's in it | Use it for |
|---|---|---|
| [history-and-timeline.md](history-and-timeline.md) | Names of Moria, the vertical Levels/Deeps structure, key persons, the full Tale of Years, and why a lone dwarf descends (~2965) | Backstory, dwarven naming, the depth system |
| [monsters.md](monsters.md) | Full bestiary — Orc factions (Moria / Udûn / Mordor), Dwarven slaves & haunts, the Balrog, Ash-wraiths, Cave Bats, Marrow-eaters, Stone Toads, Tappers, Cave Dogs | Populating `data/monsters.json` with named, themed foes + descriptions |
| [areas.md](areas.md) | Depth-ordered gazetteer of every named location, surface → Balrog's Throne, with a suggested dungeon-depth ladder | **Naming/theming dungeon levels** as the player descends |
| [items-and-treasure.md](items-and-treasure.md) | Balin's expedition backstory, the mithril tiers, named artifacts (Durin's Axe, the Last Ring, Ring of Keys, toadstone…), vault names | A themed loot table and precious-item tiers |
| [atmosphere-and-flavor.md](atmosphere-and-flavor.md) | Themes of Wonder / Sorrow & Fear, ambient portents, the Balrog-approach escalation, chamber types, and a bank of drop-in message lines | Message-log flavor, ambient events, procedural room theming |

## How this maps onto the current game

- **Depth ladder** (`areas.md`) → name each generated level after a real region, roughly: Dimrill Dale / East-gate → Old Moria → the Dwarrowdelf → the Deeps → the Mines / Balrog's Throne. The `Depth: N` HUD counter is the natural hook.
- **Monsters** (`monsters.md`) → the current lone "Orc" can become **Orc of Moria**, with **Orc of Udûn** (fire-cult), **Cave Bat**, **Stone Toad**, **Marrow-eater**, etc. added as data rows at deeper levels; the **Balrog** as a climax boss.
- **Items** (`items-and-treasure.md`) → weapon/armor/potion tiers gain names and lore; a **mithril** tier fits "precious but weightless"; **toadstone** is a natural potion/heal drop.
- **Flavor** (`atmosphere-and-flavor.md`) → the ready-made message lines can seed the message log on descent, on entering a region, or as ambient dread events.

*All of the above is deferred content — capture now, build when we start the content pass.*
