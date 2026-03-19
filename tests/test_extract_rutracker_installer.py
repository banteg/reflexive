from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from reflexive.extract_rutracker_installer import (
    SKIPPED_EXISTING,
    UNWRAPPED_REUSED_EXTRACTED,
    extract_and_optionally_unwrap,
)
import reflexive.extract_rutracker_installer as extract_rutracker_installer


def test_skip_existing_extracted_root_avoids_reextract(tmp_path: Path, monkeypatch) -> None:
    installer_path = tmp_path / "AlienSkySetup.exe"
    installer_path.write_bytes(b"setup")
    extracted_root = tmp_path / "Alien Sky"
    extracted_root.mkdir()

    called = {"extract": False}

    def fake_extract_installer(*args, **kwargs):
        called["extract"] = True
        raise AssertionError("extract_installer should not run")

    monkeypatch.setattr(extract_rutracker_installer, "extract_installer", fake_extract_installer)

    status = extract_and_optionally_unwrap(
        installer_path,
        extracted_root,
        force=False,
        skip_existing=True,
        archive_titles={},
        unwrap_after=False,
        keep_extracted=False,
        unwrapped_output_root=None,
    )

    assert status == SKIPPED_EXISTING
    assert called["extract"] is False


def test_skip_existing_reuses_extracted_tree_for_unwrap(tmp_path: Path, monkeypatch) -> None:
    installer_path = tmp_path / "AlienSkySetup.exe"
    installer_path.write_bytes(b"setup")
    extracted_root = tmp_path / "Alien Sky"
    extracted_root.mkdir()
    unwrapped_root = tmp_path / "unwrapped" / "Alien Sky"

    called = {"extract": False, "unwrap": False}

    def fake_extract_installer(*args, **kwargs):
        called["extract"] = True
        raise AssertionError("extract_installer should not run")

    def fake_unwrap_extracted_tree(source_root: Path, output_root: Path, force: bool):
        called["unwrap"] = True
        assert source_root == extracted_root
        assert output_root == unwrapped_root
        assert force is False
        return SimpleNamespace(ok_roots=("game",), unsupported_roots=())

    monkeypatch.setattr(extract_rutracker_installer, "extract_installer", fake_extract_installer)
    monkeypatch.setattr(extract_rutracker_installer, "unwrap_extracted_tree", fake_unwrap_extracted_tree)

    status = extract_and_optionally_unwrap(
        installer_path,
        extracted_root,
        force=False,
        skip_existing=True,
        archive_titles={},
        unwrap_after=True,
        keep_extracted=False,
        unwrapped_output_root=unwrapped_root,
    )

    assert status == UNWRAPPED_REUSED_EXTRACTED
    assert called["extract"] is False
    assert called["unwrap"] is True
