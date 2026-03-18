#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pefile"]
# ///

from __future__ import annotations

import argparse
import errno
import mmap
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from source_layout import extracted_root as source_extracted_root
from source_layout import infer_source_id_from_installer_path
from source_layout import source_root as source_source_root
from source_layout import unwrapped_root as source_unwrapped_root
from unwrap_installer_tree import unwrap_extracted_tree


SMART_INSTALL_MAKER_SIGNATURE = b"Smart Install Maker v"
CAB_HEADER_STRUCT = struct.Struct("<4sIIIII BB HHHHH")
DISK_NAME_RE = re.compile(r"_Disk(\d+)\.cab$")
ARCHIVE_INSTALLER_GLOB = "Reflexive Arcade *.exe"
TOKEN_REPLACEMENTS = {
    "@$&%01": "%PROGRAMFILES%",
    "@$&%02": "%WINDOWSDIR%",
    "@$&%03": "%SYSTEMDIR%",
    "@$&%04": "",
    "@$&%05": "%TEMPDIR%",
    "@$&%06": "%DESKTOP%",
    "@$&%07": "%QUICKLAUNCH%",
    "@$&%08": "%PROGRAMSDIR%",
    "@$&%09": "%STARTMENU%",
    "@$&%10": "%MYDOCUMENTS%",
    "@$&%11": "%FAVORITES%",
    "@$&%12": "%SENDTO%",
    "@$&%13": "%USERPROFILE%",
    "@$&%14": "%STARTUP%",
    "@$&%15": "%FONTDIR%",
    "@$&%16": "%COMMONFILES%",
    "@$&%17": "%SYSTEMDRIVE%",
    "@$&%18": "%CURRENTDIR%",
}
LAUNCHER_PATCH_OLD = bytes.fromhex("84c0740e8bce")
LAUNCHER_PATCH_NEW = bytes.fromhex("84c090908bce")


@dataclass(frozen=True)
class InstallerMetadata:
    path: Path
    version: str
    file_names: tuple[str, ...]
    one_volume: bool
    data_offset: int
    compressed: bool


def read_c_string(data: mmap.mmap, offset: int) -> tuple[str, int]:
    end = data.find(b"\x00", offset)
    if end == -1:
        raise ValueError(f"unterminated string at offset {offset}")
    return bytes(data[offset:end]).decode("latin1"), end + 1


def normalize_installer_path(raw_name: str) -> str:
    value = raw_name
    for token, replacement in TOKEN_REPLACEMENTS.items():
        value = value.replace(token, replacement)

    value = value.replace("\\", "/")
    if value.startswith("/"):
        value = value[1:]

    parts = [part for part in value.split("/") if part not in {"", "."}]
    if any(part == ".." for part in parts):
        raise ValueError(f"unsafe installer path: {raw_name!r}")
    if not parts:
        raise ValueError(f"empty installer path: {raw_name!r}")
    return "/".join(parts)


def find_name_table_offset(data: mmap.mmap, offset: int) -> int:
    while offset < len(data):
        candidate_offset = offset
        value, offset = read_c_string(data, offset)
        if "@$&%19" in value:
            continue
        if "@$&%" not in value:
            continue

        probe_offset = offset
        _, probe_offset = read_c_string(data, probe_offset)
        third_value, _ = read_c_string(data, probe_offset)
        if third_value:
            return candidate_offset

    raise ValueError("could not locate installer name table")


def parse_cab_header(cab_bytes: bytes) -> dict[str, int]:
    if len(cab_bytes) < CAB_HEADER_STRUCT.size:
        raise ValueError("cabinet is too small to contain a valid header")

    (
        signature,
        reserved1,
        cb_cabinet,
        reserved2,
        coff_files,
        reserved3,
        version_minor,
        version_major,
        c_folders,
        c_files,
        flags,
        set_id,
        i_cabinet,
    ) = CAB_HEADER_STRUCT.unpack_from(cab_bytes)

    if signature != b"MSCF":
        raise ValueError("cabinet signature mismatch")
    if reserved1 != 0 or reserved2 != 0 or reserved3 != 0:
        raise ValueError("cabinet reserved fields are not zero")
    if cb_cabinet > len(cab_bytes):
        raise ValueError("cabinet header size exceeds reconstructed file size")
    if coff_files >= len(cab_bytes):
        raise ValueError("cabinet file table offset is out of range")
    if version_major != 1 or version_minor != 3:
        raise ValueError("unexpected cabinet version")

    return {
        "cb_cabinet": cb_cabinet,
        "coff_files": coff_files,
        "c_folders": c_folders,
        "c_files": c_files,
        "flags": flags,
        "set_id": set_id,
        "i_cabinet": i_cabinet,
    }


