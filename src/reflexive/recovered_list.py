from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .source_layout import repo_root as source_repo_root
from .source_layout import source_label


@dataclass(frozen=True)
class RecoveredListRow:
    name: str
    game_id: int
    modulus_hex: str
    private_exponent_hex: str
    classification: str


def repo_root() -> Path:
    return source_repo_root()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def default_inventory_path(source_id: str = "rutracker") -> Path:
    return repo_root() / "docs" / "generated" / source_id / "key_inventory.json"


def default_output_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "list.txt"


def choose_name(record: dict[str, object]) -> str:
    list_name = record.get("list_name")
    if isinstance(list_name, str) and list_name:
        return list_name
    game_name_guess = record.get("game_name_guess")
    if isinstance(game_name_guess, str) and game_name_guess:
        return game_name_guess
    app_id = record.get("app_id")
    raise ValueError(f"record is missing both list_name and game_name_guess for app_id={app_id!r}")


def classify_record(record: dict[str, object]) -> str:
    if record.get("list_name") is None:
        return "added"
    if record.get("list_modulus_match") is False:
        return "replaced_public_key"
    if record.get("list_private_exponent_match") is False:
        return "replaced_private_exponent"
    return "kept"


def build_rows(report: dict[str, object]) -> list[RecoveredListRow]:
    rows_by_game_id: dict[int, RecoveredListRow] = {}
    for record in report["records"]:
        app_id = record.get("app_id")
        modulus_hex = record.get("modulus_hex")
        private_exponent_hex = record.get("private_exponent_hex")
        if app_id is None or modulus_hex is None or private_exponent_hex is None:
            continue

        row = RecoveredListRow(
            name=choose_name(record),
            game_id=int(app_id),
            modulus_hex=str(modulus_hex).upper(),
            private_exponent_hex=str(private_exponent_hex).upper(),
            classification=classify_record(record),
        )

        existing = rows_by_game_id.get(row.game_id)
        if existing is None:
            rows_by_game_id[row.game_id] = row
            continue
        if existing.modulus_hex != row.modulus_hex or existing.private_exponent_hex != row.private_exponent_hex:
            raise ValueError(f"conflicting recovered rows for app_id={row.game_id}")
        if existing.name != row.name and existing.classification == "added" and row.classification != "added":
            rows_by_game_id[row.game_id] = row

    return sorted(rows_by_game_id.values(), key=lambda row: row.game_id)


def render_list_text(rows: list[RecoveredListRow]) -> str:
    return "".join(
        f"{row.name}|{row.game_id}|{row.modulus_hex}|{row.private_exponent_hex}|\n"
        for row in rows
    )


def summarize_rows(rows: list[RecoveredListRow]) -> dict[str, int]:
    counts = Counter(row.classification for row in rows)
    return {
        "rows": len(rows),
        "kept": counts["kept"],
        "replaced_public_key": counts["replaced_public_key"],
        "replaced_private_exponent": counts["replaced_private_exponent"],
        "added": counts["added"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a recovered Reflexive list.txt from a key inventory report.")
    parser.add_argument(
        "inventory_json",
        nargs="?",
        type=Path,
        default=default_inventory_path(),
        help="path to a key_inventory.json report",
    )
    parser.add_argument("--output", type=Path, help="write recovered list.txt here")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    inventory_path = args.inventory_json.resolve()
    report = json.loads(inventory_path.read_text(encoding="utf-8"))
    rows = build_rows(report)
    summary = summarize_rows(rows)

    source_id = report.get("source_id")
    output_path = args.output
    if output_path is None:
        if not isinstance(source_id, str) or not source_id:
            raise SystemExit("--output is required when the inventory report has no source_id")
        output_path = default_output_path(source_id)
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_list_text(rows), encoding="utf-8")

    source_label_text = source_label(source_id) if isinstance(source_id, str) else None
    if source_label_text is not None:
        print(f"source={source_label_text}")
    print(f"rows={summary['rows']}")
    print(f"kept={summary['kept']}")
    print(f"replaced_public_key={summary['replaced_public_key']}")
    print(f"replaced_private_exponent={summary['replaced_private_exponent']}")
    print(f"added={summary['added']}")
    print(f"output={display_path(output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
