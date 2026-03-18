# Sources

This project now tracks external inputs as named sources. Each source gets:

- a stable repo-local artifact path
- source-scoped extracted and unwrapped roots under `artifacts/extracted/<source_id>` and `artifacts/unwrapped/<source_id>`
- a dedicated notes page under `docs/sources/`
- a status label so unpacking and reversing work can distinguish confirmed facts from pending intake

## Source Registry

| Source | Repo-local path | Status | Notes |
| --- | --- | --- | --- |
| `archive` | `artifacts/sources/archive` | analyzed | Unofficial 2008 repack mirror of the `Reflexive Arcade Games Collection` bundles. |
| `ruboard` | `artifacts/ruboard` | analyzed | Historical forum dump covering Reflexive wrappers, keygens, and archival discussion from the Ru.Board community. |
| `rutracker_patches` | `artifacts/rutracker/patches` | analyzed | Auxiliary patch/reference corpus used for wrapper build attribution and historical crack context. |
| `rutracker` | `artifacts/sources/rutracker` | extracted | Primary source linked to the RuTracker anthology release; the full corpus is extracted and the current unwrapper sweep covers `1661/1697` effective roots with no remaining execution errors. |

## Notes

- [archive.md](archive.md)
- [ruboard.md](ruboard.md)
- [rutracker_patches.md](rutracker_patches.md)
- [rutracker.md](rutracker.md)
- [rutracker_publisher_attribution.md](rutracker_publisher_attribution.md)
- [rutracker_probe.md](rutracker_probe.md)
- [rutracker_unwrapper_sweep.md](rutracker_unwrapper_sweep.md)
