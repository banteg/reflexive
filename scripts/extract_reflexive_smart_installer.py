#!/usr/bin/env -S uv run --script
# /// script
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
from dataclasses import dataclass
from pathlib import Path


SMART_INSTALL_MAKER_SIGNATURE = b"Smart Install Maker v"
CAB_HEADER_STRUCT = struct.Struct("<4sIIIII BB HHHHH")
DISK_NAME_RE = re.compile(r"_Disk(\d+)\.cab$")
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


def run_command(command: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


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


def create_volume_aliases(raw_cabs_dir: Path, installer_stem: str) -> None:
    for index, cab_path in enumerate(sorted_cab_files(raw_cabs_dir, installer_stem), start=1):
        for alias in (f"Disk{index}", f"{index - 1:04d}.tmp"):
            alias_path = raw_cabs_dir / alias
            if alias_path.exists() or alias_path.is_symlink():
                alias_path.unlink()
            try:
                os.link(cab_path, alias_path)
            except OSError as exc:
                if exc.errno != errno.EXDEV:
                    raise
                shutil.copy2(cab_path, alias_path)


def materialize_payload(file_names: tuple[str, ...], raw_payload_dir: Path, destination_root: Path) -> None:
    for index, relative_name in enumerate(file_names):
        source = raw_payload_dir / str(index)
        if not source.is_file():
            raise FileNotFoundError(f"missing extracted payload file: {source}")

        destination = destination_root / relative_name
        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            os.link(source, destination)
        except OSError as exc:
            if exc.errno not in {errno.EXDEV, errno.EPERM, errno.ENOTSUP}:
                raise
            shutil.copy2(source, destination)


def default_output_root(installer_path: Path) -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / "artifacts" / "extracted" / installer_path.stem


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

    with tempfile.TemporaryDirectory(dir=output_root.parent, prefix=f".{safe_prefix}.tmp.") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        raw_payload_dir = temp_dir / "raw_payload"
        raw_payload_dir.mkdir()

        if metadata.compressed:
            seven_zip = require_command("7z")
            raw_cabs_dir = temp_dir / "raw_cabs"
            raw_cabs_dir.mkdir()

            print("Rebuilding raw CAB volumes from installer")
            cab_count = reconstruct_raw_cabs(metadata, raw_cabs_dir)
            print(f"Rebuilt {cab_count} CAB volumes")

            print("Creating Smart Install Maker volume aliases")
            create_volume_aliases(raw_cabs_dir, installer_path.stem)

            print("Extracting numbered payload with 7z")
            run_command([seven_zip, "x", "./Disk1", f"-o{raw_payload_dir}", "-y"], cwd=raw_cabs_dir)
        else:
            print("Extracting uncompressed numbered payload directly")
            extract_uncompressed_payload(metadata, raw_payload_dir)

        print("Materializing final payload tree")
        output_root.mkdir(parents=True, exist_ok=True)
        materialize_payload(metadata.file_names, raw_payload_dir, output_root)

    print(f"Materialized payload written to {output_root}")
    return output_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract one of the unofficial Reflexive Arcade Games Collection repack "
            "installers into a final payload tree without keeping intermediate "
            "CAB/raw directories."
        )
    )
    parser.add_argument("installer", type=Path, help="Path to the Smart Install Maker installer EXE.")
    parser.add_argument(
        "output_root",
        nargs="?",
        type=Path,
        help=(
            "Directory that will receive the extracted files directly. "
            "Defaults to artifacts/extracted/<installer stem>."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove an existing output root before extracting.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    installer_path = args.installer.resolve()
    output_root = args.output_root.resolve() if args.output_root else default_output_root(installer_path)

    try:
        extract_installer(installer_path, output_root, force=args.force)
    except (FileNotFoundError, FileExistsError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
