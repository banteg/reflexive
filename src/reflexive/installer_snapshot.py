#!/usr/bin/env -S uv run --script
# /// script
# ///

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .source_layout import (
    display_path,
    infer_source_id_from_source_root,
    repo_root,
    source_label,
    source_root as source_source_root,
)


INSTALLER_GLOBS = {
    "archive": "Reflexive Arcade *.exe",
    "rutracker": "*Setup.exe",
}


def default_source_root(source_id: str) -> Path:
    return source_source_root(source_id)


def default_markdown_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "installer_snapshot.md"


def default_json_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "installer_snapshot.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def format_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024.0 or unit == "TiB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024.0
    raise AssertionError("unreachable")


def discover_installers(source_root: Path, source_id: str) -> list[Path]:
    pattern = INSTALLER_GLOBS.get(source_id)
    if pattern is None:
        raise ValueError(f"unsupported source id for installer snapshot: {source_id}")
    return sorted(path.resolve() for path in source_root.glob(pattern) if path.is_file())


def build_report(source_root: Path, source_id: str) -> dict[str, Any]:
    installers = discover_installers(source_root, source_id)
    if not installers:
        raise ValueError(f"no installer files found in {source_root} for source id {source_id}")

    records = []
    total_size = 0
    for path in installers:
        size = path.stat().st_size
        total_size += size
        records.append(
            {
                "file_name": path.name,
                "path": display_path(path),
                "size_bytes": size,
                "sha256": sha256_file(path),
            }
        )

    return {
        "source_id": source_id,
        "source_label": source_label(source_id),
        "generated_from": display_path(source_root),
        "summary": {
            "installer_count": len(records),
            "total_size_bytes": total_size,
            "total_size_human": format_size(total_size),
            "glob": INSTALLER_GLOBS[source_id],
        },
        "records": records,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"# {report['source_label']} Installer Snapshot",
        "",
        f"- Source id: `{report['source_id']}`",
        f"- Generated from installer files under `{report['generated_from']}`.",
        f"- Installer glob: `{summary['glob']}`",
        "",
        f"- Installers: {summary['installer_count']}",
        f"- Total installer bytes: {summary['total_size_bytes']}",
        f"- Total installer size: {summary['total_size_human']}",
        "",
        "| File | Size | SHA-256 |",
        "| --- | ---: | --- |",
    ]

    for record in report["records"]:
        lines.append(
            f"| `{record['file_name']}` | {record['size_bytes']} | `{record['sha256']}` |"
        )

    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Snapshot installer filenames, sizes, and SHA-256 hashes for a source corpus."
    )
    parser.add_argument(
        "source_root",
        nargs="?",
        type=Path,
        default=None,
        help="Root containing source installers. Defaults to artifacts/sources/<source_id> when --source-id is provided.",
    )
    parser.add_argument(
        "--source-id",
        default=None,
        help="Stable source id. Defaults to the id inferred from source_root.",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=None,
        help="Markdown output path. Defaults to docs/generated/<source_id>/installer_snapshot.md.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="JSON output path. Defaults to docs/generated/<source_id>/installer_snapshot.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    source_id = args.source_id
    source_root = args.source_root.resolve() if args.source_root is not None else None

    if source_id is None and source_root is not None:
        source_id = infer_source_id_from_source_root(source_root)
    if source_id is None:
        raise SystemExit("unable to infer source id; pass --source-id explicitly")
    if source_root is None:
        source_root = default_source_root(source_id).resolve()

    report = build_report(source_root, source_id)

    markdown_out = args.markdown_out.resolve() if args.markdown_out is not None else default_markdown_path(source_id)
    json_out = args.json_out.resolve() if args.json_out is not None else default_json_path(source_id)

    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.write_text(render_markdown(report), encoding="utf-8")
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"installers={report['summary']['installer_count']}")
    print(f"total_size_bytes={report['summary']['total_size_bytes']}")
    print(f"total_size={report['summary']['total_size_human']}")
    print(f"markdown_out={display_path(markdown_out)}")
    print(f"json_out={display_path(json_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
