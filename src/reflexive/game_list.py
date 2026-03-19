#!/usr/bin/env -S uv run --script
# /// script
# ///

from __future__ import annotations

import argparse
from pathlib import Path

from .source_layout import repo_root, infer_source_id_from_extracted_root, source_label


def default_output_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "game_list.md"


def archive_sort_key(path: Path) -> tuple[int, str]:
    suffix = path.name.removeprefix("Reflexive Arcade ")
    if suffix == "0-9":
        return (0, suffix)
    return (1, suffix)


def collect_archives(extracted_root: Path) -> list[tuple[str, list[str]]]:
    archives: list[tuple[str, list[str]]] = []
    for archive_dir in sorted(
        (
            path
            for path in extracted_root.iterdir()
            if path.is_dir() and path.name.startswith("Reflexive Arcade ")
        ),
        key=archive_sort_key,
    ):
        games = sorted(path.name for path in archive_dir.iterdir() if path.is_dir())
        archives.append((archive_dir.name, games))
    return archives


def render_markdown(
    archives: list[tuple[str, list[str]]],
    extracted_root: Path,
    source_id: str,
    source_label: str,
) -> str:
    total_games = sum(len(games) for _, games in archives)
    root = repo_root()
    try:
        extracted_display = extracted_root.relative_to(root)
    except ValueError:
        extracted_display = extracted_root

    lines = [
        f"# {source_label} Game List",
        "",
        f"- Source id: `{source_id}`",
        "- Generated from the extracted top-level game directories under "
        f"`{extracted_display}`.",
        "",
        f"- Archive bundles: {len(archives)}",
        f"- Extracted game directories: {total_games}",
        "",
    ]

    for archive_name, games in archives:
        lines.append(f"## {archive_name} ({len(games)})")
        lines.append("")
        lines.extend(f"- {game}" for game in games)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown list of extracted Reflexive Arcade game directories."
    )
    parser.add_argument(
        "--source-id",
        default=None,
        help="Stable source id to include in the generated document. Defaults to the id inferred from extracted_root.",
    )
    parser.add_argument(
        "--source-label",
        default=None,
        help="Human-readable source label for the document title. Defaults to the label for --source-id.",
    )
    parser.add_argument(
        "extracted_root",
        type=Path,
        help="Root containing extracted `Reflexive Arcade *` directories.",
    )
    parser.add_argument(
        "output_path",
        nargs="?",
        type=Path,
        default=None,
        help="Markdown file to write. Defaults to docs/generated/<source_id>/game_list.md when the source can be inferred.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    extracted_root = args.extracted_root.resolve()
    source_id = args.source_id or infer_source_id_from_extracted_root(extracted_root)
    if source_id is None:
        raise SystemExit(f"unable to infer source id from {extracted_root}; pass --source-id explicitly")
    source_label_text = args.source_label or source_label(source_id)
    output_path = args.output_path.resolve() if args.output_path else default_output_path(source_id)

    archives = collect_archives(extracted_root)
    if not archives:
        raise SystemExit(f"no extracted archive directories found in {extracted_root}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_markdown(
            archives,
            extracted_root,
            source_id=source_id,
            source_label=source_label_text,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
