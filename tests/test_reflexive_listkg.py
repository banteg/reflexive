from __future__ import annotations

import pytest

from reflexive.reflexive_listkg import parse_product_code, synthesize_product_code


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
