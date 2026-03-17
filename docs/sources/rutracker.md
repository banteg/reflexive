# RuTracker

## Source Record

- Source id: `rutracker`
- Repo-local path: `artifacts/sources/rutracker`
- Original path: `/Users/banteg/Downloads/Reflexive`
- Repo-local torrent: `artifacts/rutracker-3687027.torrent`
- Source type: torrent-backed installer corpus
- Status: probed
- Planned extracted root: `artifacts/extracted/rutracker`
- Planned unwrapped root: `artifacts/unwrapped/rutracker`
- Game list: `docs/game_lists/rutracker.md`
- Publisher attribution report: `docs/sources/rutracker_publisher_attribution.md`
- Probe report: `docs/sources/rutracker_probe.md`

## Initial Analysis

This source is promising because it is separate from the known 2008 Florian/TopBancuri repack and
appears to be tied to a much larger RuTracker anthology that may preserve original Reflexive-
distributed installers.

What is confirmed so far:

- `artifacts/sources/rutracker` is now a readable repo-local directory with `1698` hardlinked files.
- The repo-local torrent copy at `artifacts/rutracker-3687027.torrent` is readable and parses cleanly.
- The live source contents match the torrent-level shape: `1696` `.exe` installers plus
  `_Crack.7z` and `_Recovery.par2`.
- All `1696` installer stubs are PE executables carrying `Inno Setup Setup Data (5.2.3)`,
  `Inno Setup Messages (5.1.11)`, and `CHANNEL_NAME=Reflexive`.
- A custom outer-installer extractor now exists in `scripts/extract_rutracker_reflexive_installer.py`.

## Extraction

- Single installer: `uv run scripts/extract_rutracker_reflexive_installer.py artifacts/sources/rutracker/10DaysUnderTheSeaSetup.exe`
- Full source: `uv run scripts/extract_rutracker_reflexive_installer.py --all`
- The custom extractor strips the Reflexive `ZipLite` wrapper, recovers the embedded Inno Setup
  installer, and then delegates to `innoextract` for the inner payload.

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

- publisher signatures or PE version metadata
- overlap or divergence relative to the `archive` source after real extraction, rather than by
  filename normalization alone

## Quick Triage

The torrent manifest confirms that this source is broader than the name `Игры от Reflexive
Entertainment` suggests.

Compared against the current `archive` extracted corpus:

- the torrent contains `1696` setup executables
- the `archive` source currently materializes `1086` extracted top-level game directories
- a quick normalized-name comparison matches `1058` archive titles directly to rutracker setup
  installers
- the rutracker manifest still has `638` additional setup installers beyond that overlap
- the residual `28` archive-side misses are a small tail dominated by naming variance, split/mixed
  layouts, and a few non-game or helper entries

The extra catalog is clearly not limited to Reflexive-developed titles. The manifest includes
well-known series associated with several other casual-game publishers and portals, for example:

- PopCap-style catalog: `Bejeweled2Setup.exe`, `BejeweledTwistSetup.exe`,
  `BookwormAdventuresDeluxeSetup.exe`, `PeggleDeluxeSetup.exe`, `ZumaDeluxeSetup.exe`
- GameHouse / PlayFirst / Slingo-style catalog: `DinerDashSetup.exe`, `CollapseSetup.exe`,
  `5CardSlingoSetup.exe`, `JewelQuestSetup.exe`
- Big Fish-style catalog: `MysteryCaseFilesHuntsvilleSetup.exe`, `MysteryCaseFilesRavenhearstSetup.exe`,
  `HiddenExpeditionEverestSetup.exe`, `AzadaSetup.exe`
- MumboJumbo-style catalog: `LuxorSetup.exe`, `Luxor3Setup.exe`, `RicochetSetup.exe`,
  `7WondersTreasuresOfSevenSetup.exe`
- iWin-style catalog: `FamilyFeudSetup.exe`, `FamilyFeudHollywoodSetup.exe`,
  `JojosFashionShowSetup.exe`

So the current best framing is:

- `archive` = a narrower unofficial repack snapshot centered on what looks like a Reflexive portal
  collection
- `rutracker` = a much larger flat installer anthology that spans Reflexive plus many third-party
  casual-game lines distributed through the same broader ecosystem

## Working Implications

This source is no longer just a placeholder. The torrent manifest confirms a much larger flat
installer corpus than the `archive` repack source and strongly suggests mostly original
`*Setup.exe` installers rather than bundled repack volumes.

The current archive overlap also means a large part of the future rutracker intake is already
understood on the wrapper side once extraction works:

- `1058` rutracker setup names match titles in the current archive corpus
- `1057` of those map cleanly onto effective archive unwrap roots
- `1037` of those effective overlap roots are already handled by the current unwrapper
- the remaining known overlap-side post-extraction gaps are the `20` integrated-wrapper titles now
  listed in `docs/sources/rutracker_probe.md`

The extraction blocker is now more specific:

- standard `innoextract` rejects representative overlap and non-overlap installers as `Not a
  supported Inno Setup installer!`
- `7z` also fails on most samples
- where `7z` does return success, it only exposes a trailing branding ZIP rather than the actual
  installer payload

So the remaining engineering step is not outer installer extraction anymore. It is adapting the
existing unwrapper to the original installer variant after extraction, especially around `RAW_002`
seed derivation for original wrapper trees.

## Next Steps

- validate that extracted overlap titles materialize into the same wrapper layouts seen under
  `archive`
- feed extracted overlap trees through the existing wrapper scanner and unwrapper
- prioritize the `20` known integrated-wrapper overlap titles for post-extraction reversing
- sample non-overlap families after extraction to see how much of the broader portal catalog still
  lands in Reflexive-style wrapper trees