def build_cabinet(data: mmap.mmap, offset: int) -> tuple[bytes, int, dict[str, int]]:
    if offset + 8 > len(data):
        raise ValueError(f"cabinet offset {offset} is out of range")

    _dummy, cab_size = struct.unpack_from("<II", data, offset)
    if cab_size < 4:
        raise ValueError(f"invalid cabinet size {cab_size} at offset {offset}")

    payload_length = cab_size - 4
    end = offset + payload_length
    if end > len(data):
        raise ValueError(f"cabinet at offset {offset} overruns installer data")

    cab_bytes = b"MSCF" + bytes(data[offset:end])
    header = parse_cab_header(cab_bytes)
    return cab_bytes, cab_size, header


def direct_payload_plausible(data: mmap.mmap, offset: int) -> bool:
    if offset + 24 > len(data):
        return False

    _dummy, size = struct.unpack_from("<II", data, offset)
    if size < 0:
        return False
    return offset + 8 + 0x10 + size <= len(data)


def resolve_payload_layout(data: mmap.mmap) -> tuple[int, bool]:
    candidates: list[tuple[int, bool]] = []

    if len(data) >= 0x24:
        _info_offset, _inst_size, _inst_offset, offset, raw_type = struct.unpack_from(
            "<QQQQI", data, len(data) - 0x24
        )
        candidates.append((offset, bool(raw_type & 1)))

    if len(data) >= 0x22:
        _info_offset, _inst_size, _inst_offset, offset = struct.unpack_from(
            "<QQQQ", data, len(data) - 0x22
        )
        candidates.append((offset, True))

    for offset, compressed in candidates:
        try:
            if compressed:
                build_cabinet(data, offset)
                return offset, True
            if direct_payload_plausible(data, offset):
                return offset, False
        except ValueError:
            continue

    raise ValueError("could not resolve Smart Install Maker payload layout")


def parse_installer_metadata(installer_path: Path) -> InstallerMetadata:
    with installer_path.open("rb") as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as data:
        signature_offset = data.find(SMART_INSTALL_MAKER_SIGNATURE)
        if signature_offset == -1:
            raise ValueError(f"Smart Install Maker signature not found in {installer_path}")

        version, offset = read_c_string(data, signature_offset)

        fields: list[str] = []
        for _ in range(120):
            field, offset = read_c_string(data, offset)
            fields.append(field)

        files_count = int(fields[66])
        one_volume = fields[33] != "0"
        offset = find_name_table_offset(data, offset)

        file_names: list[str] = []
        for _ in range(files_count):
            raw_name, offset = read_c_string(data, offset)
            file_names.append(normalize_installer_path(raw_name))
            _, offset = read_c_string(data, offset)
            _, offset = read_c_string(data, offset)

        data_offset, compressed = resolve_payload_layout(data)

    return InstallerMetadata(
        path=installer_path,
        version=version,
        file_names=tuple(file_names),
        one_volume=one_volume,
        data_offset=data_offset,
        compressed=compressed,
    )


def require_command(name: str) -> str:
    resolved = shutil.which(name)
    if resolved is None:
        raise FileNotFoundError(f"missing required command: {name}")
    return resolved


def format_bytes(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    size = float(value)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TiB"


def run_command(command: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(command))
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            command,
            output=completed.stdout,
            stderr=completed.stderr,
        )


def is_no_space_left_error(exc: subprocess.CalledProcessError) -> bool:
    output = exc.output if isinstance(exc.output, str) else ""
    stderr = exc.stderr if isinstance(exc.stderr, str) else ""
    return "No space left on device" in f"{output}\n{stderr}"


