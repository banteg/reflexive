# Reflexive Wrapper Inventory

Generated from wrapper roots discovered under `artifacts/extracted/archive`.

- Wrapper roots: 1084
- `ReflexiveArcade.dll` files: 1084 total / 1084 unique full SHA-256
- Launcher `.exe.BAK` files: 1013 total / 1000 unique full SHA-256
- `ReflexiveArcade.exe` files: 20 total / 6 unique full SHA-256

Full-file SHA-256 is too granular for the support DLLs. The useful grouping signal is the PE section hash.

## Layout Summary

- `wrapped_rwg_with_config`: 952 roots. Example: `Reflexive Arcade 0-9/10 Days Under The Sea`
- `dll_only_with_application_dat`: 49 roots. Example: `Reflexive Arcade A/Air Strike 2`
- `wrapped_raw001_with_config`: 46 roots. Example: `Reflexive Arcade A/A Pirates Legend`
- `helper_exe_with_application_dat`: 20 roots. Example: `Reflexive Arcade E/Double Trump/Electric`
- `other`: 9 roots. Example: `Reflexive Arcade C/Cash Cow/bin`
- `wrapped_rwg_without_raw_002`: 8 roots. Example: `Reflexive Arcade A/Alpha Ball/bin`

## Wrapper Asset Versions

| Asset | Version | Roots | Info String | Example |
| --- | ---: | ---: | --- | --- |
| `Application.version.txt` | `1` | 1083 | `4/22/2003 15:29:02` | `Reflexive Arcade 0-9/10 Days Under The Sea` |
| `Arcade.version.txt` | `19` | 1 | `01/12/2004 01:25:00` | `Reflexive Arcade A/Alpha Ball/bin` |
| `Arcade.version.txt` | `21` | 1 | `01/12/2004 01:25:00` | `Reflexive Arcade T/Turtle Bay` |
| `Arcade.version.txt` | `22` | 1082 | `01/12/2004 01:25:00` | `Reflexive Arcade 0-9/10 Days Under The Sea` |
| `RAManagerData.managerinfo.txt` | `4` | 1084 | `-` | `Reflexive Arcade 0-9/10 Days Under The Sea` |

## Launcher Build Strings

| Build | Roots | Launcher Families | Example |
| --- | ---: | --- | --- |
| `122` | 1 | `launcher_family_12` | `Reflexive Arcade S/Slot Words` |
| `123` | 2 | `launcher_family_03` | `Reflexive Arcade D/Diamond Drop` |
| `124` | 2 | `launcher_family_04` | `Reflexive Arcade E/Emperors Mahjong` |
| `128` | 1 | `launcher_family_11` | `Reflexive Arcade P/Pharaoh's Curse Gold` |
| `131` | 1 | `launcher_family_16` | `Reflexive Arcade W/Word Craft` |
| `142` | 1 | `launcher_family_09` | `Reflexive Arcade M/Mind Your Marbles Christmas Edition` |
| `143` | 2 | `launcher_family_05` | `Reflexive Arcade T/Traffic Jam Extreme` |
| `145` | 1 | `launcher_family_06` | `Reflexive Arcade A/Alpha Ball/bin` |
| `156` | 1 | `launcher_family_07` | `Reflexive Arcade A/Astrobatics` |
| `167` | 1 | `launcher_family_08` | `Reflexive Arcade I/Ice Cream Tycoon` |
| `172` | 3 | `launcher_family_02` | `Reflexive Arcade H/Home Sweet Home` |
| `173` | 993 | `launcher_family_01` | `Reflexive Arcade 0-9/10 Days Under The Sea` |
| `-` | 4 | `launcher_family_10`, `launcher_family_13`, `launcher_family_14`, `launcher_family_15` | `Reflexive Arcade O/Orbz` |

## DLL Families

