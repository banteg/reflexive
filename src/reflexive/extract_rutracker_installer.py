#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pefile"]
# ///

from __future__ import annotations

import argparse
import re
import shutil
import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .source_layout import extracted_root as source_extracted_root
from .source_layout import source_root as source_source_root
from .source_layout import unwrapped_root as source_unwrapped_root
from .unwrap_installer_tree import unwrap_extracted_tree


OUTER_MAGIC = 0xFE03D185
ENTRY_MAGIC = 0x10B3AF52
RUTRACKER_INSTALLER_GLOB = "*Setup.exe"


@dataclass(frozen=True)
class OuterEntry:
    name: str
    offset: int
    size: int
    record_size: int


SKIPPED_EXISTING = "skipped_existing"
EXTRACTED_ONLY = "extracted"
UNWRAPPED_FRESH = "unwrapped_fresh"
UNWRAPPED_REUSED_EXTRACTED = "unwrapped_reused_extracted"

def default_archive_extracted_root() -> Path:
    return source_extracted_root("archive")


def default_rutracker_source_root() -> Path:
    return source_source_root("rutracker")


def default_rutracker_unwrapped_root() -> Path:
    return source_unwrapped_root("rutracker")


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


def extract_installer(
    installer_path: Path,
    output_root: Path,
    *,
    force: bool,
    archive_titles: dict[str, str] | None = None,
) -> Path:
    installer_path = installer_path.resolve()
    output_root = output_root.resolve()
    archive_titles = archive_titles or {}

    data, entries = parse_outer_entries(installer_path)

    with tempfile.TemporaryDirectory(prefix="rutracker_outer_") as outer_temp, tempfile.TemporaryDirectory(
        prefix="rutracker_inno_"
    ) as inno_temp:
        outer_dir = Path(outer_temp)
        inno_dir = Path(inno_temp)
        write_outer_members(data, entries, outer_dir)
        inner_installer = choose_inner_installer(installer_path, outer_dir)
        run_innoextract(inner_installer, inno_dir)
        materialize_inno_extract(inno_dir, output_root, force=force)
        embedded_installer_name = inner_installer.name

    title = canonical_title(installer_path, archive_titles)
    print(f"Outer installer: {installer_path}")
    print(f"Title: {title}")
    print(f"Output root: {output_root}")
    print(f"Outer members: {len(entries)}")
    print(f"Embedded installer: {embedded_installer_name}")
    return output_root


