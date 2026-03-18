#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["capstone", "pefile"]
# ///

from __future__ import annotations

import argparse
import re
import shutil
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from capstone.x86_const import X86_OP_IMM


BUILD_RE = re.compile(rb"Build\s+(\d{2,4})\x00")
IMAGE_SCN_MEM_EXECUTE = 0x20000000
TARGET_NAMES = (
    "radll_HasTheProductBeenPurchased",
    "radll_GetUnlockCode",
)
OEP_STUB = b"\x33\xC0\x40\xC3"
MOV_EAX_STUB_TEMPLATE = b"\xB8" + (b"\x00" * 4) + (b"\x90" * 10)
MOV_EAX_RET_NULL = bytes.fromhex("b801000000c300")
CRC_HELPER_SIG = bytes.fromhex("8b442404f7d0")
ZERO_BLOCK_SIZE = 0x32
ZERO_CHECK_OFFSETS = (0x00, 0x0A, 0x14, 0x1E)
OEP_CODE_CAVE_START_RVA = 0x20010
OEP_CODE_CAVE_STEP = 0x10
OEP_PATCH_LEN = 15
MAX_SUPPORTED_OEP_BUILD = 173


@dataclass(frozen=True)
class PatchSite:
    symbol_name: str
    string_va: int
    patch_va: int
    patch_offset: int


@dataclass(frozen=True)
class ExecutableAnalysis:
    path: Path
    builds: tuple[int, ...]
    oep_sites: tuple[PatchSite, ...]
    cave_va: int | None
    cave_offset: int | None
    has_crc_markers: bool
    oep_error: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Patch supported Reflexive Arcade wrapper executables without using the original GUI patcher."
    )
    parser.add_argument("path", type=Path, help="Wrapper executable to patch.")
    parser.add_argument(
        "--mode",
        choices=("auto", "oep", "crc"),
        default="auto",
        help="Patch mode. 'auto' selects the supported family when it can be identified.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the patched executable to a separate path instead of modifying the input in place.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create '<path>.bak' before in-place patching.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing output or backup file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the detected patch plan without writing any files.",
    )
    return parser.parse_args()


def absolutize(path: Path) -> Path:
    expanded = path.expanduser()
    if expanded.is_absolute():
        return expanded
    return Path.cwd() / expanded


def load_pe(path: Path) -> pefile.PE:
    return pefile.PE(str(path), fast_load=False)


def find_builds(data: bytes) -> tuple[int, ...]:
    return tuple(sorted({int(match.group(1)) for match in BUILD_RE.finditer(data)}))


def va_to_offset(pe: pefile.PE, va: int) -> int:
    image_base = int(pe.OPTIONAL_HEADER.ImageBase)
    rva = va - image_base
    return int(pe.get_offset_from_rva(rva))


def iter_exec_section_instructions(pe: pefile.PE, data: bytes):
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    image_base = int(pe.OPTIONAL_HEADER.ImageBase)

    for section in pe.sections:
        if not (int(section.Characteristics) & IMAGE_SCN_MEM_EXECUTE):
            continue
        raw_offset = int(section.PointerToRawData)
        raw_size = int(section.SizeOfRawData)
        if raw_size <= 0:
            continue
        section_data = data[raw_offset : raw_offset + raw_size]
        section_va = image_base + int(section.VirtualAddress)
        for instruction in md.disasm(section_data, section_va):
            yield instruction


def find_string_vas(pe: pefile.PE, data: bytes, text: str) -> tuple[int, ...]:
    needle = text.encode("ascii") + b"\x00"
    image_base = int(pe.OPTIONAL_HEADER.ImageBase)
    offsets: list[int] = []
    start = 0
    while True:
        offset = data.find(needle, start)
        if offset < 0:
            break
        offsets.append(offset)
        start = offset + 1
    return tuple(image_base + int(pe.get_rva_from_offset(offset)) for offset in offsets)


def is_eax_test_or_compare(instruction) -> bool:
    if instruction.mnemonic in {"test", "or"} and instruction.op_str == "eax, eax":
        return True
    if instruction.mnemonic == "cmp" and instruction.op_str in {"eax, 0", "eax, 0x0"}:
        return True
    return False