def raise_no_space_left_error(
    installer_path: Path,
    temp_dir: Path,
    extractor_name: str,
) -> None:
    usage = shutil.disk_usage(temp_dir)
    raise ValueError(
        (
            f"{extractor_name} ran out of disk space while expanding {installer_path.name} in {temp_dir}. "
            "Temporary extraction workspaces are cleaned after each attempt, but compressed installers need "
            "enough scratch space for reconstructed CAB volumes and the numbered raw payload before the final "
            f"tree can be materialized. Free space on this filesystem: {format_bytes(usage.free)}."
        )
    )


def build_cab_extract_command(raw_payload_dir: Path) -> tuple[str, list[str], tuple[str, ...]]:
    cabextract = shutil.which("cabextract")
    if cabextract is not None:
        return (
            "cabextract",
            [cabextract, "-q", "-d", str(raw_payload_dir), "./0000.tmp"],
            ("hardlink", "copy"),
        )

    seven_zip = require_command("7z")
    return (
        "7z",
        [seven_zip, "x", "./0000.tmp", f"-o{raw_payload_dir}", "-y"],
        ("hardlink", "copy", "copy"),
    )


def reconstruct_raw_cabs(metadata: InstallerMetadata, raw_cabs_dir: Path) -> int:
    if not metadata.one_volume:
        raise ValueError("external Smart Install Maker volumes are not supported")

    count = 0
    with metadata.path.open("rb") as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as data:
        offset = metadata.data_offset
        while True:
            cab_bytes, cab_size, header = build_cabinet(data, offset)
            count += 1

            if header["flags"] & 3:
                cab_name = f"{metadata.path.stem}_Disk{count}.cab"
            else:
                cab_name = f"{metadata.path.stem}.cab"

            (raw_cabs_dir / cab_name).write_bytes(cab_bytes)
            offset += cab_size - 4

            if not (header["flags"] & 2):
                break

    return count


def extract_uncompressed_payload(metadata: InstallerMetadata, raw_payload_dir: Path) -> None:
    with metadata.path.open("rb") as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as data:
        offset = metadata.data_offset
        for index in range(len(metadata.file_names)):
            if offset + 24 > len(data):
                raise ValueError("unexpected end of installer while extracting uncompressed payload")

            _dummy, size = struct.unpack_from("<II", data, offset)
            offset += 8 + 0x10
            end = offset + size
            if end > len(data):
                raise ValueError("uncompressed payload entry overruns installer data")

            (raw_payload_dir / str(index)).write_bytes(bytes(data[offset:end]))
            offset = end


def sorted_cab_files(raw_cabs_dir: Path, installer_stem: str) -> list[Path]:
    cabs = list(raw_cabs_dir.glob(f"{installer_stem}_Disk*.cab"))
    if not cabs:
        single_cab = raw_cabs_dir / f"{installer_stem}.cab"
        if single_cab.is_file():
            return [single_cab]
        raise FileNotFoundError(f"no reconstructed CABs found in {raw_cabs_dir}")

    def disk_number(path: Path) -> int:
        match = DISK_NAME_RE.search(path.name)
        if match is None:
            raise ValueError(f"unexpected CAB name: {path.name}")
        return int(match.group(1))

    return sorted(cabs, key=disk_number)


def create_volume_aliases(raw_cabs_dir: Path, installer_stem: str, *, mode: str = "hardlink") -> None:
    for index, cab_path in enumerate(sorted_cab_files(raw_cabs_dir, installer_stem), start=1):
        alias_path = raw_cabs_dir / f"{index - 1:04d}.tmp"
        if alias_path.exists() or alias_path.is_symlink():
            alias_path.unlink()
        if mode == "copy":
            shutil.copy2(cab_path, alias_path)
            continue
        try:
            os.link(cab_path, alias_path)
        except OSError as exc:
            if exc.errno != errno.EXDEV:
                raise
            shutil.copy2(cab_path, alias_path)


def synthesize_patched_launcher(raw_payload_dir: Path, source_index: int) -> Path | None:
    source = raw_payload_dir / str(source_index)
    if not source.is_file():
        return None

    original = source.read_bytes()
    hits = [offset for offset in range(len(original) - len(LAUNCHER_PATCH_OLD) + 1) if original[offset : offset + len(LAUNCHER_PATCH_OLD)] == LAUNCHER_PATCH_OLD]
    if len(hits) != 1:
        return None

    offset = hits[0]
    patched = source.with_name(f".synthesized-{source_index}")
    patched.write_bytes(
        original[:offset] + LAUNCHER_PATCH_NEW + original[offset + len(LAUNCHER_PATCH_OLD) :]
    )
    return patched