| Family | Roots | .text | .data | Timestamp | Example | Note |
| --- | ---: | --- | --- | --- | --- | --- |
| `dll_family_01` | 1081 | `d8a3dbb9bc2bb23c` | `18d5843eefdce676` | `2008-08-15T01:29:16Z` | `Reflexive Arcade 0-9/10 Days Under The Sea` | Matches prior Xeno/Xango/XAvenger/Xmas v5 sample |
| `dll_family_02` | 1 | `fe252b9105c0b5b6` | `b5cd1913416f39d5` | `2004-04-01T00:47:34Z` | `Reflexive Arcade A/Alpha Ball/bin` |  |
| `dll_family_03` | 1 | `7b346dff40795f96` | `959452bc016c1f37` | `2008-06-10T21:00:48Z` | `Reflexive Arcade H/Home Sweet Home` |  |
| `dll_family_04` | 1 | `bb08623750681215` | `70b36def5dd39617` | `2004-10-13T21:41:56Z` | `Reflexive Arcade T/Turtle Bay` |  |

## Launcher Families

| Family | Roots | Builds | .text | .rdata | Timestamp | Example | Note |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| `launcher_family_01` | 993 | `173` | `e45e08a30a5769bf` | `4e50f4973b416f93` | `2008-08-26T22:20:21Z` | `Reflexive Arcade 0-9/10 Days Under The Sea` | Matches prior Xeno/Xango/XAvenger/Xmas v5 sample |
| `launcher_family_02` | 3 | `172` | `b23bceca2d9a59c2` | `a6305d73365e1f40` | `2008-07-22T20:28:57Z` | `Reflexive Arcade H/Home Sweet Home` |  |
| `launcher_family_03` | 2 | `123` | `d398538d67f24e35` | `039abd008271dd69` | `2004-07-28T18:14:13Z` | `Reflexive Arcade D/Diamond Drop` |  |
| `launcher_family_04` | 2 | `124` | `61e00d97cedbc10a` | `d9b316fc3b70dbb0` | `2004-08-16T23:25:08Z` | `Reflexive Arcade E/Emperors Mahjong` |  |
| `launcher_family_05` | 2 | `143` | `07aa3cc82b7bb404` | `14be53673e3a826a` | `2004-12-03T00:26:21Z` | `Reflexive Arcade T/Traffic Jam Extreme` |  |
| `launcher_family_06` | 1 | `145` | `e11bbf659453da45` | `8d3f5b1013c8c477` | `2004-12-21T22:37:35Z` | `Reflexive Arcade A/Alpha Ball/bin` |  |
| `launcher_family_07` | 1 | `156` | `27f613e55f369d1c` | `ffbf334e95944742` | `2005-03-02T01:09:08Z` | `Reflexive Arcade A/Astrobatics` |  |
| `launcher_family_08` | 1 | `167` | `160f6577a0e10f4c` | `a497ecc91a496634` | `2007-04-04T21:24:57Z` | `Reflexive Arcade I/Ice Cream Tycoon` |  |
| `launcher_family_09` | 1 | `142` | `e4d6b95f7e163617` | `d1cf3fb08a460908` | `2004-11-24T01:42:23Z` | `Reflexive Arcade M/Mind Your Marbles Christmas Edition` |  |
| `launcher_family_10` | 1 | `-` | `5b58314dbf443431` | `f2b8a86cf4e1a500` | `2003-11-10T21:56:45Z` | `Reflexive Arcade O/Orbz` |  |
| `launcher_family_11` | 1 | `128` | `cdabda884f993280` | `69680a5abdfe7f3f` | `2004-08-25T18:50:39Z` | `Reflexive Arcade P/Pharaoh's Curse Gold` |  |
| `launcher_family_12` | 1 | `122` | `8429677c10704f1e` | `5eebd1797ca41e3f` | `2004-07-27T01:04:45Z` | `Reflexive Arcade S/Slot Words` |  |
| `launcher_family_13` | 1 | `-` | `5566de8af008eb60` | `e582b700b1169a6c` | `2003-07-09T20:18:25Z` | `Reflexive Arcade S/Solitaire 2` |  |
| `launcher_family_14` | 1 | `-` | `97c584204326e8e1` | `36d8395a6071c40c` | `2004-11-18T19:33:46Z` | `Reflexive Arcade T/Tablut` |  |
| `launcher_family_15` | 1 | `-` | `371aa6ff962192ba` | `02ec861a883e97f6` | `2003-11-07T00:00:25Z` | `Reflexive Arcade T/Think Tanks` |  |
| `launcher_family_16` | 1 | `131` | `5f5f0b8bf45f6c62` | `55eaa1da765c809f` | `2004-08-31T01:00:44Z` | `Reflexive Arcade W/Word Craft` |  |

