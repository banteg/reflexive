# RuTracker Probe

- Source id: `rutracker`
- Source root: `artifacts/sources/rutracker`
- Torrent manifest: `artifacts/rutracker-3687027.torrent`
- Archive comparison root: `artifacts/extracted/archive`
- Archive unwrapper sweep: `docs/generated/archive/unwrapper_sweep.json`
- Archive wrapper version scan: `docs/generated/archive/wrapper_versions.json`

## Live Source Status

- Live rutracker source is readable.
- Installer stubs scanned: 1696
- Stubs with explicit Reflexive markers: 1696

### Installer Technology Summary

| Technology | Count |
| --- | ---: |
| `Inno Setup signature` | 1696 |

### Sample Extraction Results

| Installer | Inno markers | `innoextract -i` | `7z l` |
| --- | --- | --- | --- |
| `10DaysUnderTheSeaSetup.exe` | `Inno Setup Setup Data (5.2.3)`@216972, `Inno Setup Messages (5.1.11)`@217036, `CHANNEL_NAME=Reflexive`@36320821 | `Done with 1 error. \| Not a supported Inno Setup installer!` | `7-Zip [64] 17.05 : Copyright (c) 1999-2021 Igor Pavlov : 2017-08-28 \| p7zip Version 17.05 (locale=utf8,Utf16=on,HugeFiles=on,64 bits,10 CPUs LE) \| Scanning the drive for archives: \| 1 file, 36341341 bytes (35 MiB)` |
| `AlienShooterSetup.exe` | `Inno Setup Setup Data (5.2.3)`@216972, `Inno Setup Messages (5.1.11)`@217036, `CHANNEL_NAME=Reflexive`@21765111 | `Done with 1 error. \| Not a supported Inno Setup installer!` | `7-Zip [64] 17.05 : Copyright (c) 1999-2021 Igor Pavlov : 2017-08-28 \| p7zip Version 17.05 (locale=utf8,Utf16=on,HugeFiles=on,64 bits,10 CPUs LE) \| Scanning the drive for archives: \| 1 file, 21785626 bytes (21 MiB)` |
| `BudRedheadSetup.exe` | `Inno Setup Setup Data (5.2.3)`@216972, `Inno Setup Messages (5.1.11)`@217036, `CHANNEL_NAME=Reflexive`@7663567 | `Done with 1 error. \| Not a supported Inno Setup installer!` | `tail zip only (files=?, warnings=1)` |
| `DigbysDonutsSetup.exe` | `Inno Setup Setup Data (5.2.3)`@216972, `Inno Setup Messages (5.1.11)`@217036, `CHANNEL_NAME=Reflexive`@8718033 | `Done with 1 error. \| Not a supported Inno Setup installer!` | `7-Zip [64] 17.05 : Copyright (c) 1999-2021 Igor Pavlov : 2017-08-28 \| p7zip Version 17.05 (locale=utf8,Utf16=on,HugeFiles=on,64 bits,10 CPUs LE) \| Scanning the drive for archives: \| 1 file, 8738548 bytes (8534 KiB)` |
| `Bejeweled2DeluxeSetup.exe` | `Inno Setup Setup Data (5.2.3)`@216972, `Inno Setup Messages (5.1.11)`@217036, `CHANNEL_NAME=Reflexive`@9254017 | `Done with 1 error. \| Not a supported Inno Setup installer!` | `7-Zip [64] 17.05 : Copyright (c) 1999-2021 Igor Pavlov : 2017-08-28 \| p7zip Version 17.05 (locale=utf8,Utf16=on,HugeFiles=on,64 bits,10 CPUs LE) \| Scanning the drive for archives: \| 1 file, 9274536 bytes (9058 KiB)` |
| `DinerDashSetup.exe` | `Inno Setup Setup Data (5.2.3)`@216972, `Inno Setup Messages (5.1.11)`@217036, `CHANNEL_NAME=Reflexive`@9532131 | `Done with 1 error. \| Not a supported Inno Setup installer!` | `7-Zip [64] 17.05 : Copyright (c) 1999-2021 Igor Pavlov : 2017-08-28 \| p7zip Version 17.05 (locale=utf8,Utf16=on,HugeFiles=on,64 bits,10 CPUs LE) \| Scanning the drive for archives: \| 1 file, 9552643 bytes (9329 KiB)` |
| `MysteryCaseFilesHuntsvilleSetup.exe` | `Inno Setup Setup Data (5.2.3)`@216972, `Inno Setup Messages (5.1.11)`@217036, `CHANNEL_NAME=Reflexive`@23949712 | `Done with 1 error. \| Not a supported Inno Setup installer!` | `7-Zip [64] 17.05 : Copyright (c) 1999-2021 Igor Pavlov : 2017-08-28 \| p7zip Version 17.05 (locale=utf8,Utf16=on,HugeFiles=on,64 bits,10 CPUs LE) \| Scanning the drive for archives: \| 1 file, 23970241 bytes (23 MiB)` |

## Archive Overlap Readiness