def match_oep_stub_window(instructions: list, start_index: int) -> int | None:
    start_address = instructions[start_index].address
    saw_call = False

    for index in range(start_index + 1, min(len(instructions), start_index + 8)):
        instruction = instructions[index]
        span = (instruction.address + instruction.size) - start_address

        if instruction.mnemonic in {"jmp", "je", "jne", "ret", "retn"}:
            return None

        if instruction.mnemonic == "call":
            if saw_call:
                return None
            saw_call = True
            continue

        if saw_call:
            if not is_eax_test_or_compare(instruction):
                return None
            return span if span == OEP_PATCH_LEN else None

        if span > OEP_PATCH_LEN:
            return None

    return None


def find_oep_patch_site(pe: pefile.PE, data: bytes, symbol_name: str) -> PatchSite:
    string_vas = set(find_string_vas(pe, data, symbol_name))
    if not string_vas:
        raise ValueError(f"could not find the '{symbol_name}' string in the executable")

    instructions = list(iter_exec_section_instructions(pe, data))
    candidates: list[PatchSite] = []

    for index, instruction in enumerate(instructions):
        if instruction.mnemonic != "push" or not instruction.operands:
            continue
        operand = instruction.operands[0]
        if operand.type != X86_OP_IMM or operand.imm not in string_vas:
            continue

        span = match_oep_stub_window(instructions, index)
        if span != OEP_PATCH_LEN:
            continue

        patch_va = instruction.address
        patch_offset = va_to_offset(pe, patch_va)
        candidates.append(
            PatchSite(
                symbol_name=symbol_name,
                string_va=operand.imm,
                patch_va=patch_va,
                patch_offset=patch_offset,
            )
        )

    if not candidates:
        raise ValueError(
            f"did not find a supported 15-byte GetProcAddress stub for '{symbol_name}'"
        )
    if len(candidates) > 1:
        locations = ", ".join(hex(candidate.patch_va) for candidate in candidates)
        raise ValueError(f"found multiple candidate patch sites for '{symbol_name}': {locations}")
    return candidates[0]


def zero_block_matches(block: bytes) -> bool:
    if len(block) < ZERO_BLOCK_SIZE:
        return False
    return all(block[offset : offset + 4] == b"\x00\x00\x00\x00" for offset in ZERO_CHECK_OFFSETS)


def find_oep_code_cave(pe: pefile.PE, data: bytes) -> tuple[int, int] | tuple[None, None]:
    image_base = int(pe.OPTIONAL_HEADER.ImageBase)
    start_va = image_base + OEP_CODE_CAVE_START_RVA
    end_va = image_base + int(pe.OPTIONAL_HEADER.SizeOfImage) - ZERO_BLOCK_SIZE

    candidate_va = start_va
    while candidate_va <= end_va:
        try:
            candidate_offset = va_to_offset(pe, candidate_va)
        except pefile.PEFormatError:
            candidate_va += OEP_CODE_CAVE_STEP
            continue
        block = data[candidate_offset : candidate_offset + ZERO_BLOCK_SIZE]
        if zero_block_matches(block):
            return candidate_va, candidate_offset
        candidate_va += OEP_CODE_CAVE_STEP

    return None, None


def analyze_executable(path: Path) -> ExecutableAnalysis:
    data = path.read_bytes()
    pe = load_pe(path)
    try:
        builds = find_builds(data)
        oep_sites: tuple[PatchSite, ...] = ()
        oep_error: str | None = None
        try:
            oep_sites = tuple(find_oep_patch_site(pe, data, symbol_name) for symbol_name in TARGET_NAMES)
        except ValueError as exc:
            oep_error = str(exc)
        cave_va, cave_offset = find_oep_code_cave(pe, data)
        has_crc_markers = (
            data.find(MOV_EAX_RET_NULL) >= 0
            and data.find(CRC_HELPER_SIG) >= 0
        )
        return ExecutableAnalysis(
            path=path,
            builds=builds,
            oep_sites=oep_sites,
            cave_va=cave_va,
            cave_offset=cave_offset,
            has_crc_markers=has_crc_markers,
            oep_error=oep_error,
        )
    finally:
        pe.close()


