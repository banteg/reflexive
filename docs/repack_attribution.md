# Repack Attribution

These installers should not be described as generic "Smart Install Maker" packages only.
Smart Install Maker is the packaging tool. The repack attribution is much narrower.

## Attribution

The `Reflexive Arcade <letter>.exe` bundles in this collection are consistent with a single
unofficial third-party repack set attributed inside the installers to:

- `Florian`
- `www.TopBancuri.ro`

Recommended wording:

- `unofficial Florian / TopBancuri.ro Reflexive Arcade Games Collection repacks`

## Local evidence

Across the bundles inspected locally, the Smart Install Maker metadata is consistent:

- Title strings such as `Reflexive Arcade Games Collection - X - By Florian 07.12.2008`
- Repeated site URL `http://www.topbancuri.ro`
- Bundle names like `Reflexive Arcade Games Collection X`
- Default install roots like `Reflexive Arcade Games Collection\\X`

The outer installer version info is branded as `Reflexive Arcade`, but that branding belongs to
the repack wrapper and should not be treated as proof that the installers are official publisher
releases.

## Why they are clearly unofficial

The extracted installs include paired launcher files such as `Ingenious.exe` and
`Ingenious.exe.BAK`. In the locally extracted `Reflexive Arcade I` bundle, the launcher and its
`.BAK` differ by only two bytes, which matches the preserved original-vs-patched launcher pattern
seen in earlier reverse-engineering work on these same repacks.

That is consistent with pre-cracked third-party redistributions, not original Reflexive
installers.

## Distribution trail

The installer metadata stamps the bundles with `By Florian 07.12.2008`.

A public torrent listing for `REFLEXIVE ARCADE GAMES COLLECTION - 1100 Games` was uploaded on
`2008-12-21` by `florian_g` and described the bundle as `patched and working`, which matches the
local installer metadata and the patched launcher backups:

- <https://tpb.party/torrent/4593872/REFLEXIVE_ARCADE_GAMES_COLLECTION_-_1100_Games>

The Archive.org item is a later mirror, not the original repack source:

- <https://archive.org/download/reflexivearcadegamescollection>

## Bottom line

These should be described as unofficial 2008 Florian / TopBancuri.ro repacks of Reflexive games,
later mirrored on Archive.org, not as official Reflexive installers and not merely as anonymous
Smart Install Maker archives.
