from __future__ import annotations

from pathlib import Path

import reflexive.rutracker_game_list as rutracker_game_list


def test_build_game_list_prefers_metadata_titles(tmp_path: Path, monkeypatch) -> None:
    source_root = tmp_path / "sources"
    source_root.mkdir()
    (source_root / "Around3DSetup.exe").write_bytes(b"")
    (source_root / "AlienSkySetup.exe").write_bytes(b"")

    monkeypatch.setattr(
        rutracker_game_list,
        "parse_torrent_files",
        lambda path: ["Around3DSetup.exe", "AlienSkySetup.exe"],
    )
    monkeypatch.setattr(
        rutracker_game_list,
        "collect_archive_titles",
        lambda root: {"aliensky": "Alien Sky"},
    )

    report = rutracker_game_list.build_game_list(
        source_root,
        tmp_path / "rutracker.torrent",
        tmp_path / "archive",
        {"around3d": "Around 3D"},
    )

    groups = dict(report["groups"])
    assert report["metadata_title_count"] == 1
    assert groups["A"][0]["display_title"] == "Alien Sky"
    assert groups["A"][1]["display_title"] == "Around 3D"
