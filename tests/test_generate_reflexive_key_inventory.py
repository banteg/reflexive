from __future__ import annotations

from pathlib import Path

from reflexive.generate_reflexive_key_inventory import derive_private_exponent, extract_embedded_key_material
from reflexive.generate_reflexive_key_inventory import load_historical_private_entries


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
    assert result.prime_factors_hex == ["06CF9D0B9A4D6F389A31", "07BA0EDB3385D2B101DD"]
    assert result.private_exponent_hex == "1ABD872BF6F35041892550797506D085A75901"


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
