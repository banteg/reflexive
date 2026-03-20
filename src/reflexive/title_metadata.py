from __future__ import annotations

import json
import re
import struct
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Mapping

import pefile

from . import unwrap, wrapper_versions
from .keygen import DEFAULT_LIST_PATH, load_entries


APP_ID_HEX_RE = re.compile(rb"[0-9A-Fa-f]{8}")
TITLE_SOURCE_PRIORITY = {
    "raw_002_config": 0,
    "embedded_app_id_list": 1,
    "directory_name": 9,
}


@dataclass(frozen=True)
class TitleResolution:
    title: str | None
    source: str | None


def clean_title(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned or None


def normalize_title_key(value: str) -> str:
    lowered = value.lower().removesuffix("setup.exe").removesuffix(".exe")
    lowered = lowered.replace("&", "and")
    return "".join(ch for ch in lowered if ch.isalnum())


@lru_cache(maxsize=1)
def load_default_entries_by_id() -> dict[int, object]:
    return load_entries(DEFAULT_LIST_PATH)


def parse_export_rva(pe: pefile.PE, export_name: str) -> int | None:
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
    directory = getattr(pe, "DIRECTORY_ENTRY_EXPORT", None)
    if directory is None:
        return None
    target = export_name.encode("ascii")
    for symbol in directory.symbols:
        if symbol.name == target:
            return symbol.address
    return None


def follow_unconditional_jumps(pe: pefile.PE, data: bytes, rva: int, max_hops: int = 8) -> int:
    current = rva
    for _ in range(max_hops):
        offset = pe.get_offset_from_rva(current)
        opcode = data[offset]
        if opcode == 0xE9 and offset + 5 <= len(data):
            displacement = struct.unpack_from("<i", data, offset + 1)[0]
            current = current + 5 + displacement
            continue
        if opcode == 0xEB and offset + 2 <= len(data):
            displacement = struct.unpack_from("<b", data, offset + 1)[0]
            current = current + 2 + displacement
            continue
        break
    return current


def va_to_offset(pe: pefile.PE, va: int) -> int:
    rva = va - pe.OPTIONAL_HEADER.ImageBase
    if rva < 0:
        raise pefile.PEFormatError(f"virtual address before image base: 0x{va:X}")
    return pe.get_offset_from_rva(rva)


def read_c_string(data: bytes, offset: int) -> bytes:
    end = data.find(b"\x00", offset)
    if end == -1:
        end = len(data)
    return data[offset:end]


def extract_app_id(path: Path) -> tuple[int | None, list[str]]:
    errors: list[str] = []
    data = path.read_bytes()
    try:
        pe = pefile.PE(data=data, fast_load=True)
    except pefile.PEFormatError as exc:
        return None, [f"invalid PE: {exc}"]
    rva = parse_export_rva(pe, "unittest_GetBrandedApplicationID")
    if rva is None:
        return None, ["missing unittest_GetBrandedApplicationID export"]

    target_rva = follow_unconditional_jumps(pe, data, rva)
    offset = pe.get_offset_from_rva(target_rva)
    window = data[offset : offset + 0x30]
    for index in range(max(0, len(window) - 5)):
        if window[index] != 0x68:
            continue
        string_va = struct.unpack_from("<I", window, index + 1)[0]
        try:
            string_offset = va_to_offset(pe, string_va)
        except pefile.PEFormatError:
            continue
        candidate = read_c_string(data, string_offset)
        if APP_ID_HEX_RE.fullmatch(candidate):
            return int(candidate.decode("ascii"), 16), errors

    return None, ["could not locate pushed branded application id string"]


def _title_from_static_wrapper(record: dict[str, object], wrapper_root: Path) -> TitleResolution:
    try:
        strategy = unwrap.choose_strategy(record, wrapper_root)
    except Exception:
        return TitleResolution(None, None)

    if strategy.kind != "static" or strategy.child_payload is None or strategy.config_path is None:
        return TitleResolution(None, None)

    try:
        seed = unwrap.derive_seed_material(
            strategy.config_path,
            strategy.child_payload,
            wrapper_root,
            strategy.wrapper_binary,
        )
        config = unwrap.parse_config(seed.decrypted_config)
    except Exception:
        return TitleResolution(None, None)

    title = clean_title(config.get("Application Name"))
    if title is None:
        return TitleResolution(None, None)
    return TitleResolution(title, "raw_002_config")


def _title_from_embedded_app_id(
    wrapper_root: Path,
    entries_by_id: Mapping[int, object],
) -> TitleResolution:
    support_dll = wrapper_root / "ReflexiveArcade" / "ReflexiveArcade.dll"
    if not support_dll.is_file():
        return TitleResolution(None, None)

    app_id, _ = extract_app_id(support_dll)
    if app_id is None:
        return TitleResolution(None, None)

    entry = entries_by_id.get(app_id)
    title = clean_title(getattr(entry, "name", None)) if entry is not None else None
    if title is None:
        return TitleResolution(None, None)
    return TitleResolution(title, "embedded_app_id_list")


def resolve_title_for_wrapper_root(
    wrapper_root: Path,
    *,
    entries_by_id: Mapping[int, object] | None = None,
    fallback_title: str | None = None,
) -> TitleResolution:
    resolved_root = wrapper_root.resolve()
    entries = load_default_entries_by_id() if entries_by_id is None else entries_by_id

    try:
        record = wrapper_versions.build_record(resolved_root, resolved_root.parent)
    except Exception:
        record = None

    if record is not None:
        resolution = _title_from_static_wrapper(record, resolved_root)
        if resolution.title is not None:
            return resolution

    resolution = _title_from_embedded_app_id(resolved_root, entries)
    if resolution.title is not None:
        return resolution

    title = clean_title(fallback_title)
    if title is None:
        return TitleResolution(None, None)
    return TitleResolution(title, "directory_name")


def resolve_title_for_extracted_tree(
    extracted_root: Path,
    *,
    entries_by_id: Mapping[int, object] | None = None,
    fallback_title: str | None = None,
) -> TitleResolution:
    resolved_root = extracted_root.resolve()
    candidates: defaultdict[str, list[str]] = defaultdict(list)

    for wrapper_root in wrapper_versions.discover_wrapper_roots(resolved_root):
        resolution = resolve_title_for_wrapper_root(wrapper_root, entries_by_id=entries_by_id)
        if resolution.title is not None and resolution.source is not None:
            candidates[resolution.source].append(resolution.title)

    if not candidates:
        title = clean_title(fallback_title)
        if title is None:
            return TitleResolution(None, None)
        return TitleResolution(title, "directory_name")

    source, names = min(
        candidates.items(),
        key=lambda item: (
            TITLE_SOURCE_PRIORITY[item[0]],
            -Counter(item[1]).most_common(1)[0][1],
            item[1][0].casefold(),
        ),
    )
    counts = Counter(names)
    title = sorted(counts, key=lambda value: (-counts[value], value.casefold()))[0]
    return TitleResolution(title, source)


def load_titles_from_key_inventory(path: Path) -> dict[str, str]:
    report = json.loads(path.read_text(encoding="utf-8"))
    extracted_root = Path(report["extracted_root"]).resolve()
    titles: dict[str, str] = {}

    for record in report["records"]:
        dll_path = record.get("dll_path")
        game_name_guess = clean_title(record.get("game_name_guess"))
        if not isinstance(dll_path, str) or game_name_guess is None:
            continue
        try:
            relative = Path(dll_path).resolve().relative_to(extracted_root)
        except ValueError:
            continue
        if not relative.parts:
            continue
        titles[normalize_title_key(relative.parts[0])] = game_name_guess

    return titles
