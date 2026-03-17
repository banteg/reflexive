# RuTracker

## Source Record

- Source id: `rutracker`
- Repo-local path: `artifacts/sources/rutracker`
- Original path: `/Users/banteg/Downloads/Reflexive`
- Source type: suspected original installer corpus
- Status: registered, pending readable access
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
- The current process still cannot enumerate the directory contents. Both shell `ls` and Python
  `Path.iterdir()` fail with `Operation not permitted`.

What is not confirmed yet:

- file count
- filename scheme
- installer formats
- publisher signatures or PE version metadata
- overlap or divergence relative to the `archive` source

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

- `/Users/banteg/Downloads/[DL] [Антология] Игры от Reflexive Entertainment [L] [ENG ENG] (2010, Arcade) [rutracker-3687027].torrent`

What is confirmed locally about that file:

- it exists
- its size is `169865` bytes
- the current process cannot read its contents because of the same macOS `Downloads` permission
  boundary affecting the installer directory itself

## Working Implications

The source should be treated as registered but not yet ingested. The symlink gives the repo a
stable local path for future scripts and notes, but it does not bypass macOS privacy controls on
`Downloads`.

## Next Steps Once Readable

- inventory filenames, extensions, and hashes
- compare title coverage against the repack bundles and extracted game list
- classify installer technologies such as MSI, Inno Setup, InstallShield, NSIS, or custom
  Reflexive stubs
- extract signer, version, and timestamp metadata from representative installers
- prioritize titles that can improve the remaining unsupported unwrapper cases
