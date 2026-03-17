# Reflexive Wrapper Versions

Generated from wrapper roots discovered under `artifacts/extracted/archive`.

## Methodology

- A binary is treated as Reflexive wrapper code if it contains any of: ReflexiveArcade DLL Signature, radll_GetDLLVersionAsInt, radll_Initialize, or the standard ReflexiveArcade.dll load-error string.
- Build numbers are only accepted from standalone null-terminated ASCII strings of the form 'Build NNN'.
- DLL major versions are assigned by matching ReflexiveArcade.dll .text/.data section hashes to the four families whose radll_GetDLLVersionAsInt exports were verified in Binja.

## Summary

- Wrapper roots scanned: 1084
- Primary wrapper binaries with a literal `Build NNN` string: 1012
- Primary wrapper binaries without a literal build string: 50
- Roots with no preserved wrapper entry binary: 22

## DLL API Major Versions

| DLL Major | Roots |
| --- | ---: |
| `3` | 1 |
| `5` | 1083 |

## Primary Wrapper Entry Binaries

| Role | Literal Build | Roots |
| --- | --- | ---: |
| `launcher_bak` | `no` | 3 |
| `launcher_bak` | `yes` | 1009 |
| `none` | `no` | 22 |
| `support_exe` | `no` | 20 |
| `top_level_exe` | `no` | 27 |
| `top_level_exe` | `yes` | 3 |

## Wrapper Build Histogram

| Build | Roots | Roles | Example |
| --- | ---: | --- | --- |
| `122` | 1 | `launcher_bak` | `Reflexive Arcade S/Slot Words` |
| `123` | 2 | `launcher_bak` | `Reflexive Arcade D/Diamond Drop` |
| `124` | 2 | `launcher_bak` | `Reflexive Arcade E/Emperors Mahjong` |
| `128` | 1 | `launcher_bak` | `Reflexive Arcade P/Pharaoh's Curse Gold` |
| `131` | 1 | `launcher_bak` | `Reflexive Arcade W/Word Craft` |
| `142` | 1 | `launcher_bak` | `Reflexive Arcade M/Mind Your Marbles Christmas Edition` |
| `143` | 2 | `launcher_bak` | `Reflexive Arcade T/Traffic Jam Extreme` |
| `145` | 1 | `launcher_bak` | `Reflexive Arcade A/Alpha Ball/bin` |
| `156` | 1 | `launcher_bak` | `Reflexive Arcade A/Astrobatics` |
| `167` | 1 | `launcher_bak` | `Reflexive Arcade I/Ice Cream Tycoon` |
| `172` | 3 | `launcher_bak` | `Reflexive Arcade H/Home Sweet Home` |
| `173` | 996 | `launcher_bak`, `top_level_exe` | `Reflexive Arcade 0-9/10 Days Under The Sea` |

## Top-Level EXE Roots With Build Strings

| Root | Primary Wrapper | Build |
| --- | --- | --- |
| `Reflexive Arcade C/Cash Cow/bin` | `artifacts/extracted/archive/Reflexive Arcade C/Cash Cow/bin/launcher.exe` | `173` |
| `Reflexive Arcade E/Escape The Museum` | `artifacts/extracted/archive/Reflexive Arcade E/Escape The Museum/Museum.exe` | `173` |
| `Reflexive Arcade Z/ZoomBook The Temple Of The Sun` | `artifacts/extracted/archive/Reflexive Arcade Z/ZoomBook The Temple Of The Sun/zoombook.exe` | `173` |

## Buildless Wrapper Binaries

