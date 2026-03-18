# RuTracker Game Engine Probe

- Scanned unwrapped roots under `artifacts/unwrapped/rutracker`.
- JSON report: `docs/generated/rutracker/game_engines.json`.
- Roots scanned: 1660
- Confident primary engine assignments: 257 (15.5%)
- Unclassified roots after this static pass: 1403
- Roots matching more than one engine family before precedence: 3

This pass only counts engine families with direct static evidence. Runtime and audio middleware are reported separately and are not treated as engine assignments.

## Confirmed Engine Families

| Engine | Roots | Share | Evidence Basis | Example Roots |
| --- | ---: | ---: | --- | --- |
| Ren'Py | 1 | 0.1% | `renpy/` runtime tree and launcher scripts mentioning `Ren'Py`. | `Science Girls` |
| Unity | 1 | 0.1% | `UnityEngine.dll`, `sharedassets*.assets`, and Unity data files. | `Mr Jones Graveyard Shift` |
| Telltale Tool | 10 | 0.6% | `.ttarch`/`.ttarch2` archives and embedded `Telltale` strings. | `Talesof Monkey Island Chapter 1`, `Talesof Monkey Island Chapter 2`, `Talesof Monkey Island Chapter 3`, `Talesof Monkey Island Chapter 4` |
| Wintermute Engine | 4 | 0.2% | `data.dcp`/`packages.dcp` bundles with `Wintermute Engine` strings. | `East Side Story`, `Ghostinthe Sheet`, `Hamlet`, `The Colorof Murder` |
| RPG Maker XP / RGSS | 9 | 0.5% | `RGSS102*.dll` runtimes and `*.rgssad` archives. | `3 Starsof Destiny`, `Aveyond`, `Aveyond 2`, `Aveyond Gatesof Night` |
| Torque Game Engine | 53 | 3.2% | `main.cs` scripts whose header names `Torque Game Engine` / `GarageGames`. | `Aqua Park`, `ArchMage`, `Be A King`, `Bricktopia` |
| OGRE | 6 | 0.4% | `OgreMain.dll` plus OGRE renderer / plugin DLLs. | `Deep Quest`, `Iron Roses`, `Magic Tea`, `Marblez` |
| Irrlicht | 2 | 0.1% | `Irrlicht.dll` and the bundled `License/irrlicht.txt` notice. | `Amulet Of Tricolor`, `Harvest Massive Encounter` |
| PopCap / SexyApp Framework | 126 | 7.6% | `main.pak` and/or `SexyApp` / `PopCap Framework` markers. | `1912 Titanic Mystery`, `Age Of Emerald`, `Alex Gordon`, `Angkor` |
| Haaf's Game Engine (HGE) | 45 | 2.7% | `hge.dll` or `Haaf's Game Engine` / `[HGESTRINGTABLE]` markers. | `1 Penguin 100 Cases`, `Aerial MahJong`, `Alien Outbreak 2 Invasion`, `Amazonia` |

## Common Runtime / Middleware Tags

| Runtime | Roots | Share | Example Roots |
| --- | ---: | ---: | --- |
| BASS | 425 | 25.6% | `1 Penguin 100 Cases`, `10 Days Under The Sea`, `10 Talismans`, `1912 Titanic Mystery` |
| OpenAL | 124 | 7.5% | `Alices Magical Mahjong`, `Alien Abduction`, `Alien Defense`, `Ancient Quest Of Saqqarah` |
| SDL | 96 | 5.8% | `Action Memory`, `Alien Defense`, `Archibalds Adventures`, `Azada` |
| FMOD | 91 | 5.5% | `Adventuresof Robinson Crusoe`, `African War`, `Agatha Christie Peril At End House`, `Alice Greenfingers` |
| FMOD Ex | 50 | 3.0% | `Astariel`, `Big Shot`, `CLUE Classic`, `Discovery A Seek And Find Adventure` |

## Zero-Hit Marker Families

| Engine Family Marker | Roots |
| --- | ---: |
| Adventure Game Studio | 0 |
| Cocos2d-x | 0 |
| GameMaker | 0 |
| Godot | 0 |
| Unreal | 0 |
| XNA / MonoGame | 0 |
