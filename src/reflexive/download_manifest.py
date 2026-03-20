from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .installer_snapshot import default_json_path as default_snapshot_path
from .source_layout import display_path, repo_root
from .title_metadata import load_titles_from_key_inventory, normalize_title_key


def default_inventory_path() -> Path:
    return repo_root() / "docs" / "generated" / "rutracker" / "key_inventory.json"


def default_output_path() -> Path:
    return repo_root() / "src" / "reflexive" / "data" / "rutracker_download_manifest.json"


def build_manifest(
    snapshot_report: dict[str, Any],
    title_map: dict[str, str],
    *,
    snapshot_path: str,
    inventory_path: str,
) -> dict[str, Any]:
    records = []
    for row in snapshot_report["records"]:
        file_name = str(row["file_name"])
        records.append(
            {
                "file_name": file_name,
                "title": title_map.get(normalize_title_key(file_name)),
                "size_bytes": int(row["size_bytes"]),
                "sha256": str(row["sha256"]),
            }
        )

    return {
        "source_id": snapshot_report.get("source_id"),
        "source_label": snapshot_report.get("source_label"),
        "base_url": "https://reflexive.banteg.xyz/",
        "generated_from": {
            "installer_snapshot_json": snapshot_path,
            "key_inventory_json": inventory_path,
            "source_root": snapshot_report.get("generated_from"),
        },
        "summary": {
            "installer_count": len(records),
        },
        "records": records,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the packaged installer download manifest from the RuTracker snapshot and key inventory."
    )
    parser.add_argument(
        "--snapshot-path",
        type=Path,
        default=default_snapshot_path("rutracker"),
        help="Installer snapshot JSON.",
    )
    parser.add_argument(
        "--inventory-path",
        type=Path,
        default=default_inventory_path(),
        help="Key inventory JSON used for metadata-backed titles.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=default_output_path(),
        help="Packaged output manifest path.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    snapshot_path = args.snapshot_path.resolve()
    inventory_path = args.inventory_path.resolve()
    output_path = args.output_path.resolve()

    snapshot_report = json.loads(snapshot_path.read_text(encoding="utf-8"))
    title_map = load_titles_from_key_inventory(inventory_path)
    manifest = build_manifest(
        snapshot_report,
        title_map,
        snapshot_path=display_path(snapshot_path),
        inventory_path=display_path(inventory_path),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"installers={manifest['summary']['installer_count']}")
    print(f"snapshot={display_path(snapshot_path)}")
    print(f"inventory={display_path(inventory_path)}")
    print(f"output={display_path(output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
