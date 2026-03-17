# Archive.org Repack

## Source Record

- Source id: `archive_org_repack`
- Repo-local path: `artifacts/archive/reflexivearcadegamescollection`
- Source type: mirror of a third-party repack set
- Status: analyzed

## Attribution

These installers are not generic "Smart Install Maker" packages only. Smart Install Maker is the
packaging tool. The repack attribution is narrower.

The `Reflexive Arcade <letter>.exe` bundles in this collection are consistent with a single
unofficial third-party repack set attributed inside the installers to:

- `Florian`
- `www.TopBancuri.ro`

## Local Evidence

Across the bundles inspected locally, the Smart Install Maker metadata is consistent:

- Title strings such as `Reflexive Arcade Games Collection - X - By Florian 07.12.2008`
- Repeated site URL `http://www.topbancuri.ro`
- Bundle names like `Reflexive Arcade Games Collection X`
- Default install roots like `Reflexive Arcade Games Collection\\X`

The outer installer version info is branded as `Reflexive Arcade`, but that branding belongs to
the repack wrapper and should not be treated as proof that the installers are official publisher
releases.

## Unofficial Modifications

The extracted installs include paired launcher files such as `Ingenious.exe` and
`Ingenious.exe.BAK`. In the locally extracted `Reflexive Arcade I` bundle, the launcher and its
`.BAK` differ by only two bytes, which matches the preserved original-vs-patched launcher pattern
seen in earlier reverse-engineering work on these same repacks.

That is consistent with pre-cracked third-party redistributions, not original Reflexive
installers.

## Distribution Trail

The installer metadata stamps the bundles with `By Florian 07.12.2008`.

A local copy of the torrent `REFLEXIVE ARCADE GAMES COLLECTION - 1100 Games` with info hash
`78DFF22C325815C46F26DC2A275B879B1BFB3947` matches the Archive.org mirror on every installer file
name and byte length:

- the torrent contains the same `26` `Reflexive Arcade *.exe` installers
- every installer size matches the Archive.org mirror exactly
- the torrent additionally contains `--- ReadMe ---.txt`
- the Archive.org mirror additionally contains Archive.org metadata files and the mirrored
  `.torrent`

The corresponding Pirate Bay description page is:

- <https://thepiratebay.org/description.php?id=4591769>

The Archive.org item is a later mirror, not the original repack source:

- <https://archive.org/download/reflexivearcadegamescollection>
