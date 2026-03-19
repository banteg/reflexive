#!/usr/bin/env -S uv run --script
# /// script
# ///

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_source_root() -> Path:
    return repo_root() / "artifacts" / "sources" / "rutracker"


def default_torrent_path() -> Path:
    return repo_root() / "artifacts" / "rutracker-3687027.torrent"


def default_archive_extracted_root() -> Path:
    return repo_root() / "artifacts" / "extracted" / "archive"


def default_output_path() -> Path:
    return repo_root() / "docs" / "generated" / "rutracker" / "game_list.md"


def decode_bencode(buf: bytes, index: int = 0):
    token = buf[index : index + 1]
    if token == b"i":
        end = buf.index(b"e", index)
        return int(buf[index + 1 : end]), end + 1
    if token == b"l":
        items = []
        index += 1
        while buf[index : index + 1] != b"e":
            value, index = decode_bencode(buf, index)
            items.append(value)
        return items, index + 1
    if token == b"d":
        items = {}
        index += 1
        while buf[index : index + 1] != b"e":
            key, index = decode_bencode(buf, index)
            value, index = decode_bencode(buf, index)
            items[key] = value
        return items, index + 1
    colon = buf.index(b":", index)
    size = int(buf[index:colon])
    start = colon + 1
    end = start + size
    return buf[start:end], end


def decode_text(value: bytes) -> str:
    for encoding in ("utf-8", "cp1251", "latin-1"):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            continue
    return value.decode("utf-8", "replace")


def normalize_title(value: str) -> str:
    lowered = value.lower().removesuffix("setup.exe").removesuffix(".exe")
    lowered = lowered.replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "", lowered)


def humanize_stem(stem: str) -> str:
    text = stem.replace("_", " ").replace("-", " ")
    text = re.sub(r"(?<=[0-9])(?=[A-Z])", " ", text)
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or stem


def parse_torrent_files(torrent_path: Path) -> list[str]:
    meta, end = decode_bencode(torrent_path.read_bytes())
    if end != torrent_path.stat().st_size:
        raise ValueError(f"failed to parse complete torrent file: {torrent_path}")

    info = meta[b"info"]
    files = info.get(b"files", [])
    parsed: list[str] = []
    for entry in files:
        path = "/".join(decode_text(part) for part in entry[b"path"])
        parsed.append(Path(path).name)
    return parsed


def collect_archive_titles(extracted_root: Path) -> dict[str, str]:
    titles: dict[str, str] = {}
    for bundle_dir in sorted(extracted_root.iterdir()):
        if not bundle_dir.is_dir() or not bundle_dir.name.startswith("Reflexive Arcade "):
            continue
        for game_dir in sorted(bundle_dir.iterdir()):
            if not game_dir.is_dir():
                continue
            titles[normalize_title(game_dir.name)] = game_dir.name
    return titles


def build_game_list(
    source_root: Path,
    torrent_path: Path,
    archive_extracted_root: Path,
) -> dict[str, object]:
    source_files = sorted(path.name for path in source_root.iterdir() if path.is_file())
    torrent_files = sorted(parse_torrent_files(torrent_path))

    source_file_set = set(source_files)
    torrent_file_set = set(torrent_files)
    missing_from_source = sorted(torrent_file_set - source_file_set)
    unexpected_in_source = sorted(source_file_set - torrent_file_set)

    setup_files = sorted(name for name in source_files if name.lower().endswith("setup.exe"))
    archive_titles = collect_archive_titles(archive_extracted_root)

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    overlap_count = 0

    for file_name in setup_files:
        stem = file_name.removesuffix("Setup.exe")
        normalized = normalize_title(file_name)
        archive_title = archive_titles.get(normalized)
        if archive_title is not None:
            display_title = archive_title
            overlap_count += 1
        else:
            display_title = humanize_stem(stem)

        group = "0-9" if display_title[:1].isdigit() else display_title[:1].upper()
        grouped[group].append(
            {
                "display_title": display_title,
                "file_name": file_name,
            }
        )

    for group_entries in grouped.values():
        group_entries.sort(key=lambda item: (item["display_title"].lower(), item["file_name"].lower()))

    ordered_groups = []
    for group in sorted(grouped, key=lambda value: (value != "0-9", value)):
        ordered_groups.append((group, grouped[group]))

    return {
        "source_file_count": len(source_files),
        "setup_installer_count": len(setup_files),
        "non_setup_files": sorted(name for name in source_files if not name.lower().endswith("setup.exe")),
        "torrent_file_count": len(torrent_files),
        "missing_from_source": missing_from_source,
        "unexpected_in_source": unexpected_in_source,
        "archive_overlap_count": overlap_count,
        "groups": ordered_groups,
    }


