# Rutracker Patches

## Source Record

- Source id: `rutracker_patches`
- Repo-local path: `artifacts/rutracker/patches`
- Source type: auxiliary patch and crack reference corpus
- Status: analyzed

## Initial Analysis

This source is not a primary installer corpus. It is a mixed patch archive organized by portal,
protection scheme, and publisher families.

The local tree currently includes categories such as:

- `Reflexive Arcade`
- `RealArcade`
- `Big Fish Games`
- `GameHouse`
- `WildTangent`
- `Armadillo`
- `ASProtect`

Within this project, its main value has been historical context rather than payload recovery:

- corroborating Reflexive wrapper launcher build numbering like `167` through `184`
- comparing crack conventions across wrapper families
- locating older patch logic that may help with the remaining integrated wrapper cases

## Caveats

- This source mixes many unrelated ecosystems, so it should not be treated as direct provenance for
  the game installers themselves.
- Patches here are useful for wrapper study, not for claiming originality of any given game build.
