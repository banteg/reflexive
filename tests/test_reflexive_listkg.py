from __future__ import annotations

import pytest

from reflexive.reflexive_listkg import build_message_bytes, generate_for_entry, ListkgEntry, parse_product_code
from reflexive.reflexive_listkg import synthesize_product_code


def test_synthesize_product_code_defaults_to_revision_a() -> None:
    product_code = synthesize_product_code(66, [1, 2, 3, 4, 5])
    assert product_code.startswith("EA")
    product = parse_product_code(product_code)
    assert product.game_id == 66
    assert product.group_values[:5] == [1, 2, 3, 4, 5]


def test_synthesize_product_code_supports_revision_b() -> None:
    product_code = synthesize_product_code(53, [1, 2, 3, 4, 5], revision="B")
    assert product_code.startswith("EB")
    product = parse_product_code(product_code)
    assert product.game_id == 53
    assert product.group_values[:5] == [1, 2, 3, 4, 5]


def test_synthesize_product_code_rejects_invalid_revision() -> None:
    with pytest.raises(ValueError, match="unsupported revision character"):
        synthesize_product_code(53, [1, 2, 3, 4, 5], revision="-")


def test_build_message_bytes_matches_unpacker_for_zuma_registration_code() -> None:
    assert build_message_bytes("4861598").hex() == "35a3811c2c235ffb1c3f83097c8c3aa321031f00"


def test_generate_for_entry_matches_listkg_for_zuma_deluxe_sample() -> None:
    entry = ListkgEntry(
        name="Zuma Deluxe",
        game_id=368,
        modulus_hex="32BB4BD2EF0B240DAAFE90A96F714D0066AF25",
        exponent_hex="D97D1C13AFBA935604FF3EE67E901D6168D01",
    )
    generated = generate_for_entry(entry, [1614])

    assert generated.registration_code == "4861598"
    assert generated.unlock_code == "FAADRAIAALEOE6PI7UV9J4AX69JPFZTIJ"
