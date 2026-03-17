# RuTracker

## Source Record

- Source id: `rutracker`
- Repo-local path: `artifacts/sources/rutracker`
- Original path: `/Users/banteg/Downloads/Reflexive`
- Repo-local torrent: `artifacts/rutracker-3687027.torrent`
- Source type: torrent-backed installer corpus
- Status: manifest parsed, directory intake still blocked
- Planned extracted root: `artifacts/extracted/rutracker`
- Planned unwrapped root: `artifacts/unwrapped/rutracker`
- Game list: `docs/game_lists/rutracker.md`

## Initial Analysis

This source is promising because it is separate from the known 2008 Florian/TopBancuri repack and
appears to be tied to a much larger RuTracker anthology that may preserve original Reflexive-
distributed installers.

What is confirmed so far:

- `/Users/banteg/Downloads/Reflexive` exists and is a directory.
- A repo-local symlink at `artifacts/sources/rutracker` points to that location.
- The repo-local torrent copy at `artifacts/rutracker-3687027.torrent` is readable and parses cleanly.
- The current process still cannot enumerate the directory contents. Both shell `ls` and Python
  `Path.iterdir()` fail with `Operation not permitted`.

## Attribution

The working attribution for this source is the RuTracker thread:

- <https://rutracker.org/forum/viewtopic.php?t=3687027>

The thread title resolves to:

- `[DL] [Антология] Игры от Reflexive Entertainment [L] [ENG / ENG] (2010, Arcade)`

The visible release metadata on that page states:

- year range: `200?—2010`
- genre: `Arcade`
- source: `Digital`
- edition type: `Лицензия`
- release: `Reflexive`
- interface language: `английский`
- voice language: `английский`
- crack: `отсутствует`
- claimed collection size: `1696` games and about `60` cracks
- reported torrent size: `59.85 GB`
- magnet info hash: `5DDC17FA07475962A3BCA35E3F145E14ADABD644`

There is also a local `.torrent` file whose name matches that thread id:

- `/Users/banteg/dev/banteg/reflexive/artifacts/rutracker-3687027.torrent`

Confirmed from the local torrent metadata:

- torrent `name`: `Reflexive`
- comment: `https://rutracker.org/forum/viewtopic.php?t=3687027`
- announce URL: `http://bt2.t-ru.org/ann`
- announce list includes `http://bt2.t-ru.org/ann` and `http://retracker.local/announce`
- info hash: `5DDC17FA07475962A3BCA35E3F145E14ADABD644`
- created by: `qBittorrent v5.1.4`
- torrent creation date: `2026-02-12T20:32:41Z`
- file count: `1698`
- total size: `64259348595` bytes
- payload makeup: `1696` `.exe` files, `1` `.7z`, `1` `.par2`
- file layout is flat rather than nested under subdirectories
- installer naming is consistent with titles like `10DaysUnderTheSeaSetup.exe`, `4ElementsSetup.exe`,
  `AbraAcademySetup.exe`, and `20000LeaguesUndertheSeaSetup.exe`

What is not confirmed yet:

- whether the files currently present in `/Users/banteg/Downloads/Reflexive` match the torrent
  manifest exactly
- installer technologies across the corpus
- publisher signatures or PE version metadata
- overlap or divergence relative to the `archive` source

## Working Implications

This source is no longer just a placeholder. The torrent manifest confirms a much larger flat
installer corpus than the `archive` repack source and strongly suggests mostly original
`*Setup.exe` installers rather than bundled repack volumes.

The remaining blocker is only the live directory intake. The symlink gives the repo a stable local
path for future scripts and notes, but it does not bypass macOS privacy controls on `Downloads`.

## Next Steps Once Readable

- inventory filenames, extensions, and hashes
- compare the live directory against the confirmed torrent manifest
- compare title coverage against the `archive` source and extracted game list
- classify installer technologies such as MSI, Inno Setup, InstallShield, NSIS, or custom
  Reflexive stubs
- extract signer, version, and timestamp metadata from representative installers
- prioritize titles that can improve the remaining unsupported unwrapper cases