def render_markdown(report: dict[str, object], source_root: Path, torrent_path: Path) -> str:
    root = repo_root()
    try:
        source_display = source_root.relative_to(root)
    except ValueError:
        source_display = source_root
    try:
        torrent_display = torrent_path.relative_to(root)
    except ValueError:
        torrent_display = torrent_path

    groups: list[tuple[str, list[dict[str, str]]]] = report["groups"]  # type: ignore[assignment]
    non_setup_files: list[str] = report["non_setup_files"]  # type: ignore[assignment]
    missing_from_source: list[str] = report["missing_from_source"]  # type: ignore[assignment]
    unexpected_in_source: list[str] = report["unexpected_in_source"]  # type: ignore[assignment]

    lines = [
        "# RuTracker Game List",
        "",
        "- Source id: `rutracker`",
        f"- Generated from the live source files under `{source_display}`.",
        f"- Verified against the torrent manifest at `{torrent_display}`.",
        "",
        f"- Source files: {report['source_file_count']}",
        f"- Setup installers: {report['setup_installer_count']}",
        f"- Archive-overlap titles with canonical archive naming: {report['archive_overlap_count']}",
        f"- Non-setup payload files: {len(non_setup_files)}",
        "",
    ]

    if non_setup_files:
        lines.append("Non-setup payloads:")
        lines.extend(f"- `{name}`" for name in non_setup_files)
        lines.append("")

    lines.append(f"- Torrent manifest files: {report['torrent_file_count']}")
    lines.append(f"- Missing from source relative to torrent manifest: {len(missing_from_source)}")
    lines.append(f"- Unexpected in source relative to torrent manifest: {len(unexpected_in_source)}")
    lines.append("")

    if missing_from_source:
        lines.append("Missing from source:")
        lines.extend(f"- `{name}`" for name in missing_from_source[:20])
        lines.append("")

    if unexpected_in_source:
        lines.append("Unexpected in source:")
        lines.extend(f"- `{name}`" for name in unexpected_in_source[:20])
        lines.append("")

    lines.append(
        "Titles below are derived from flat installer filenames by stripping `Setup.exe`, with canonical archive names used where the title overlaps the current `archive` corpus."
    )
    lines.append("")

    for group, entries in groups:
        lines.append(f"## {group} ({len(entries)})")
        lines.append("")
        for entry in entries:
            lines.append(f"- {entry['display_title']} (`{entry['file_name']}`)")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the RuTracker installer-derived game list.")
    parser.add_argument("--source-root", type=Path, default=default_source_root(), help="Readable RuTracker source root.")
    parser.add_argument("--torrent-path", type=Path, default=default_torrent_path(), help="RuTracker torrent manifest.")
    parser.add_argument(
        "--archive-extracted-root",
        type=Path,
        default=default_archive_extracted_root(),
        help="Archive extracted root used to recover canonical titles for overlap entries.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=default_output_path(),
        help="Markdown output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = args.source_root.resolve()
    torrent_path = args.torrent_path.resolve()
    archive_extracted_root = args.archive_extracted_root.resolve()
    output_path = args.output_path.resolve()

    report = build_game_list(source_root, torrent_path, archive_extracted_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(report, source_root, torrent_path), encoding="utf-8")
    print(f"Wrote {output_path}")
    print(
        "Summary:"
        f" files={report['source_file_count']}"
        f" setup_installers={report['setup_installer_count']}"
        f" archive_overlap={report['archive_overlap_count']}"
        f" missing={len(report['missing_from_source'])}"
        f" unexpected={len(report['unexpected_in_source'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
