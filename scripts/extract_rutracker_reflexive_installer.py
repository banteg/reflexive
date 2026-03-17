#!/usr/bin/env -S uv run --script
# /// script
# ///

from __future__ import annotations

import argparse
import shutil
import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from source_layout import extracted_root as source_extracted_root


OUTER_MAGIC = 0xFE03D185
ENTRY_MAGIC = 0x10B3AF52


@dataclass(frozen=True)
class OuterEntry:
    name: str
    offset: int
    size: int
    record_size: int


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_archive_extracted_root() -> Path:
    return repo_root() / "artifacts" / "extracted" / "archive"


def normalize_title(value: str) -> str:
    lowered = value.lower().removesuffix("setup.exe").removesuffix(".exe")
    lowered = lowered.replace("&", "and")
    return "".join(ch for ch in lowered if ch.isalnum())


def humanize_stem(stem: str) -> str:
    text = stem.replace("_", " ").replace("-", " ")
    result: list[str] = []
    for index, char in enumerate(text):
        if index > 0:
            prev = text[index - 1]
            next_char = text[index + 1] if index + 1 < len(text) else ""
            if char.isupper() and prev.islower():
                result.append(" ")
            elif char.isupper() and prev.isupper() and next_char.islower():
                result.append(" ")
            elif char.isdigit() and prev.isalpha():
                result.append(" ")
            elif char.isalpha() and prev.isdigit():
                result.append(" ")
        result.append(char)
    return " ".join("".join(result).split()) or stem


def collect_archive_titles(extracted_root: Path) -> dict[str, str]:
    titles: dict[str, str] = {}
    if not extracted_root.is_dir():
        return titles

    for bundle_dir in sorted(extracted_root.iterdir()):
        if not bundle_dir.is_dir() or not bundle_dir.name.startswith("Reflexive Arcade "):
            continue
        for game_dir in sorted(bundle_dir.iterdir()):
            if game_dir.is_dir():
                titles[normalize_title(game_dir.name)] = game_dir.name
    return titles


def canonical_title(installer_path: Path, archive_titles: dict[str, str]) -> str:
    stem = installer_path.name.removesuffix(".exe")
    if stem.endswith("Setup"):
        stem = stem[:-5]
    return archive_titles.get(normalize_title(installer_path.name), humanize_stem(stem))


def parse_outer_entries(installer_path: Path) -> tuple[bytes, list[OuterEntry]]:
    data = installer_path.read_bytes()
    if len(data) < 12:
        raise ValueError(f"{installer_path} is too small to contain a ZipLite footer")

    footer_offset = len(data) - 12
    magic, entry_count, dir_offset = struct.unpack_from("<III", data, footer_offset)
    if magic != OUTER_MAGIC:
        raise ValueError(f"{installer_path} does not end with the expected ZipLite footer")
    if entry_count <= 0:
        raise ValueError(f"{installer_path} has no entries in the outer archive")
    if dir_offset < 0 or dir_offset >= footer_offset:
        raise ValueError(f"{installer_path} has an invalid directory offset {dir_offset}")

    entries: list[OuterEntry] = []
    position = dir_offset
    for _ in range(entry_count):
        if position + 12 > footer_offset:
            raise ValueError(f"{installer_path} has a truncated directory record at {position}")

        record_size, offset, size = struct.unpack_from("<III", data, position)
        if record_size < 13 or position + record_size > footer_offset:
            raise ValueError(f"{installer_path} has an invalid directory record size {record_size}")

        raw_name = data[position + 12 : position + record_size]
        name = raw_name.split(b"\x00", 1)[0].decode("latin1")
        if not name:
            raise ValueError(f"{installer_path} has an empty outer entry name")

        stored_size = size + 4
        if offset < 0 or offset + stored_size > dir_offset:
            raise ValueError(f"{installer_path} has an invalid stored extent for {name}")

        prefix = struct.unpack_from("<I", data, offset)[0]
        if prefix != ENTRY_MAGIC:
            raise ValueError(f"{installer_path} entry {name} is missing the expected data prefix")

        entries.append(OuterEntry(name=name, offset=offset, size=size, record_size=record_size))
        position += record_size

    if position != footer_offset:
        raise ValueError(f"{installer_path} directory does not terminate at the footer")

    return data, entries