def classify_mode(analysis: ExecutableAnalysis) -> str:
    if analysis.builds and min(analysis.builds) > MAX_SUPPORTED_OEP_BUILD:
        return "crc"
    if analysis.has_crc_markers and not analysis.builds:
        return "crc"
    if analysis.cave_va is not None and len(analysis.oep_sites) == len(TARGET_NAMES):
        return "oep"
    return "unknown"


def ensure_backup(path: Path, force: bool) -> Path:
    backup_path = path.with_name(path.name + ".bak")
    if backup_path.exists():
        if not force:
            raise FileExistsError(f"backup already exists: {backup_path}")
    shutil.copy2(path, backup_path)
    return backup_path


def patch_oep_family(path: Path, analysis: ExecutableAnalysis, output_path: Path | None, create_backup: bool, force: bool) -> Path:
    if analysis.cave_va is None or analysis.cave_offset is None:
        raise ValueError("could not find the OEP code cave used by the original patcher")
    if len(analysis.oep_sites) != len(TARGET_NAMES):
        detail = analysis.oep_error or "missing one or more limitation patch sites"
        raise ValueError(detail)

    patched = bytearray(path.read_bytes())
    patched[analysis.cave_offset : analysis.cave_offset + len(OEP_STUB)] = OEP_STUB

    resolver_stub = bytearray(MOV_EAX_STUB_TEMPLATE)
    struct.pack_into("<I", resolver_stub, 1, analysis.cave_va)
    for site in analysis.oep_sites:
        patched[site.patch_offset : site.patch_offset + OEP_PATCH_LEN] = resolver_stub

    destination = output_path or path
    if destination.exists() and destination != path and not force:
        raise FileExistsError(f"output already exists: {destination}")

    if output_path is None and create_backup:
        ensure_backup(path, force=force)

    destination.write_bytes(patched)
    return destination


def render_analysis(analysis: ExecutableAnalysis, requested_mode: str, selected_mode: str) -> str:
    lines = [
        f"target: {analysis.path}",
        f"requested_mode: {requested_mode}",
        f"selected_mode: {selected_mode}",
        f"builds: {list(analysis.builds)}",
        f"has_crc_markers: {analysis.has_crc_markers}",
        f"oep_code_cave_va: {hex(analysis.cave_va) if analysis.cave_va is not None else None}",
    ]
    if analysis.oep_error is not None:
        lines.append(f"oep_error: {analysis.oep_error}")
    for site in analysis.oep_sites:
        lines.append(
            f"{site.symbol_name}: patch_va={hex(site.patch_va)} string_va={hex(site.string_va)}"
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    path = absolutize(args.path)
    output_path = absolutize(args.output) if args.output is not None else None

    if not path.is_file():
        print(f"error: file does not exist: {path}", file=sys.stderr)
        return 1

    try:
        analysis = analyze_executable(path)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    auto_mode = classify_mode(analysis)
    selected_mode = auto_mode if args.mode == "auto" else args.mode

    if args.dry_run:
        print(render_analysis(analysis, args.mode, selected_mode))
        return 0

    if selected_mode == "crc":
        print(render_analysis(analysis, args.mode, selected_mode), file=sys.stderr)
        print(
            "error: CRC-family launcher patching is not implemented yet; the recovered repa6 logic still depends on a runtime-derived immediate.",
            file=sys.stderr,
        )
        return 1

    if selected_mode != "oep":
        print(render_analysis(analysis, args.mode, selected_mode), file=sys.stderr)
        print(
            "error: could not classify this executable as a supported OEP-family wrapper",
            file=sys.stderr,
        )
        return 1

    try:
        destination = patch_oep_family(
            path=path,
            analysis=analysis,
            output_path=output_path,
            create_backup=not args.no_backup,
            force=args.force,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(render_analysis(analysis, args.mode, selected_mode))
    print(f"patched: {destination}")
    if output_path is None and not args.no_backup:
        print(f"backup: {path.with_name(path.name + '.bak')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