- Torrent setup installers: 1696
- Title matches against the archive corpus: 1058
- Effective archive overlap roots with unwrap data: 1057
- Already unwrap-capable if extraction yields familiar layouts: 1037
- Overlap `direct` roots: 37
- Overlap `static` roots: 1000
- Overlap `unsupported` roots: 20
- Overlap titles that matched by name but do not map cleanly onto an effective archive root: 1

### Dominant Overlap Layouts

| Layout | Count |
| --- | ---: |
| `wrapped_rwg_with_config` | 944 |
| `wrapped_raw001_with_config` | 46 |
| `dll_only_with_application_dat` | 38 |
| `helper_exe_with_application_dat` | 15 |
| `other` | 8 |
| `wrapped_rwg_without_raw_002` | 6 |

### Dominant Overlap Launcher Builds

| Build | Count |
| --- | ---: |
| `173` | 988 |
| `none` | 56 |
| `172` | 3 |
| `143` | 2 |
| `145` | 1 |
| `156` | 1 |
| `123` | 1 |
| `167` | 1 |

### Dominant Overlap DLL Major Versions

| DLL major | Count |
| --- | ---: |
| `3` | 1 |
| `5` | 1056 |

## Known Overlap Unsupported Titles

- `BudRedheadSetup.exe` -> `Reflexive Arcade B/Bud Redhead`
- `CashCowSetup.exe` -> `Reflexive Arcade C/Cash Cow/bin`
- `ColonySetup.exe` -> `Reflexive Arcade C/Colony`
- `DigbysDonutsSetup.exe` -> `Reflexive Arcade D/Digby's Donuts`
- `FiveCardDeluxeSetup.exe` -> `Reflexive Arcade F/Five Card Deluxe`
- `FlipWordsSetup.exe` -> `Reflexive Arcade F/Flip Words`
- `HolidayExpressSetup.exe` -> `Reflexive Arcade H/Holiday Express`
- `IceBreakerSetup.exe` -> `Reflexive Arcade I/Ice Breaker`
- `LiveBilliardsSetup.exe` -> `Reflexive Arcade L/Live Billiards`
- `MaxGammonSetup.exe` -> `Reflexive Arcade M/MaxGammon`
- `OrbzSetup.exe` -> `Reflexive Arcade O/Orbz`
- `PacQuest3DSetup.exe` -> `Reflexive Arcade P/PacQuest 3D`
- `PuzzleExpressSetup.exe` -> `Reflexive Arcade P/Puzzle Express`
- `RicochetLostWorldsSetup.exe` -> `Reflexive Arcade R/Ricochet Lost Worlds`
- `SecretChamberSetup.exe` -> `Reflexive Arcade S/Secret Chamber`
- `SnowyTheBearsAdventureSetup.exe` -> `Reflexive Arcade S/Snowy The Bears Adventure`
- `Solitaire2Setup.exe` -> `Reflexive Arcade S/Solitaire 2`
- `ThinkTanksSetup.exe` -> `Reflexive Arcade T/Think Tanks`
- `TriviaMachineSetup.exe` -> `Reflexive Arcade T/Trivia Machine`
- `WildWestWendySetup.exe` -> `Reflexive Arcade W/Wild West Wendy`

## Probe Priorities

Known overlap titles that should already fit the current unwrapper once extraction works:
- `10DaysUnderTheSeaSetup.exe`
- `AlienShooterSetup.exe`
- `FamilyFeudSetup.exe`
- `AbraAcademySetup.exe`
- `AirportManiaSetup.exe`

Known overlap titles that are likely post-extraction reversing targets:
- `BudRedheadSetup.exe`
- `DigbysDonutsSetup.exe`
- `OrbzSetup.exe`
- `Solitaire2Setup.exe`
- `ThinkTanksSetup.exe`

Non-overlap titles worth sampling to see whether rutracker also carries non-Reflexive installer families:
- `Bejeweled2DeluxeSetup.exe`
- `DinerDashSetup.exe`
- `MysteryCaseFilesHuntsvilleSetup.exe`
- `LuxorSetup.exe`
- `FarmFrenzySetup.exe`

## Plan

- Manifest overlap titles already look favorable: 1037 of 1057 effective overlap roots are already unwrap-capable in the current archive corpus if extraction yields comparable wrapper trees.
- The existing static/direct unwrapper path should remain the default for extracted trees that contain `RAW_001*`, `RAW_002*`, `*.RWG`, or familiar `ReflexiveArcade.dll` layouts.
- The main new engineering work is likely installer extraction rather than new decryption logic: we need to detect the original portal installer families first, then feed their extracted output into the current wrapper scanner and unwrapper.
- The currently known archive-side gaps are concentrated in the integrated-wrapper cohort, so titles that line up with those roots should be treated as likely post-extraction reversing targets rather than simple extractor work.
- Once the live source is readable, extractor work should be split by detected installer technology rather than by publisher guesswork. Current top observed technologies: Inno Setup signature (1696).
- Representative overlap and non-overlap samples all expose Reflexive-branded Inno Setup markers, but standard `innoextract` and `7z` fail on those same installers, so the first new script should target this Reflexive-customized Inno variant rather than a new wrapper decryption family.
- Where `7z` does succeed, it only reveals a trailing branding ZIP rather than the installer payload itself, as seen in BudRedheadSetup.exe.
