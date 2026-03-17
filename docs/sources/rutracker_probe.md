# RuTracker Probe

- Source id: `rutracker`
- Source root: `/Users/banteg/Downloads/Reflexive`
- Torrent manifest: `artifacts/rutracker-3687027.torrent`
- Archive comparison root: `artifacts/extracted/archive`
- Archive unwrapper sweep: `docs/reflexive_unwrapper_sweep.json`
- Archive wrapper version scan: `docs/reflexive_wrapper_versions.json`

## Live Source Status

- Live rutracker source status: `blocked`
- Probe error: `[Errno 1] Operation not permitted: '/Users/banteg/Downloads/Reflexive'`
- Byte-level installer classification is deferred until the source becomes readable through a repo-local copy or a permission change.

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
- The live `rutracker` source is still unreadable through the Downloads symlink, so byte-level installer technology clustering remains blocked until the source is copied repo-local or this app gets access.
