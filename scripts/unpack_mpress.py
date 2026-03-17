from __future__ import annotations

import argparse
import os
import struct
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DUMPER_SOURCE = REPO_ROOT / "scripts" / "mpress_memory_dumper.c"
DUMPER_EXE = Path(tempfile.gettempdir()) / "reflexive_mpress_memory_dumper.exe"


def compile_dumper() -> Path:
    if DUMPER_EXE.exists() and DUMPER_EXE.stat().st_mtime >= DUMPER_SOURCE.stat().st_mtime:
        return DUMPER_EXE

    subprocess.run(
        [
            "i686-w64-mingw32-gcc",
            "-Os",
            "-s",
            "-o",
            str(DUMPER_EXE),
            str(DUMPER_SOURCE),
        ],
        check=True,
    )
    return DUMPER_EXE


def read_u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def read_u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def align(value: int, alignment: int) -> int:
    if alignment <= 1:
        return value
    return (value + alignment - 1) // alignment * alignment


def rebuild_pe_from_memory_image(memory_image: bytes, unpacked_oep_rva: int) -> bytes:
    if memory_image[:2] != b"MZ":
        raise ValueError("memory image is not a PE")

    pe_offset = read_u32(memory_image, 0x3C)
    if memory_image[pe_offset : pe_offset + 4] != b"PE\x00\x00":
        raise ValueError("memory image has invalid NT headers")

    file_header_offset = pe_offset + 4
    section_count = read_u16(memory_image, file_header_offset + 2)
    size_of_optional_header = read_u16(memory_image, file_header_offset + 16)
    optional_header_offset = file_header_offset + 20
    section_table_offset = optional_header_offset + size_of_optional_header
    size_of_headers = read_u32(memory_image, optional_header_offset + 60)
    file_alignment = read_u32(memory_image, optional_header_offset + 36)

    # Patch the OEP in the rebuilt file to the post-unpack destination.
    rebuilt_headers = bytearray(memory_image[:size_of_headers])
    struct.pack_into("<I", rebuilt_headers, optional_header_offset + 16, unpacked_oep_rva)

    sections: list[tuple[int, int, int, int, int]] = []
    next_raw_pointer = align(size_of_headers, file_alignment)
    output_size = next_raw_pointer
    for index in range(section_count):
        section_offset = section_table_offset + index * 40
        virtual_size = read_u32(memory_image, section_offset + 8)
        virtual_address = read_u32(memory_image, section_offset + 12)
        copy_size = virtual_size or read_u32(memory_image, section_offset + 16)
        raw_size = align(copy_size, file_alignment)
        pointer_to_raw_data = next_raw_pointer
        struct.pack_into("<I", rebuilt_headers, section_offset + 16, raw_size)
        struct.pack_into("<I", rebuilt_headers, section_offset + 20, pointer_to_raw_data)
        sections.append((virtual_address, copy_size, raw_size, pointer_to_raw_data, section_offset))
        next_raw_pointer += raw_size
        output_size = max(output_size, pointer_to_raw_data + raw_size)

    rebuilt = bytearray(output_size)
    rebuilt[:size_of_headers] = rebuilt_headers
    for virtual_address, copy_size, raw_size, pointer_to_raw_data, section_offset in sections:
        src_start = virtual_address
        src_end = min(len(memory_image), src_start + copy_size)
        if src_start >= len(memory_image) or src_end <= src_start:
            continue
        rebuilt[pointer_to_raw_data : pointer_to_raw_data + (src_end - src_start)] = memory_image[src_start:src_end]

    return bytes(rebuilt)


def dump_unpacked_image(packed_path: Path, break_va: int, unpacked_oep_va: int, output_path: Path) -> None:
    dumper = compile_dumper()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="mpress_dump_") as tmpdir:
        memdump_path = Path(tmpdir) / "memory_image.bin"
        env = dict(os.environ)
        env.setdefault("WINEDEBUG", "-all")
        subprocess.run(
            [
                "wine",
                str(dumper),
                str(packed_path),
                f"{break_va:08x}",
                str(memdump_path),
            ],
            check=True,
            env=env,
        )
        memory_image = memdump_path.read_bytes()

    image_base = read_u32(memory_image, read_u32(memory_image, 0x3C) + 4 + 20 + 28)
    unpacked_oep_rva = unpacked_oep_va - image_base
    rebuilt = rebuild_pe_from_memory_image(memory_image, unpacked_oep_rva)
    output_path.write_bytes(rebuilt)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dump and rebuild an MPRESS-packed PE after the unpack stub runs.")
    parser.add_argument("packed_exe", type=Path)
    parser.add_argument("unpacked_oep_va", help="real unpacked entrypoint virtual address, e.g. 0x4033a8")
    parser.add_argument(
        "--break-va",
        help="breakpoint virtual address to dump from; defaults to the unpacked OEP, but MPRESS often needs the final stub jump instead",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="output path for the rebuilt PE (defaults next to the input as *.unpacked.exe)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packed_path = args.packed_exe.resolve()
    unpacked_oep_va = int(args.unpacked_oep_va, 0)
    break_va = int(args.break_va, 0) if args.break_va else unpacked_oep_va
    output_path = args.output or packed_path.with_suffix(".unpacked.exe")
    dump_unpacked_image(packed_path, break_va, unpacked_oep_va, output_path)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
