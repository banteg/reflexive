from __future__ import annotations

import json
import struct
from pathlib import Path
from types import SimpleNamespace

import reflexive.key_inventory as key_inventory
from reflexive.key_inventory import EmbeddedKeyMaterial
from reflexive.key_inventory import FactorCacheEntry, HistoricalListEntry, ScannedKeyRecord
from reflexive.key_inventory import build_record, derive_private_exponent, extract_embedded_key_material
from reflexive.key_inventory import load_historical_private_entries
from reflexive.key_inventory import load_factor_cache, parse_msieve_factor_output


def test_extract_embedded_key_material() -> None:
    material, errors = extract_embedded_key_material(
        b"prefix\x00Decryption Key Data=A/3KBCE4G5QWXAW39ZEHQ46VLQFFQTKN\x00/CAAB\x00suffix"
    )
    assert errors == []
    assert material is not None
    assert material.revision == "A"
    assert material.encoded_modulus == "3KBCE4G5QWXAW39ZEHQ46VLQFFQTKN"
    assert material.encoded_public_exponent == "CAAB"
    assert material.modulus_hex == "34A0889B37216B82DAFE48786FB55C0A584D4D"
    assert material.public_exponent == 65537

def test_derive_private_exponent() -> None:
    result = derive_private_exponent(int("34A0889B37216B82DAFE48786FB55C0A584D4D", 16), 65537)
    assert result.backend == "internal"
    assert result.prime_factors_hex == ["06CF9D0B9A4D6F389A31", "07BA0EDB3385D2B101DD"]
    assert result.private_exponent_hex == "1ABD872BF6F35041892550797506D085A75901"


def test_parse_msieve_factor_output() -> None:
    factors = parse_msieve_factor_output(
        "0x34A0889B37216B82DAFE48786FB55C0A584D4D\n"
        "prp23: 32163991228621816109617\n"
        "prp23: 36488730283783782203869\n",
        int("34A0889B37216B82DAFE48786FB55C0A584D4D", 16),
    )
    assert factors == [32163991228621816109617, 36488730283783782203869]