def resolve_materialized_source(
    file_names: tuple[str, ...],
    name_to_index: dict[str, int],
    raw_payload_dir: Path,
    index: int,
    relative_name: str,
) -> tuple[Path, str | None]:
    source = raw_payload_dir / str(index)
    if source.is_file():
        return source, None

    if relative_name.lower().endswith(".exe"):
        backup_index = name_to_index.get(f"{relative_name}.BAK")
        if backup_index is not None:
            synthesized = synthesize_patched_launcher(raw_payload_dir, backup_index)
            if synthesized is not None:
                return synthesized, f"synthesized from payload {backup_index} ({relative_name}.BAK)"

    raise FileNotFoundError(f"missing extracted payload file: {source}")


def materialize_payload(file_names: tuple[str, ...], raw_payload_dir: Path, destination_root: Path) -> None:
    name_to_index = {relative_name: index for index, relative_name in enumerate(file_names)}
    for index, relative_name in enumerate(file_names):
        source, note = resolve_materialized_source(file_names, name_to_index, raw_payload_dir, index, relative_name)

        destination = destination_root / relative_name
        destination.parent.mkdir(parents=True, exist_ok=True)

        if note is not None:
            print(f"Using fallback for {relative_name}: {note}")

        try:
            os.link(source, destination)
        except OSError as exc:
            if exc.errno not in {errno.EXDEV, errno.EPERM, errno.ENOTSUP}:
                raise
            shutil.copy2(source, destination)


def default_output_root(installer_path: Path) -> Path:
    source_id = infer_source_id_from_installer_path(installer_path)
    return source_extracted_root(source_id) / installer_path.stem


def default_batch_installers_root() -> Path:
    return source_source_root("archive")


def default_batch_unwrapped_root() -> Path:
    return source_unwrapped_root("archive")


def clear_output_root(output_root: Path, *, force: bool) -> None:
    if not output_root.exists():
        return

    if force:
        if output_root.is_dir():
            shutil.rmtree(output_root)
        else:
            output_root.unlink()
        return

    if not output_root.is_dir():
        raise FileExistsError(f"output root already exists and is not a directory: {output_root}")
    if any(output_root.iterdir()):
        raise FileExistsError(f"output root already exists and is not empty: {output_root}")


def cleanup_temp_dir(temp_dir: Path) -> None:
    for attempt_index in range(3):
        try:
            shutil.rmtree(temp_dir)
            return
        except FileNotFoundError:
            return
        except OSError as exc:
            if exc.errno != errno.ENOTEMPTY or attempt_index == 2:
                print(f"warning: failed to remove temporary directory {temp_dir}: {exc}", file=sys.stderr)
                return
            time.sleep(0.1 * (attempt_index + 1))


