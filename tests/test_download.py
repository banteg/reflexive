from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import reflexive.download as download


class DummyResponse(io.BytesIO):
    def __enter__(self) -> DummyResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def getcode(self) -> int:
        return 200


def test_resolve_record_accepts_metadata_title() -> None:
    records = [
        download.InstallerRecord(
            file_name="Around3DSetup.exe",
            size_bytes=123,
            sha256="aa",
            title="Around 3D",
        )
    ]

    resolved = download.resolve_record("Around 3D", records)

    assert resolved.file_name == "Around3DSetup.exe"


def test_download_record_verifies_hash_and_size(tmp_path: Path, monkeypatch) -> None:
    payload = b"installer-bytes"
    record = download.InstallerRecord(
        file_name="AirStrike2Setup.exe",
        size_bytes=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        title="Air Strike 2",
    )
    output_path = tmp_path / record.file_name

    monkeypatch.setattr(download.urllib.request, "urlopen", lambda request: DummyResponse(payload))

    status = download.download_record(
        record,
        base_url="https://reflexive.banteg.xyz/",
        output_path=output_path,
        force=False,
    )

    assert status == "downloaded"
    assert output_path.read_bytes() == payload


def test_load_manifest_records_reads_titles(tmp_path: Path) -> None:
    manifest_path = tmp_path / "download_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "file_name": "Around3DSetup.exe",
                        "title": "Around 3D",
                        "size_bytes": 123,
                        "sha256": "aa",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    records = download.load_manifest_records(manifest_path)

    assert records[0].title == "Around 3D"
