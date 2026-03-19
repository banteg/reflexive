from __future__ import annotations

from pathlib import Path


SOURCE_LABELS = {
    "archive": "Archive.org",
    "rutracker": "RuTracker",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def artifacts_root() -> Path:
    return repo_root() / "artifacts"


def source_root(source_id: str) -> Path:
    return artifacts_root() / "sources" / source_id


def extracted_root(source_id: str) -> Path:
    return artifacts_root() / "extracted" / source_id


def unwrapped_root(source_id: str) -> Path:
    return artifacts_root() / "unwrapped" / source_id


def source_label(source_id: str) -> str:
    return SOURCE_LABELS.get(source_id, source_id.replace("_", " ").title())


def infer_source_id_from_installer_path(installer_path: Path) -> str | None:
    path = installer_path.resolve()
    candidates = {
        source_root("archive"): "archive",
        repo_root() / "artifacts" / "archive" / "reflexivearcadegamescollection": "archive",
        source_root("rutracker"): "rutracker",
    }

    for root, source_id in candidates.items():
        try:
            path.relative_to(root.resolve())
            return source_id
        except ValueError:
            continue

    return None


def infer_source_id_from_extracted_root(path: Path) -> str | None:
    resolved = path.resolve()
    extracted_parent = artifacts_root() / "extracted"

    try:
        relative = resolved.relative_to(extracted_parent.resolve())
    except ValueError:
        return None

    if not relative.parts:
        return None
    return relative.parts[0]