def test_extract_app_id_uses_in_memory_pe_parse(tmp_path: Path, monkeypatch) -> None:
    dll_path = tmp_path / "sample.dll"
    dll_bytes = b"\x68" + struct.pack("<I", 6) + b"\x90" + b"000000aa\x00"
    dll_path.write_bytes(dll_bytes)
    seen: dict[str, object] = {}

    class DummyPE:
        OPTIONAL_HEADER = SimpleNamespace(ImageBase=0)

        def parse_data_directories(self, directories) -> None:
            self.DIRECTORY_ENTRY_EXPORT = SimpleNamespace(
                symbols=[SimpleNamespace(name=b"unittest_GetBrandedApplicationID", address=0)]
            )

        def get_offset_from_rva(self, rva: int) -> int:
            return rva

    def fake_pe(*args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return DummyPE()

    monkeypatch.setattr(key_inventory.pefile, "PE", fake_pe)
    app_id, errors = key_inventory.extract_app_id(dll_path)

    assert app_id == 170
    assert errors == []
    assert seen["args"] == ()
    assert seen["kwargs"] == {"data": dll_bytes, "fast_load": True}


def test_load_historical_private_entries(tmp_path: Path) -> None:
    list_dir = tmp_path / "listkg_1421_by_russiankid"
    list_dir.mkdir()
    (list_dir / "list.txt").write_text(
        "5 Spots|170|34A0889B37216B82DAFE48786FB55C0A584D4D|1ABD872BF6F35041892550797506D085A75901|\n",
        encoding="latin-1",
    )

    entries = load_historical_private_entries(tmp_path)
    entry = entries[(170, "34A0889B37216B82DAFE48786FB55C0A584D4D")]
    assert entry.name == "5 Spots"
    assert entry.game_id == 170
    assert entry.private_exponent_hex == "1ABD872BF6F35041892550797506D085A75901"


def test_load_factor_cache(tmp_path: Path) -> None:
    cache_path = tmp_path / "factor_cache.jsonl"
    cache_path.write_text(
        json.dumps(
            {
                "modulus_hex": "34A0889B37216B82DAFE48786FB55C0A584D4D",
                "public_exponent": 65537,
                "backend": "msieve",
                "prime_factors_hex": ["06CF9D0B9A4D6F389A31", "07BA0EDB3385D2B101DD"],
                "private_exponent_hex": "1ABD872BF6F35041892550797506D085A75901",
                "elapsed_seconds": 0.12,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    entries = load_factor_cache(cache_path)
    entry = entries[("34A0889B37216B82DAFE48786FB55C0A584D4D", 65537)]
    assert entry.backend == "msieve"
    assert entry.prime_factors_hex == ["06CF9D0B9A4D6F389A31", "07BA0EDB3385D2B101DD"]
    assert entry.private_exponent_hex == "1ABD872BF6F35041892550797506D085A75901"


def test_build_record_verifies_historical_entry() -> None:
    material = EmbeddedKeyMaterial(
        revision="A",
        encoded_modulus="3KBCE4G5QWXAW39ZEHQ46VLQFFQTKN",
        encoded_public_exponent="CAAB",
        modulus_hex="34A0889B37216B82DAFE48786FB55C0A584D4D",
        public_exponent=65537,
    )
    historical = HistoricalListEntry(
        name="5 Spots",
        game_id=170,
        modulus_hex="34A0889B37216B82DAFE48786FB55C0A584D4D",
        private_exponent_hex="1ABD872BF6F35041892550797506D085A75901",
        source_path="artifacts/rutracker/_Crack/list.txt",
    )
    scanned = ScannedKeyRecord(
        game_name_guess="5 Spots",
        dll_path="artifacts/extracted/rutracker/5 Spots/ReflexiveArcade/ReflexiveArcade.dll",
        app_id=170,
        key_material=material,
        historical_entry=historical,
        list_name="5 Spots",
        list_modulus_hex="34A0889B37216B82DAFE48786FB55C0A584D4D",
        list_private_exponent_hex="1ABD872BF6F35041892550797506D085A75901",
        errors=[],
    )
    factored = FactorCacheEntry(
        modulus_hex="34A0889B37216B82DAFE48786FB55C0A584D4D",
        public_exponent=65537,
        backend="msieve",
        prime_factors_hex=["06CF9D0B9A4D6F389A31", "07BA0EDB3385D2B101DD"],
        private_exponent_hex="01ABD872BF6F35041892550797506D085A75901",
        elapsed_seconds=0.12,
    )

    record = build_record(
        scanned,
        factor_results={("34A0889B37216B82DAFE48786FB55C0A584D4D", 65537): factored},
        factor_errors={},
        derive_private=True,
        factor_remaining=True,
        verify_known=True,
    )

    assert record.private_exponent_source == "historical_list"
    assert record.factored_private_exponent_source == "msieve"
    assert record.factored_private_exponent_match is True
    assert record.prime_factors_hex == []
    assert record.factored_prime_factors_hex == ["06CF9D0B9A4D6F389A31", "07BA0EDB3385D2B101DD"]


def test_build_record_uses_factored_override_for_invalid_historical_entry() -> None:
    material = EmbeddedKeyMaterial(
        revision="A",
        encoded_modulus="3KBCE4G5QWXAW39ZEHQ46VLQFFQTKN",
        encoded_public_exponent="CAAB",
        modulus_hex="34A0889B37216B82DAFE48786FB55C0A584D4D",
        public_exponent=65537,
    )
    historical = HistoricalListEntry(
        name="5 Spots",
        game_id=170,
        modulus_hex="34A0889B37216B82DAFE48786FB55C0A584D4D",
        private_exponent_hex="02ABD872BF6F35041892550797506D085A75901",
        source_path="artifacts/rutracker/_Crack/list.txt",
    )
    scanned = ScannedKeyRecord(
        game_name_guess="5 Spots",
        dll_path="artifacts/extracted/rutracker/5 Spots/ReflexiveArcade/ReflexiveArcade.dll",
        app_id=170,
        key_material=material,
        historical_entry=historical,
        list_name="5 Spots",
        list_modulus_hex="34A0889B37216B82DAFE48786FB55C0A584D4D",
        list_private_exponent_hex="02ABD872BF6F35041892550797506D085A75901",
        errors=[],
    )
    factored = FactorCacheEntry(
        modulus_hex="34A0889B37216B82DAFE48786FB55C0A584D4D",
        public_exponent=65537,
        backend="msieve",
        prime_factors_hex=["06CF9D0B9A4D6F389A31", "07BA0EDB3385D2B101DD"],
        private_exponent_hex="1ABD872BF6F35041892550797506D085A75901",
        elapsed_seconds=0.12,
    )

    record = build_record(
        scanned,
        factor_results={("34A0889B37216B82DAFE48786FB55C0A584D4D", 65537): factored},
        factor_errors={},
        derive_private=True,
        factor_remaining=True,
        verify_known=True,
    )

    assert record.private_exponent_source == "msieve"
    assert record.private_exponent_hex == "1ABD872BF6F35041892550797506D085A75901"
    assert record.list_private_exponent_match is False
    assert record.factored_private_exponent_match is False
    assert "historical private exponent failed RSA verification" in record.errors[0]