def safe_temp_prefix(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-") or "installer"


def extract_and_optionally_unwrap(
    installer_path: Path,
    extracted_output_root: Path,
    *,
    force: bool,
    skip_existing: bool,
    archive_titles: dict[str, str],
    unwrap_after: bool,
    keep_extracted: bool,
    unwrapped_output_root: Path | None,
) -> str:
    installer_path = installer_path.resolve()
    extracted_output_root = extracted_output_root.resolve()
    final_unwrapped_root = None if unwrapped_output_root is None else unwrapped_output_root.resolve()
    title = canonical_title(installer_path, archive_titles)

    if skip_existing:
        if unwrap_after:
            if final_unwrapped_root is not None and final_unwrapped_root.exists():
                print(f"Skipping existing unwrapped root: {final_unwrapped_root}")
                return SKIPPED_EXISTING
            if final_unwrapped_root is not None and extracted_output_root.exists():
                print(f"Reusing extracted tree: {extracted_output_root}")
                unwrap_result = unwrap_extracted_tree(extracted_output_root, final_unwrapped_root, force=False)
                print(f"Unwrapped root: {final_unwrapped_root}")
                print(f"Materialized wrapper roots: {len(unwrap_result.ok_roots)}")
                if unwrap_result.unsupported_roots:
                    print("Unsupported wrapper roots:")
                    for root in unwrap_result.unsupported_roots:
                        print(f"  - {root}")
                return UNWRAPPED_REUSED_EXTRACTED
        elif extracted_output_root.exists():
            print(f"Skipping existing extracted root: {extracted_output_root}")
            return SKIPPED_EXISTING

    if not unwrap_after:
        extract_installer(installer_path, extracted_output_root, force=force, archive_titles=archive_titles)
        return EXTRACTED_ONLY

    if final_unwrapped_root is None:
        raise ValueError("unwrap destination is required when --unwrap is enabled")

    if keep_extracted:
        extracted_tree = extract_installer(
            installer_path,
            extracted_output_root,
            force=force,
            archive_titles=archive_titles,
        )
        unwrap_result = unwrap_extracted_tree(extracted_tree, final_unwrapped_root, force=force)
        status = UNWRAPPED_FRESH
    else:
        temp_parent = final_unwrapped_root.parent
        temp_parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=f".{safe_temp_prefix(title)}.unwrap.", dir=temp_parent) as temp_dir_str:
            temp_extract_root = Path(temp_dir_str) / title
            extracted_tree = extract_installer(
                installer_path,
                temp_extract_root,
                force=True,
                archive_titles=archive_titles,
            )
            unwrap_result = unwrap_extracted_tree(extracted_tree, final_unwrapped_root, force=force)
        status = UNWRAPPED_FRESH

    print(f"Unwrapped root: {final_unwrapped_root}")
    print(f"Materialized wrapper roots: {len(unwrap_result.ok_roots)}")
    if unwrap_result.unsupported_roots:
        print("Unsupported wrapper roots:")
        for root in unwrap_result.unsupported_roots:
            print(f"  - {root}")
        if not keep_extracted:
            print("Rerun with --keep-extracted to retain the extracted tree for inspection.")
    return status


def collect_batch_installers(installers_root: Path) -> list[Path]:
    if not installers_root.is_dir():
        raise FileNotFoundError(f"rutracker source directory does not exist: {installers_root}")

    installers = sorted(path for path in installers_root.glob(RUTRACKER_INSTALLER_GLOB) if path.is_file())
    if not installers:
        raise FileNotFoundError(
            f"no rutracker installers matching {RUTRACKER_INSTALLER_GLOB!r} found in {installers_root}"
        )
    return installers


