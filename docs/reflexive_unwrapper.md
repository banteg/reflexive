# Reflexive Unwrapper

Generated from the extracted Reflexive Arcade corpus under `artifacts/extracted/archive_org_repack`.

## Methodology

- Static strategy: For wrapper roots that carry an encrypted child file (*.RWG, RAW_001.exe, or RAW_001.dat), derive the RAW_002 config seed from the wrapper-side dependency file sizes, decrypt RAW_002 statically, derive the child-payload seed from the encrypted RAW_002 header, and patch the decrypted entrypoint-to-section-end span back into the child PE on disk.
- Direct strategy: For helper and dll-only layouts where a non-wrapper game executable is already present at the top level, carry that executable forward and drop Reflexive wrapper artifacts.
- Output shape: Materialize wrapper-free trees under artifacts/unwrapped/archive_org_repack by removing ReflexiveArcade/ content, wrapper launcher copies, encrypted child blobs, RAW_002/RAW_003 wrapper sidecars, and wrapper-only top-level assets such as Background.jpg, button_*.jpg, and wraperr.log.
- Validation: The static decryptor matches the earlier runtime-captured outputs byte-for-byte on eight cross-family roots: 10 Days Under The Sea, A Pirates Legend, Diamond Drop, Emperors Mahjong, Home Sweet Home, Astrobatics, Ice Cream Tycoon, and Alpha Ball/bin.

## Summary

- Effective wrapper roots scanned: 1083
- `direct` roots: 46
- `static` roots: 1011
- `unsupported` roots: 26
- Static child types:
  - `raw_001_dat`: 3
  - `raw_001_exe`: 46
  - `rwg`: 962

## Layout Strategy Counts

| Layout | Strategy | Roots | Example |
| --- | --- | ---: | --- |
| `dll_only_with_application_dat` | `direct` | 26 | `Reflexive Arcade A/Air Strike 2` |
| `dll_only_with_application_dat` | `unsupported` | 22 | `Reflexive Arcade B/Bud Redhead` |
| `helper_exe_with_application_dat` | `direct` | 20 | `Reflexive Arcade E/Double Trump/Electric` |
| `other` | `static` | 5 | `Reflexive Arcade D/Diamond Drop` |
| `other` | `unsupported` | 4 | `Reflexive Arcade C/Cash Cow/bin` |
| `wrapped_raw001_with_config` | `static` | 46 | `Reflexive Arcade A/A Pirates Legend` |
| `wrapped_rwg_with_config` | `static` | 952 | `Reflexive Arcade 0-9/10 Days Under The Sea` |
| `wrapped_rwg_without_raw_002` | `static` | 8 | `Reflexive Arcade A/Alpha Ball/bin` |

## Validated Examples

| Root | Strategy | Child Type | Output Executable |
| --- | --- | --- | --- |
| `Reflexive Arcade 0-9/10 Days Under The Sea` | `static` | `rwg` | `10DaysUnderTheSea.exe` |
| `Reflexive Arcade A/A Pirates Legend` | `static` | `raw_001_exe` | `APiratesLegend.exe` |
| `Reflexive Arcade D/Diamond Drop` | `static` | `raw_001_dat` | `DiamondDrop.exe` |
| `Reflexive Arcade E/Emperors Mahjong` | `static` | `rwg` | `Mahjong.exe` |
| `Reflexive Arcade E/Double Trump/Electric` | `direct` | - | `Electric.exe` |
| `Reflexive Arcade C/Crimsonland` | `direct` | - | `crimsonland.exe` |

## Unsupported Roots

| Root | Layout | Primary Wrapper Role | Example Wrapper |
| --- | --- | --- | --- |
| `Reflexive Arcade B/Bud Redhead` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade B/Bud Redhead/BudRedhead.exe` |
| `Reflexive Arcade C/Cash Cow/bin` | `other` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade C/Cash Cow/bin/launcher.exe` |
| `Reflexive Arcade C/Colony` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade C/Colony/Colony.exe` |
| `Reflexive Arcade D/Digby's Donuts` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade D/Digby's Donuts/DigbysDonuts.exe` |
| `Reflexive Arcade D/Docker Sokoban` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade D/Docker Sokoban/docker.exe` |
| `Reflexive Arcade F/Five Card Deluxe` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade F/Five Card Deluxe/FiveCardDeluxe.exe` |
| `Reflexive Arcade F/Flip Words` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade F/Flip Words/FlipWords.exe` |
| `Reflexive Arcade H/Holiday Express` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade H/Holiday Express/HolidayExpress.exe` |
| `Reflexive Arcade I/Ice Breaker` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade I/Ice Breaker/ice_breaker.exe` |
| `Reflexive Arcade J/The Walls of Jericho` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade J/The Walls of Jericho/jericho.exe` |
| `Reflexive Arcade L/Live Billiards` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade L/Live Billiards/LiveBilliards.exe` |
| `Reflexive Arcade L/Lucky Streak Poker` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade L/Lucky Streak Poker/LuckyStreakPoker.exe` |
| `Reflexive Arcade M/Magic Ball` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade M/Magic Ball/MagicBall.exe` |
| `Reflexive Arcade M/MaxGammon` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade M/MaxGammon/maxgammon.exe` |
| `Reflexive Arcade O/Orbz` | `other` | `launcher_bak` | `artifacts/extracted/archive_org_repack/Reflexive Arcade O/Orbz/orbz.exe.BAK` |
| `Reflexive Arcade P/PacQuest 3D` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade P/PacQuest 3D/PacQuest.exe` |
| `Reflexive Arcade P/Puzzle Express` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade P/Puzzle Express/PuzzleExpress.exe` |
| `Reflexive Arcade R/Ricochet Lost Worlds` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade R/Ricochet Lost Worlds/Ricochet.exe` |
| `Reflexive Arcade S/Sea War The Battles 2` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade S/Sea War The Battles 2/SeaWar.exe` |
| `Reflexive Arcade S/Secret Chamber` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade S/Secret Chamber/chamber.exe` |
| `Reflexive Arcade S/Snowy The Bears Adventure` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade S/Snowy The Bears Adventure/Snowy.exe` |
| `Reflexive Arcade S/Solitaire 2` | `other` | `launcher_bak` | `artifacts/extracted/archive_org_repack/Reflexive Arcade S/Solitaire 2/solitaire2.exe.BAK` |
| `Reflexive Arcade S/Sportball Challenge` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade S/Sportball Challenge/Sportball.exe` |
| `Reflexive Arcade T/Think Tanks` | `other` | `launcher_bak` | `artifacts/extracted/archive_org_repack/Reflexive Arcade T/Think Tanks/ThinkTanks.exe.BAK` |
| `Reflexive Arcade T/Trivia Machine` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade T/Trivia Machine/TriviaMachine.exe` |
| `Reflexive Arcade W/Wild West Wendy` | `dll_only_with_application_dat` | `top_level_exe` | `artifacts/extracted/archive_org_repack/Reflexive Arcade W/Wild West Wendy/www.exe` |