def write_outer_members(data: bytes, entries: list[OuterEntry], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    preferred_inner = None

    for entry in entries:
        target = out_dir / entry.name
        target.write_bytes(data[entry.offset + 4 : entry.offset + 4 + entry.size])
        if preferred_inner is None and entry.name.lower().endswith(".exe"):
            preferred_inner = target

    if preferred_inner is None:
        raise ValueError("outer archive did not contain an embedded installer executable")
    return preferred_inner


def choose_inner_installer(outer_installer: Path, outer_members_dir: Path) -> Path:
    preferred = outer_members_dir / outer_installer.name
    if preferred.is_file():
        return preferred

    exe_candidates = sorted(path for path in outer_members_dir.iterdir() if path.is_file() and path.suffix.lower() == ".exe")
    if not exe_candidates:
        raise ValueError(f"no embedded installer executable found in {outer_installer}")
    return exe_candidates[0]


def run_innoextract(inner_installer: Path, temp_extract_dir: Path) -> None:
    innoextract = shutil.which("innoextract")
    if innoextract is None:
        raise RuntimeError("innoextract is required but was not found in PATH")

    result = subprocess.run(
        [innoextract, "-s", "-e", "-d", str(temp_extract_dir), str(inner_installer)],
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
    )
    if result.returncode != 0:
        message = (result.stdout + "\n" + result.stderr).strip()
        raise RuntimeError(f"innoextract failed for {inner_installer}:\n{message}")


def move_tree_contents(source_dir: Path, output_root: Path, force: bool) -> None:
    if output_root.exists():
        if not force:
            raise FileExistsError(f"{output_root} already exists; rerun with --force to replace it")
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True, exist_ok=True)
    for child in source_dir.iterdir():
        shutil.move(str(child), str(output_root / child.name))


def materialize_inno_extract(temp_extract_dir: Path, output_root: Path, force: bool) -> None:
    app_dir = temp_extract_dir / "app"
    source_dir = app_dir if app_dir.is_dir() else temp_extract_dir
    move_tree_contents(source_dir, output_root, force=force)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract a RuTracker Reflexive outer installer into an installed game tree."
    )
    parser.add_argument("installer", type=Path, help="Path to the outer RuTracker setup executable.")
    parser.add_argument(
        "output_root",
        nargs="?",
        type=Path,
        help="Directory to write the extracted installed tree into. Defaults to artifacts/extracted/rutracker/<title>.",
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing output directory.")
    parser.add_argument(
        "--archive-extracted-root",
        type=Path,
        default=default_archive_extracted_root(),
        help="Archive extracted root used to recover canonical names for overlapping titles.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    installer_path = args.installer.resolve()
    archive_titles = collect_archive_titles(args.archive_extracted_root.resolve())

    if args.output_root is None:
        title = canonical_title(installer_path, archive_titles)
        output_root = (source_extracted_root("rutracker") / title).resolve()
    else:
        output_root = args.output_root.resolve()

    data, entries = parse_outer_entries(installer_path)

    with tempfile.TemporaryDirectory(prefix="rutracker_outer_") as outer_temp, tempfile.TemporaryDirectory(
        prefix="rutracker_inno_"
    ) as inno_temp:
        outer_dir = Path(outer_temp)
        inno_dir = Path(inno_temp)
        write_outer_members(data, entries, outer_dir)
        inner_installer = choose_inner_installer(installer_path, outer_dir)
        run_innoextract(inner_installer, inno_dir)
        materialize_inno_extract(inno_dir, output_root, force=args.force)

    print(f"Outer installer: {installer_path}")
    print(f"Output root: {output_root}")
    print(f"Outer members: {len(entries)}")
    print(f"Embedded installer: {choose_inner_installer(installer_path, Path(tempfile.gettempdir())) if False else inner_installer.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