## Helper EXE Families

| Family | Roots | .text | .rdata | Timestamp | Example |
| --- | ---: | --- | --- | --- | --- |
| `helper_exe_family_01` | 6 | `e2296f9570fb9375` | `72880443856db5a7` | `2004-03-22T20:02:05Z` | `Reflexive Arcade E/Double Trump/Electric` |
| `helper_exe_family_02` | 5 | `75786e3fc2a398f0` | `b1e233d87b5b3a2f` | `2003-08-04T18:03:02Z` | `Reflexive Arcade F/Flip Wit!` |
| `helper_exe_family_03` | 5 | `fcbed52cf6212fc5` | `33463695e2d7023f` | `2004-07-28T22:09:00Z` | `Reflexive Arcade J/Jigsaw365` |
| `helper_exe_family_04` | 2 | `cf97b36173d76371` | `2c7e3065a9f8247a` | `2003-08-28T23:54:01Z` | `Reflexive Arcade G/Garfield Goes to Pieces` |
| `helper_exe_family_05` | 1 | `784b288cd658b5fd` | `b13c5366be52d5ad` | `2004-02-20T23:20:59Z` | `Reflexive Arcade E/Playtonium Jigsaw Enchanted Forest` |
| `helper_exe_family_06` | 1 | `078acbf0577d6f6d` | `9a32235f2144aae6` | `2004-12-01T22:22:23Z` | `Reflexive Arcade G/Gold Miner` |

## Dominant DLL/Launcher Pairs

| Roots | DLL Family | Launcher Family | Example |
| ---: | --- | --- | --- |
| 993 | `dll_family_01` | `launcher_family_01` | `Reflexive Arcade 0-9/10 Days Under The Sea` |
| 71 | `dll_family_01` | `-` | `Reflexive Arcade A/Air Strike 2` |
| 2 | `dll_family_01` | `launcher_family_03` | `Reflexive Arcade D/Diamond Drop` |
| 2 | `dll_family_01` | `launcher_family_04` | `Reflexive Arcade E/Emperors Mahjong` |
| 2 | `dll_family_01` | `launcher_family_02` | `Reflexive Arcade T/The Legend Of El Dorado` |
| 1 | `dll_family_02` | `launcher_family_06` | `Reflexive Arcade A/Alpha Ball/bin` |
| 1 | `dll_family_01` | `launcher_family_07` | `Reflexive Arcade A/Astrobatics` |
| 1 | `dll_family_03` | `launcher_family_02` | `Reflexive Arcade H/Home Sweet Home` |
| 1 | `dll_family_01` | `launcher_family_08` | `Reflexive Arcade I/Ice Cream Tycoon` |
| 1 | `dll_family_01` | `launcher_family_09` | `Reflexive Arcade M/Mind Your Marbles Christmas Edition` |

## Binja Priorities

- The patcher README's `167-184` wording lines up with launcher build strings, not the coarse DLL export major. The corpus is overwhelmingly `Build 173`, with smaller `Build 172` and `Build 167` pockets still inside that range.
- Start with the dominant pair `dll_family_01` + `launcher_family_01`. It covers 993 wrapper roots, reports `Build 173`, and matches the already-studied Xeno/Xango/XAvenger/Xmas sample.
- Then look at the three one-off DLL outliers: `dll_family_02` (`Alpha Ball/bin`), `dll_family_03` (`Home Sweet Home`), and `dll_family_04` (`Turtle Bay`).
- After that, inspect the small launcher outliers that still use `dll_family_01`, because they may be title-specific wrapper revisions rather than a new DLL generation. The four best targets are the no-literal-build launchers: `Orbz`, `Solitaire 2`, `Tablut`, and `Think Tanks`.
- Use the JSON inventory for exact full hashes and per-root mapping.

