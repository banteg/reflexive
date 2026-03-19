from __future__ import annotations

import json
from pathlib import Path

from reflexive.generate_reflexive_recovered_list import build_rows, main, render_list_text, summarize_rows


def test_build_rows_classifies_kept_replaced_and_added() -> None:
    report = {
        "records": [
            {
                "app_id": 10,
                "game_name_guess": "Collapse",
                "list_name": "Collapse",
                "modulus_hex": "AA",
                "private_exponent_hex": "BB",
                "list_modulus_match": True,
                "list_private_exponent_match": True,
            },
            {
                "app_id": 20,
                "game_name_guess": "Space Taxi 2",
                "list_name": "Space Taxi 2",
                "modulus_hex": "CC",
                "private_exponent_hex": "DD",
                "list_modulus_match": False,
                "list_private_exponent_match": False,
            },
            {
                "app_id": 30,
                "game_name_guess": "Fiber Twig",
                "list_name": "Fiber Twig",
                "modulus_hex": "EE",
                "private_exponent_hex": "FF",
                "list_modulus_match": True,
                "list_private_exponent_match": False,
            },
            {
                "app_id": 40,
                "game_name_guess": "Youda Camper",
                "list_name": None,
                "modulus_hex": "11",
                "private_exponent_hex": "22",
                "list_modulus_match": None,
                "list_private_exponent_match": None,
            },
        ]
    }

    rows = build_rows(report)

    assert [(row.game_id, row.name, row.classification) for row in rows] == [
        (10, "Collapse", "kept"),
        (20, "Space Taxi 2", "replaced_public_key"),
        (30, "Fiber Twig", "replaced_private_exponent"),
        (40, "Youda Camper", "added"),
    ]
    assert summarize_rows(rows) == {
        "rows": 4,
        "kept": 1,
        "replaced_public_key": 1,
        "replaced_private_exponent": 1,
        "added": 1,
    }
    assert render_list_text(rows) == (
        "Collapse|10|AA|BB|\n"
        "Space Taxi 2|20|CC|DD|\n"
        "Fiber Twig|30|EE|FF|\n"
        "Youda Camper|40|11|22|\n"
    )


def test_build_rows_rejects_conflicting_duplicate_app_ids() -> None:
    report = {
        "records": [
            {
                "app_id": 10,
                "game_name_guess": "Collapse",
                "list_name": "Collapse",
                "modulus_hex": "AA",
                "private_exponent_hex": "BB",
                "list_modulus_match": True,
                "list_private_exponent_match": True,
            },
            {
                "app_id": 10,
                "game_name_guess": "Collapse Copy",
                "list_name": None,
                "modulus_hex": "AA",
                "private_exponent_hex": "CC",
                "list_modulus_match": None,
                "list_private_exponent_match": None,
            },
        ]
    }

    try:
        build_rows(report)
    except ValueError as exc:
        assert "conflicting recovered rows" in str(exc)
    else:
        raise AssertionError("expected conflicting duplicate app ids to fail")


def test_main_writes_default_source_output(tmp_path: Path) -> None:
    inventory_path = tmp_path / "key_inventory.json"
    inventory_path.write_text(
        json.dumps(
            {
                "source_id": "rutracker",
                "records": [
                    {
                        "app_id": 40,
                        "game_name_guess": "Youda Camper",
                        "list_name": None,
                        "modulus_hex": "11",
                        "private_exponent_hex": "22",
                        "list_modulus_match": None,
                        "list_private_exponent_match": None,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output_path = tmp_path / "list.txt"

    exit_code = main([str(inventory_path), "--output", str(output_path)])

    assert exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "Youda Camper|40|11|22|\n"