def extract_installer(installer_path: Path, output_root: Path, *, force: bool) -> Path:
    installer_path = installer_path.resolve()
    output_root = output_root.resolve()

    clear_output_root(output_root, force=force)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    metadata = parse_installer_metadata(installer_path)

    print(f"Installer: {installer_path}")
    print(f"Wrapper: {metadata.version}")
    print(f"Files: {len(metadata.file_names)}")
    print(f"Compressed payload: {'yes' if metadata.compressed else 'no'}")
    print(f"Output root: {output_root}")

    safe_prefix = re.sub(r"[^A-Za-z0-9._-]+", "-", installer_path.stem).strip("-") or "reflexive"

    if metadata.compressed:
        last_error: subprocess.CalledProcessError | None = None
        max_attempts = 3

        for attempt_index in range(1, max_attempts + 1):
            temp_dir = Path(tempfile.mkdtemp(dir=output_root.parent, prefix=f".{safe_prefix}.tmp."))
            try:
                raw_payload_dir = temp_dir / "raw_payload"
                raw_payload_dir.mkdir()
                raw_cabs_dir = temp_dir / "raw_cabs"
                raw_cabs_dir.mkdir()
                extractor_name, extract_command, alias_modes = build_cab_extract_command(raw_payload_dir)
                alias_mode = alias_modes[min(attempt_index - 1, len(alias_modes) - 1)]

                print(
                    f"Rebuilding raw CAB volumes from installer (attempt {attempt_index}/{max_attempts})"
                )
                cab_count = reconstruct_raw_cabs(metadata, raw_cabs_dir)
                print(f"Rebuilt {cab_count} CAB volumes")

                print(f"Creating numbered CAB volume aliases ({alias_mode})")
                create_volume_aliases(raw_cabs_dir, installer_path.stem, mode=alias_mode)

                if attempt_index > 1:
                    time.sleep(attempt_index - 1)

                print(f"Extracting numbered payload with {extractor_name}")
                try:
                    run_command(extract_command, cwd=raw_cabs_dir)
                except subprocess.CalledProcessError as exc:
                    if is_no_space_left_error(exc):
                        raise_no_space_left_error(installer_path, temp_dir, extractor_name)
                    last_error = exc
                    if attempt_index == max_attempts:
                        break
                    print(
                        f"{extractor_name} extraction attempt {attempt_index} failed, retrying in a fresh workspace"
                    )
                    continue

                print("Materializing final payload tree")
                output_root.mkdir(parents=True, exist_ok=True)
                materialize_payload(metadata.file_names, raw_payload_dir, output_root)
                print(f"Materialized payload written to {output_root}")
                return output_root
            finally:
                cleanup_temp_dir(temp_dir)

        if last_error is not None:
            raise last_error
        raise RuntimeError("compressed payload extraction failed without a captured subprocess error")
    else:
        temp_dir = Path(tempfile.mkdtemp(dir=output_root.parent, prefix=f".{safe_prefix}.tmp."))
        try:
            raw_payload_dir = temp_dir / "raw_payload"
            raw_payload_dir.mkdir()

            print("Extracting uncompressed numbered payload directly")
            extract_uncompressed_payload(metadata, raw_payload_dir)

            print("Materializing final payload tree")
            output_root.mkdir(parents=True, exist_ok=True)
            materialize_payload(metadata.file_names, raw_payload_dir, output_root)
        finally:
            cleanup_temp_dir(temp_dir)

    print(f"Materialized payload written to {output_root}")
    return output_root


def extract_and_optionally_unwrap(
    installer_path: Path,
    extracted_output_root: Path,
    *,
    force: bool,
    unwrap_after: bool,
    keep_extracted: bool,
    unwrapped_output_root: Path | None,
) -> None:
    installer_path = installer_path.resolve()
    extracted_output_root = extracted_output_root.resolve()
    final_unwrapped_root = None if unwrapped_output_root is None else unwrapped_output_root.resolve()

    if not unwrap_after:
        extract_installer(installer_path, extracted_output_root, force=force)
        return

    if final_unwrapped_root is None:
        raise ValueError("unwrap destination is required when --unwrap is enabled")

    if keep_extracted:
        extracted_tree = extract_installer(installer_path, extracted_output_root, force=force)
        unwrap_result = unwrap_extracted_tree(extracted_tree, final_unwrapped_root, force=force)
    else:
        temp_parent = final_unwrapped_root.parent
        temp_parent.mkdir(parents=True, exist_ok=True)
        safe_prefix = re.sub(r"[^A-Za-z0-9._-]+", "-", installer_path.stem).strip("-") or "reflexive"
        temp_dir = Path(tempfile.mkdtemp(prefix=f".{safe_prefix}.unwrap.", dir=temp_parent))
        try:
            temp_extract_root = temp_dir / installer_path.stem
            extracted_tree = extract_installer(installer_path, temp_extract_root, force=True)
            unwrap_result = unwrap_extracted_tree(extracted_tree, final_unwrapped_root, force=force)
        finally:
            cleanup_temp_dir(temp_dir)

    print(f"Unwrapped root: {final_unwrapped_root}")
    print(f"Materialized wrapper roots: {len(unwrap_result.ok_roots)}")
    if unwrap_result.unsupported_roots:
        print("Unsupported wrapper roots:")
        for root in unwrap_result.unsupported_roots:
            print(f"  - {root}")
        if not keep_extracted:
            print("Rerun with --keep-extracted to retain the extracted tree for inspection.")


