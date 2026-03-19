from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import reflexive.integrated_wrappers as integrated_wrappers


def test_structural_candidate_requires_unsupported_top_level_without_wrapper_sidecars(
    tmp_path: Path, monkeypatch
) -> None:
    wrapper_root = tmp_path / "Alien Sky"
    wrapper_root.mkdir()
    (wrapper_root / "AlienSky.exe").write_bytes(b"MZ")
    record = {
        "primary_wrapper_binary": {
            "role": "top_level_exe",
            "path": "artifacts/extracted/rutracker/Alien Sky/AlienSky.exe",
        },
        "binary_candidates": [
            {
                "role": "top_level_exe",
                "path": "artifacts/extracted/rutracker/Alien Sky/AlienSky.exe",
            }
        ],
    }

    monkeypatch.setattr(
        integrated_wrappers.unwrap,
        "choose_strategy",
        lambda record, wrapper_root: SimpleNamespace(kind="unsupported"),
    )
    monkeypatch.setattr(integrated_wrappers.unwrap, "choose_child_payload", lambda wrapper_root: None)
    monkeypatch.setattr(integrated_wrappers.unwrap, "choose_config_path", lambda wrapper_root: None)

    is_candidate, reasons = integrated_wrappers.structural_candidate(record, wrapper_root)

    assert is_candidate is True
    assert reasons == []


def test_scan_binding_signals_detects_dynamic_loader_pattern(tmp_path: Path) -> None:
    exe_path = tmp_path / "AlienSky.exe"
    exe_path.write_bytes(
        b"MZ"
        + b"ReflexiveArcade.dll\x00"
        + b"LoadLibraryA\x00"
        + b"GetProcAddress\x00"
        + b"radll_Initialize\x00"
        + b"radll_HasTheProductBeenPurchased\x00"
    )

    result = integrated_wrappers.scan_binding_signals(exe_path)

    assert result["binding_mode"] == "dynamic_loader"
    assert result["likely_integrated"] is True
    assert result["references_reflexive_dll_string"] is True
    assert result["references_radll_exports"] is True
    assert result["references_load_library_name"] is True
    assert result["references_get_proc_address_name"] is True
    assert result["radll_export_names"] == [
        "radll_HasTheProductBeenPurchased",
        "radll_Initialize",
    ]
