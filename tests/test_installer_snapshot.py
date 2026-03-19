from __future__ import annotations

import hashlib
import json
from pathlib import Path

import reflexive.installer_snapshot as installer_snapshot


def test_build_report_filters_rutracker_installers(tmp_path: Path) -> None:
    source_root = tmp_path / "rutracker"
    source_root.mkdir()
    installer = source_root / "ZumaDeluxeSetup.exe"
    installer.write_bytes(b"zuma")
    (source_root / "notes.txt").write_text("ignore", encoding="utf-8")
    (source_root / "payload.bin").write_bytes(b"ignore")

    report = installer_snapshot.build_report(source_root, "rutracker")

    assert report["summary"]["installer_count"] == 1
    assert report["summary"]["total_size_bytes"] == 4
    assert report["records"] == [
        {
            "file_name": "ZumaDeluxeSetup.exe",
            "path": str(installer),
            "size_bytes": 4,
            "sha256": hashlib.sha256(b"zuma").hexdigest(),
        }
    ]


def test_build_report_filters_archive_bundle_installers(tmp_path: Path) -> None:
    source_root = tmp_path / "archive"
    source_root.mkdir()
    installer = source_root / "Reflexive Arcade A.exe"
    installer.write_bytes(b"bundle")
    (source_root / "reflexivearcadegamescollection_meta.xml").write_text("meta", encoding="utf-8")

    report = installer_snapshot.build_report(source_root, "archive")

    assert report["summary"]["installer_count"] == 1
    assert report["records"][0]["file_name"] == "Reflexive Arcade A.exe"


def test_render_markdown_and_main_emit_snapshot(tmp_path: Path, monkeypatch) -> None:
    source_root = tmp_path / "sources" / "rutracker"
    source_root.mkdir(parents=True)
    installer = source_root / "AlienSkySetup.exe"
    installer.write_bytes(b"alien")

    markdown_out = tmp_path / "snapshot.md"
    json_out = tmp_path / "snapshot.json"

    monkeypatch.setattr(
        installer_snapshot,
        "parse_args",
        lambda: type(
            "Args",
            (),
            {
                "source_root": source_root,
                "source_id": "rutracker",
                "markdown_out": markdown_out,
                "json_out": json_out,
            },
        )(),
    )

    assert installer_snapshot.main() == 0
    markdown_text = markdown_out.read_text(encoding="utf-8")
    json_payload = json.loads(json_out.read_text(encoding="utf-8"))

    assert "# RuTracker Installer Snapshot" in markdown_text
    assert "`AlienSkySetup.exe`" in markdown_text
    assert json_payload["summary"]["installer_count"] == 1