def collect_batch_installers(installers_root: Path) -> list[Path]:
    if not installers_root.is_dir():
        raise FileNotFoundError(f"archive directory does not exist: {installers_root}")

    installers = sorted(path for path in installers_root.glob(ARCHIVE_INSTALLER_GLOB) if path.is_file())
    if not installers:
        raise FileNotFoundError(
            f"no Smart Install Maker installers matching {ARCHIVE_INSTALLER_GLOB!r} found in {installers_root}"
        )
    return installers


def extract_all_installers(
    installers_root: Path,
    output_root: Path,
    *,
    force: bool,
    unwrap_after: bool,
    keep_extracted: bool,
    unwrapped_root: Path | None,
) -> int:
    installers_root = installers_root.resolve()
    output_root = output_root.resolve()
    installers = collect_batch_installers(installers_root)
    output_root.mkdir(parents=True, exist_ok=True)

    print(f"Archive directory: {installers_root}")
    print(f"Output root: {output_root}")
    print(f"Installers: {len(installers)}")
    if unwrap_after and unwrapped_root is not None:
        print(f"Unwrapped root: {unwrapped_root.resolve()}")

    for installer_path in installers:
        destination = output_root / installer_path.stem
        print(f"\n[{time.strftime('%H:%M:%S')}] {installer_path.stem}")
        unwrap_destination = None if unwrapped_root is None else unwrapped_root / installer_path.stem
        extract_and_optionally_unwrap(
            installer_path,
            destination,
            force=force,
            unwrap_after=unwrap_after,
            keep_extracted=keep_extracted,
            unwrapped_output_root=unwrap_destination,
        )

    return len(installers)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract the unofficial Reflexive Arcade Games Collection repack "
            "installers into final payload trees without keeping intermediate "
            "CAB/raw directories."
        )
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        type=Path,
        help=(
            "Single mode: path to the Smart Install Maker installer EXE. "
            "Batch mode (--all): directory containing the archive installer set."
        ),
    )
    parser.add_argument(
        "output_root",
        nargs="?",
        type=Path,
        help=(
            "Single mode: directory that will receive the extracted files directly. "
            "Defaults to artifacts/extracted/<source_id>/<installer stem>. "
            "Batch mode (--all): extracted root that will receive one directory per installer."
        ),
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help=(
            "Extract every archive installer matching "
            f"{ARCHIVE_INSTALLER_GLOB!r}. Defaults to artifacts/sources/archive."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove an existing output root before extracting.",
    )
    parser.add_argument(
        "--unwrap",
        action="store_true",
        help=(
            "After extraction, materialize wrapper-free outputs under artifacts/unwrapped/archive "
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
        default=default_batch_unwrapped_root(),
        help=(
            "Single mode: destination directory for the wrapper-free tree when --unwrap is enabled. "
            "Batch mode (--all): root that will receive one wrapper-free directory per installer."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.keep_extracted and not args.unwrap:
        print("error: --keep-extracted requires --unwrap", file=sys.stderr)
        return 1

    try:
        if args.all:
            installers_root = (
                args.input_path.resolve() if args.input_path else default_batch_installers_root().resolve()
            )
            if installers_root.is_file():
                raise ValueError(f"expected an archive directory for --all, got file: {installers_root}")
            output_root = args.output_root.resolve() if args.output_root else source_extracted_root("archive")
            extract_all_installers(
                installers_root,
                output_root,
                force=args.force,
                unwrap_after=args.unwrap,
                keep_extracted=args.keep_extracted,
                unwrapped_root=args.unwrapped_root.resolve() if args.unwrap else None,
            )
        else:
            if args.input_path is None:
                raise ValueError("missing installer path; pass an installer EXE or use --all")
            installer_path = args.input_path.resolve()
            if installer_path.is_dir():
                raise ValueError(f"expected an installer EXE, got directory: {installer_path}")
            output_root = args.output_root.resolve() if args.output_root else default_output_root(installer_path)
            unwrap_destination = (args.unwrapped_root.resolve() / installer_path.stem) if args.unwrap else None
            extract_and_optionally_unwrap(
                installer_path,
                output_root,
                force=args.force,
                unwrap_after=args.unwrap,
                keep_extracted=args.keep_extracted,
                unwrapped_output_root=unwrap_destination,
            )
    except (FileNotFoundError, FileExistsError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
