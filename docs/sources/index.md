# Sources

This project now tracks external inputs as named sources. Each source gets:

- a stable repo-local artifact path
- a dedicated notes page under `docs/sources/`
- a status label so unpacking and reversing work can distinguish confirmed facts from pending intake

## Source Registry

| Source | Repo-local path | Status | Notes |
| --- | --- | --- | --- |
| `archive_org_repack` | `artifacts/archive/reflexivearcadegamescollection` | analyzed | Unofficial 2008 repack mirror of the `Reflexive Arcade Games Collection` bundles. |
| `rutracker_patches` | `artifacts/rutracker/patches` | analyzed | Auxiliary patch/reference corpus used for wrapper build attribution and historical crack context. |
| `reflexive_downloads` | `artifacts/sources/reflexive_downloads` | registered | New source that likely contains original installers; current environment can see the root path but cannot enumerate contents yet. |

## Notes

- [archive_org_repack.md](archive_org_repack.md)
- [rutracker_patches.md](rutracker_patches.md)
- [reflexive_downloads.md](reflexive_downloads.md)