def extract_all_installers(
    installers_root: Path,
    output_root: Path,
    *,
    force: bool,
    skip_existing: bool,
    archive_titles: dict[str, str],
    unwrap_after: bool,
    keep_extracted: bool,
    unwrapped_root: Path | None,
) -> int:
    installers_root = installers_root.resolve()
    output_root = output_root.resolve()
    installers = collect_batch_installers(installers_root)
    output_root.mkdir(parents=True, exist_ok=True)

    print(f"Source directory: {installers_root}")
    print(f"Output root: {output_root}")
    print(f"Installers: {len(installers)}")
    if unwrap_after and unwrapped_root is not None:
        print(f"Unwrapped root: {unwrapped_root.resolve()}")

    status_counts = {
        SKIPPED_EXISTING: 0,
        EXTRACTED_ONLY: 0,
        UNWRAPPED_FRESH: 0,
        UNWRAPPED_REUSED_EXTRACTED: 0,
    }

    for installer_path in installers:
        title = canonical_title(installer_path, archive_titles)
        destination = output_root / title
        print(f"\n[{installer_path.stem}] {title}")
        unwrap_destination = None if unwrapped_root is None else unwrapped_root / title
        status = extract_and_optionally_unwrap(
            installer_path,
            destination,
            force=force,
            skip_existing=skip_existing,
            archive_titles=archive_titles,
            unwrap_after=unwrap_after,
            keep_extracted=keep_extracted,
            unwrapped_output_root=unwrap_destination,
        )
        status_counts[status] += 1

    print("")
    print(f"Completed: {status_counts[EXTRACTED_ONLY] + status_counts[UNWRAPPED_FRESH] + status_counts[UNWRAPPED_REUSED_EXTRACTED]}")
    print(f"Skipped existing: {status_counts[SKIPPED_EXISTING]}")
    if unwrap_after:
        print(f"Fresh unwrapped: {status_counts[UNWRAPPED_FRESH]}")
        print(f"Reused extracted: {status_counts[UNWRAPPED_REUSED_EXTRACTED]}")

    return len(installers)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract one or more RuTracker Reflexive outer installers into installed game trees."
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        type=Path,
        help=(
            "Single mode: path to the outer RuTracker setup executable. "
            "Batch mode (--all): directory containing the RuTracker installer corpus."
        ),
    )
    parser.add_argument(
        "output_root",
        nargs="?",
        type=Path,
        help=(
            "Single mode: directory to write the extracted installed tree into. "
            "Defaults to artifacts/extracted/rutracker/<title>. "
            "Batch mode (--all): extracted root that will receive one directory per installer."
        ),
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help=(
            "Extract every RuTracker installer matching "
            f"{RUTRACKER_INSTALLER_GLOB!r}. Defaults to artifacts/sources/rutracker."
        ),
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing output directory.")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help=(
            "Continue past existing outputs instead of stopping. "
            "When --unwrap is enabled, reuse an existing extracted tree if available."
        ),
    )
    parser.add_argument(
        "--unwrap",
        action="store_true",
        help=(
            "After extraction, materialize wrapper-free outputs under artifacts/unwrapped/rutracker "
            "or the path passed via --unwrapped-root."
        ),
    )
    parser.add_argument(
        "--keep-extracted",
        action="store_true",
        help="Keep the extracted installer tree when --unwrap is enabled.",
    )
    parser.add_argument(
        "--unwrapped-root",
        type=Path,
        default=default_rutracker_unwrapped_root(),
        help=(
            "Single mode: destination directory for the wrapper-free tree when --unwrap is enabled. "
            "Batch mode (--all): root that will receive one wrapper-free directory per installer."
        ),
    )
    parser.add_argument(
        "--archive-extracted-root",
        type=Path,
        default=default_archive_extracted_root(),
        help="Archive extracted root used to recover canonical names for overlapping titles.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    archive_titles = collect_archive_titles(args.archive_extracted_root.resolve())
    if args.keep_extracted and not args.unwrap:
        print("error: --keep-extracted requires --unwrap")
        return 1

    try:
        if args.all:
            installers_root = (
                args.input_path.resolve() if args.input_path else default_rutracker_source_root().resolve()
            )
            if installers_root.is_file():
                raise ValueError(f"expected a rutracker source directory for --all, got file: {installers_root}")
            output_root = args.output_root.resolve() if args.output_root else source_extracted_root("rutracker")
            extract_all_installers(
                installers_root,
                output_root,
                force=args.force,
                skip_existing=args.skip_existing,
                archive_titles=archive_titles,
                unwrap_after=args.unwrap,
                keep_extracted=args.keep_extracted,
                unwrapped_root=args.unwrapped_root.resolve() if args.unwrap else None,
            )
        else:
            if args.input_path is None:
                raise ValueError("missing installer path; pass a setup EXE or use --all")
            installer_path = args.input_path.resolve()
            if installer_path.is_dir():
                raise ValueError(f"expected a setup EXE, got directory: {installer_path}")
            if args.output_root is None:
                title = canonical_title(installer_path, archive_titles)
                output_root = (source_extracted_root("rutracker") / title).resolve()
            else:
                output_root = args.output_root.resolve()
            title = canonical_title(installer_path, archive_titles)
            unwrap_destination = (args.unwrapped_root.resolve() / title) if args.unwrap else None
            extract_and_optionally_unwrap(
                installer_path,
                output_root,
                force=args.force,
                skip_existing=args.skip_existing,
                archive_titles=archive_titles,
                unwrap_after=args.unwrap,
                keep_extracted=args.keep_extracted,
                unwrapped_output_root=unwrap_destination,
            )
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
