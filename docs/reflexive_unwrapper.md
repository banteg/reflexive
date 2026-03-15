# Reflexive Unwrapper

Generated from the extracted Reflexive Arcade corpus under `artifacts/extracted`.

## Methodology

- Runtime strategy: For wrapper roots that still carry an encrypted child file (*.RWG or RAW_001.exe), run the patched Reflexive launcher under a debugger, capture the child path from CreateProcessA, capture the decrypted write buffer from WriteProcessMemory, and patch that buffer back into the child PE on disk.
- Direct strategy: For helper and dll-only layouts where a non-wrapper game executable is already present at the top level, carry that executable forward and drop Reflexive wrapper artifacts.
- Output shape: Materialize wrapper-free trees under artifacts/unwrapped by removing ReflexiveArcade/ content, wrapper launcher copies, encrypted child blobs, and wrapper-only sidecar files such as wraperr.log.

## Summary

- Effective wrapper roots scanned: 1083
- `direct` roots: 46
- `runtime` roots: 1009
- `unsupported` roots: 28
- Runtime child types:
  - `raw_001`: 46
  - `rwg`: 963

## Layout Strategy Counts

| Layout | Strategy | Roots | Example |
| --- | --- | ---: | --- |
| `dll_only_with_application_dat` | `direct` | 26 | `Reflexive Arcade A/Air Strike 2` |
| `dll_only_with_application_dat` | `unsupported` | 22 | `Reflexive Arcade B/Bud Redhead` |
| `helper_exe_with_application_dat` | `direct` | 20 | `Reflexive Arcade E/Double Trump/Electric` |
| `other` | `runtime` | 3 | `Reflexive Arcade C/Cash Cow/bin` |
| `other` | `unsupported` | 6 | `Reflexive Arcade D/Diamond Drop` |
| `wrapped_raw001_with_config` | `runtime` | 46 | `Reflexive Arcade A/A Pirates Legend` |
| `wrapped_rwg_with_config` | `runtime` | 952 | `Reflexive Arcade 0-9/10 Days Under The Sea` |
| `wrapped_rwg_without_raw_002` | `runtime` | 8 | `Reflexive Arcade A/Alpha Ball/bin` |

## Validated Examples

| Root | Strategy | Child Type | Output Executable |
| --- | --- | --- | --- |
| `Reflexive Arcade 0-9/10 Days Under The Sea` | `runtime` | `rwg` | `10DaysUnderTheSea.exe` |
| `Reflexive Arcade A/A Pirates Legend` | `runtime` | `raw_001` | `APiratesLegend.exe` |
| `Reflexive Arcade E/Double Trump/Electric` | `direct` | - | `Electric.exe` |
| `Reflexive Arcade C/Crimsonland` | `direct` | - | `crimsonland.exe` |

## Unsupported Roots

| Root | Layout | Primary Wrapper Role | Example Wrapper |
| --- | --- | --- | --- |
| `Reflexive Arcade B/Bud Redhead` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade B/Bud Redhead/BudRedhead.exe` |
| `Reflexive Arcade C/Colony` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade C/Colony/Colony.exe` |
| `Reflexive Arcade D/Diamond Drop` | `other` | `launcher_bak` | `artifacts/extracted/Reflexive Arcade D/Diamond Drop/DiamondDrop.exe.BAK` |
| `Reflexive Arcade D/Digby's Donuts` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade D/Digby's Donuts/DigbysDonuts.exe` |
| `Reflexive Arcade D/Docker Sokoban` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade D/Docker Sokoban/docker.exe` |
| `Reflexive Arcade F/Five Card Deluxe` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade F/Five Card Deluxe/FiveCardDeluxe.exe` |
| `Reflexive Arcade F/Flip Words` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade F/Flip Words/FlipWords.exe` |
| `Reflexive Arcade H/Holiday Express` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade H/Holiday Express/HolidayExpress.exe` |
| `Reflexive Arcade I/Ice Breaker` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade I/Ice Breaker/ice_breaker.exe` |
| `Reflexive Arcade J/The Walls of Jericho` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade J/The Walls of Jericho/jericho.exe` |
| `Reflexive Arcade L/Live Billiards` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade L/Live Billiards/LiveBilliards.exe` |
| `Reflexive Arcade L/Lucky Streak Poker` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade L/Lucky Streak Poker/LuckyStreakPoker.exe` |
| `Reflexive Arcade M/Magic Ball` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade M/Magic Ball/MagicBall.exe` |
| `Reflexive Arcade M/MaxGammon` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade M/MaxGammon/maxgammon.exe` |
| `Reflexive Arcade O/Orbz` | `other` | `launcher_bak` | `artifacts/extracted/Reflexive Arcade O/Orbz/orbz.exe.BAK` |
| `Reflexive Arcade P/PacQuest 3D` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade P/PacQuest 3D/PacQuest.exe` |
| `Reflexive Arcade P/Puzzle Express` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade P/Puzzle Express/PuzzleExpress.exe` |
| `Reflexive Arcade R/Ricochet Lost Worlds` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade R/Ricochet Lost Worlds/Ricochet.exe` |
| `Reflexive Arcade S/Sea War The Battles 2` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade S/Sea War The Battles 2/SeaWar.exe` |
| `Reflexive Arcade S/Secret Chamber` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade S/Secret Chamber/chamber.exe` |
| `Reflexive Arcade S/Slot Words` | `other` | `launcher_bak` | `artifacts/extracted/Reflexive Arcade S/Slot Words/slotwords.exe.BAK` |
| `Reflexive Arcade S/Snowy The Bears Adventure` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade S/Snowy The Bears Adventure/Snowy.exe` |
| `Reflexive Arcade S/Solitaire 2` | `other` | `launcher_bak` | `artifacts/extracted/Reflexive Arcade S/Solitaire 2/solitaire2.exe.BAK` |
| `Reflexive Arcade S/Sportball Challenge` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade S/Sportball Challenge/Sportball.exe` |
| `Reflexive Arcade T/Think Tanks` | `other` | `launcher_bak` | `artifacts/extracted/Reflexive Arcade T/Think Tanks/ThinkTanks.exe.BAK` |
| `Reflexive Arcade T/Trivia Machine` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade T/Trivia Machine/TriviaMachine.exe` |
| `Reflexive Arcade W/Wild West Wendy` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/Reflexive Arcade W/Wild West Wendy/www.exe` |
| `Reflexive Arcade W/Word Wizard Deluxe` | `other` | `launcher_bak` | `artifacts/extracted/Reflexive Arcade W/Word Wizard Deluxe/Word Wizard.exe.BAK` |