| Root | Primary Wrapper Role | Primary Wrapper |
| --- | --- | --- |
| `Reflexive Arcade A/Alien Sky` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade A/Alien Sky/AlienSky.exe` |
| `Reflexive Arcade A/Atomaders` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade A/Atomaders/Atomaders.exe` |
| `Reflexive Arcade B/Bud Redhead` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade B/Bud Redhead/BudRedhead.exe` |
| `Reflexive Arcade B/Bugatron` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade B/Bugatron/Bug3D.exe` |
| `Reflexive Arcade C/Colony` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade C/Colony/Colony.exe` |
| `Reflexive Arcade D/Digby's Donuts` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade D/Digby's Donuts/DigbysDonuts.exe` |
| `Reflexive Arcade D/Docker Sokoban` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade D/Docker Sokoban/docker.exe` |
| `Reflexive Arcade E/Double Trump/Electric` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade E/Double Trump/Electric/ReflexiveArcade.exe` |
| `Reflexive Arcade E/Playtonium Jigsaw Enchanted Forest` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade E/Playtonium Jigsaw Enchanted Forest/ReflexiveArcade.exe` |
| `Reflexive Arcade F/Five Card Deluxe` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade F/Five Card Deluxe/FiveCardDeluxe.exe` |
| `Reflexive Arcade F/Flip Wit!` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade F/Flip Wit!/ReflexiveArcade.exe` |
| `Reflexive Arcade F/Flip Words` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade F/Flip Words/FlipWords.exe` |
| `Reflexive Arcade F/Fusion` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade F/Fusion/ReflexiveArcade.exe` |
| `Reflexive Arcade G/Garfield Goes to Pieces` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade G/Garfield Goes to Pieces/ReflexiveArcade.exe` |
| `Reflexive Arcade G/Global Defense Network` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade G/Global Defense Network/GDN_Client.exe` |
| `Reflexive Arcade G/Gold Miner` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade G/Gold Miner/ReflexiveArcade.exe` |
| `Reflexive Arcade G/Grump` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade G/Grump/ReflexiveArcade.exe` |
| `Reflexive Arcade H/HangStan` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade H/HangStan/ReflexiveArcade.exe` |
| `Reflexive Arcade H/Hangman Wild West 2` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade H/Hangman Wild West 2/ReflexiveArcade.exe` |
| `Reflexive Arcade H/Holiday Express` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade H/Holiday Express/HolidayExpress.exe` |
| `Reflexive Arcade I/Ice Breaker` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade I/Ice Breaker/ice_breaker.exe` |
| `Reflexive Arcade J/Jigsaw365` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade J/Jigsaw365/ReflexiveArcade.exe` |
| `Reflexive Arcade J/The Walls of Jericho` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade J/The Walls of Jericho/jericho.exe` |
| `Reflexive Arcade L/Live Billiards` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade L/Live Billiards/LiveBilliards.exe` |
| `Reflexive Arcade L/Lucky Streak Poker` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade L/Lucky Streak Poker/LuckyStreakPoker.exe` |
| `Reflexive Arcade M/Magic Ball` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade M/Magic Ball/MagicBall.exe` |
| `Reflexive Arcade M/Mahjong Towers II` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade M/Mahjong Towers II/ReflexiveArcade.exe` |
| `Reflexive Arcade M/MaxGammon` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade M/MaxGammon/maxgammon.exe` |
| `Reflexive Arcade O/Orbz` | `launcher_bak` | `artifacts/extracted/archive/Reflexive Arcade O/Orbz/orbz.exe.BAK` |
| `Reflexive Arcade P/PacQuest 3D` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade P/PacQuest 3D/PacQuest.exe` |
| `Reflexive Arcade P/Pat Sajak's Lucky Letters` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade P/Pat Sajak's Lucky Letters/ReflexiveArcade.exe` |
| `Reflexive Arcade P/Puzzle Express` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade P/Puzzle Express/PuzzleExpress.exe` |
| `Reflexive Arcade P/Puzzle Myth` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade P/Puzzle Myth/ReflexiveArcade.exe` |
| `Reflexive Arcade R/Ricochet Lost Worlds` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade R/Ricochet Lost Worlds/Ricochet.exe` |
| `Reflexive Arcade S/Chomp! Chomp! Safari` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade S/Chomp! Chomp! Safari/ReflexiveArcade.exe` |
| `Reflexive Arcade S/Sea War The Battles 2` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade S/Sea War The Battles 2/SeaWar.exe` |
| `Reflexive Arcade S/Secret Chamber` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade S/Secret Chamber/chamber.exe` |
| `Reflexive Arcade S/Snowy The Bears Adventure` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade S/Snowy The Bears Adventure/Snowy.exe` |
| `Reflexive Arcade S/Solitaire 2` | `launcher_bak` | `artifacts/extracted/archive/Reflexive Arcade S/Solitaire 2/solitaire2.exe.BAK` |
| `Reflexive Arcade S/Speed` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade S/Speed/ReflexiveArcade.exe` |
| `Reflexive Arcade S/Sportball Challenge` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade S/Sportball Challenge/Sportball.exe` |
| `Reflexive Arcade T/Tablut` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade T/Tablut/ReflexiveArcade.exe` |
| `Reflexive Arcade T/Think Tanks` | `launcher_bak` | `artifacts/extracted/archive/Reflexive Arcade T/Think Tanks/ThinkTanks.exe.BAK` |
| `Reflexive Arcade T/Triptych` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade T/Triptych/triptych.exe` |
| `Reflexive Arcade T/Trivia Machine` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade T/Trivia Machine/TriviaMachine.exe` |
| `Reflexive Arcade T/Truffle Tray` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade T/Truffle Tray/ReflexiveArcade.exe` |
| `Reflexive Arcade V/Void War` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade V/Void War/ReflexiveArcade.exe` |
| `Reflexive Arcade W/Wild West Wendy` | `top_level_exe` | `artifacts/extracted/archive/Reflexive Arcade W/Wild West Wendy/www.exe` |
| `Reflexive Arcade W/Wonderland` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade W/Wonderland/ReflexiveArcade.exe` |
| `Reflexive Arcade W/Word Blitz Deluxe` | `support_exe` | `artifacts/extracted/archive/Reflexive Arcade W/Word Blitz Deluxe/ReflexiveArcade.exe` |

## Roots Without Preserved Wrapper Entry Binary

| Root | Layout |
| --- | --- |
| `Reflexive Arcade A/Air Strike 2` | `dll_only_with_application_dat` |
| `Reflexive Arcade A/Alpha Ball` | `dll_only_with_application_dat` |
| `Reflexive Arcade A/Aqua Bubble` | `dll_only_with_application_dat` |
| `Reflexive Arcade A/Aqua Bubble 2` | `dll_only_with_application_dat` |
| `Reflexive Arcade A/Aqua Words` | `dll_only_with_application_dat` |
| `Reflexive Arcade B/Beeline` | `dll_only_with_application_dat` |
| `Reflexive Arcade B/Blox World` | `dll_only_with_application_dat` |
| `Reflexive Arcade B/Boulder Dash` | `dll_only_with_application_dat` |
| `Reflexive Arcade C/Crimsonland` | `dll_only_with_application_dat` |
| `Reflexive Arcade C/Super Collapse` | `dll_only_with_application_dat` |
| `Reflexive Arcade C/Super Collapse II` | `dll_only_with_application_dat` |
| `Reflexive Arcade F/Fatman Adventures` | `dll_only_with_application_dat` |
| `Reflexive Arcade F/Feed The Snake` | `dll_only_with_application_dat` |
| `Reflexive Arcade G/Gold Sprinter` | `dll_only_with_application_dat` |
| `Reflexive Arcade G/Super Glinx` | `dll_only_with_application_dat` |
| `Reflexive Arcade I/Ice Age` | `dll_only_with_application_dat` |
| `Reflexive Arcade M/Mad Cars` | `dll_only_with_application_dat` |
| `Reflexive Arcade M/Super Mahjong` | `dll_only_with_application_dat` |
| `Reflexive Arcade P/Puzzle Word` | `dll_only_with_application_dat` |
| `Reflexive Arcade R/Ricochet Lost Worlds Recharged` | `dll_only_with_application_dat` |
| `Reflexive Arcade S/Solitaire` | `dll_only_with_application_dat` |
| `Reflexive Arcade T/Super Text Twist` | `dll_only_with_application_dat` |

## Mixed Layout Notes

| Root | Notes |
| --- | --- |
| `Reflexive Arcade T/Tablut` | `support_exe_is_wrapper_entrypoint`, `launcher_bak_is_not_wrapper_binary` |

