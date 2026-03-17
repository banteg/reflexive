from __future__ import annotations

from pathlib import Path


DEFAULT_SOURCE_ID = "archive_org_repack"
SOURCE_LABELS = {
    "archive_org_repack": "Archive.org Repack",
    "reflexive_downloads": "Reflexive Downloads",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def artifacts_root() -> Path:
    return repo_root() / "artifacts"


def extracted_root(source_id: str = DEFAULT_SOURCE_ID) -> Path:
    return artifacts_root() / "extracted" / source_id


def unwrapped_root(source_id: str = DEFAULT_SOURCE_ID) -> Path:
    return artifacts_root() / "unwrapped" / source_id


def source_label(source_id: str) -> str:
    return SOURCE_LABELS.get(source_id, source_id.replace("_", " ").title())


def infer_source_id_from_installer_path(installer_path: Path) -> str:
    path = installer_path.resolve()
    repo = repo_root()
    candidates = {
        repo / "artifacts" / "archive" / "reflexivearcadegamescollection": "archive_org_repack",
        repo / "artifacts" / "sources" / "reflexive_downloads": "reflexive_downloads",
    }

    for root, source_id in candidates.items():
        try:
            path.relative_to(root.resolve())
            return source_id
        except ValueError:
            continue

    return DEFAULT_SOURCE_ID


def infer_source_id_from_extracted_root(path: Path) -> str | None:
    resolved = path.resolve()
    extracted_parent = artifacts_root() / "extracted"

    try:
        relative = resolved.relative_to(extracted_parent.resolve())
    except ValueError:
        return None

    if not relative.parts:
        return DEFAULT_SOURCE_ID
    return relative.parts[0]
