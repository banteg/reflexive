#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pefile"]
# ///

from __future__ import annotations

import argparse
import importlib.util
import itertools
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pefile


MASK32 = 0xFFFFFFFF
STATE_WORDS = 250
UTILITY_EXE_NAMES = {
    "controls.exe",
    "config.exe",
    "launcher.exe",
    "play.exe",
    "readme.exe",
    "setup.exe",
    "unins000.exe",
}
TOP_LEVEL_WRAPPER_JUNK = {
    "ra_games.png",
    "ra_trial_dialog.png",
    "wraperr.log",
}
TOP_LEVEL_WRAPPER_SIDECARS = {
    "background.jpg",
    "button_hover.jpg",
    "button_normal.jpg",
    "button_pressed.jpg",
    "channel.dat",
    "raw_002.dat",
    "raw_002.wdt",
    "raw_003.dat",
    "raw_003.wdt",
    "raw_004.dat",
    "raw_004.wdt",
}
RAW2_FILENAMES = ("RAW_002.wdt", "RAW_002.dat")
RAW1_FILENAMES = ("RAW_001.exe", "RAW_001.dat")
PRIMARY_SEED_DEPENDENCY_NAMES = {
    "background.jpg",
    "button_hover.jpg",
    "button_normal.jpg",
    "button_pressed.jpg",
    "raw_003.dat",
    "raw_003.wdt",
}
SECONDARY_SEED_DEPENDENCY_NAMES = PRIMARY_SEED_DEPENDENCY_NAMES | {
    "channel.dat",
    "raw_004.dat",
    "raw_004.wdt",
}


@dataclass(frozen=True)
class Strategy:
    kind: str
    reason: str
    wrapper_binary: Path | None = None
    direct_executable: Path | None = None
    output_executable_name: str | None = None
    child_payload: Path | None = None
    config_path: Path | None = None


@dataclass(frozen=True)
class SeedMaterial:
    seed1: int
    dependency_paths: tuple[Path, ...]
    decrypted_config: bytes


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_extracted_root() -> Path:
    return repo_root() / "artifacts" / "extracted"


def default_output_root() -> Path:
    return repo_root() / "artifacts" / "unwrapped"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def load_wrapper_scan_module() -> Any:
    module_path = repo_root() / "scripts" / "generate_reflexive_wrapper_versions.py"
    spec = importlib.util.spec_from_file_location("reflexive_wrapper_versions", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_scan(extracted_root: Path, selected_roots: Iterable[str] | None = None) -> dict[str, Any]:
    module = load_wrapper_scan_module()
    wrapper_roots = None
    if selected_roots is not None:
        wrapper_roots = [(extracted_root / Path(root)).resolve() for root in selected_roots]
    return module.build_scan(extracted_root, wrapper_roots=wrapper_roots)


def choose_static_wrapper(record: dict[str, Any], wrapper_root: Path) -> Path | None:
    candidates: list[tuple[int, Path]] = []

    for candidate in record["binary_candidates"]:
        if not candidate["looks_like_wrapper_binary"]:
            continue

        path = repo_root() / Path(candidate["path"])
        role = str(candidate["role"])
        if role == "top_level_exe":
            priority = 0
        elif role == "launcher_bak":
            priority = 1
        elif role == "support_exe":
            priority = 2
        else:
            priority = 3
        candidates.append((priority, path))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (item[0], item[1].name.lower()))
    chosen = candidates[0][1]

    if chosen.name.lower().endswith(".exe.bak"):
        patched = wrapper_root / chosen.name[:-4]
        if patched.is_file():
            return patched
    return chosen


def choose_direct_executable(record: dict[str, Any], wrapper_root: Path) -> Path | None:
    candidates: list[Path] = []
    score_hints = wrapper_root.name.lower().replace("_", " ").replace("-", " ")

    for candidate in record["binary_candidates"]:
        if candidate["role"] != "top_level_exe" or candidate["looks_like_wrapper_binary"]:
            continue
        path = repo_root() / Path(candidate["path"])
        if path.name.lower() in UTILITY_EXE_NAMES:
            continue
        candidates.append(path)

    if not candidates:
        return None

    def sort_key(path: Path) -> tuple[int, int, int, str]:
        name = path.name.lower()
        stem = path.stem.lower().replace("_", " ").replace("-", " ")
        utility_penalty = 1 if name in UTILITY_EXE_NAMES else 0
        root_hint_penalty = 0 if any(token and token in stem for token in score_hints.split()) else 1
        size_penalty = -path.stat().st_size
        return (utility_penalty, root_hint_penalty, size_penalty, name)

    candidates.sort(key=sort_key)
    return candidates[0]


def choose_child_payload(wrapper_root: Path) -> Path | None:
    explicit_candidates = [wrapper_root / name for name in RAW1_FILENAMES]
    for candidate in explicit_candidates:
        if candidate.is_file():
            return candidate

    rwg_files = sorted(wrapper_root.glob("*.RWG"))
    if len(rwg_files) == 1:
        return rwg_files[0]
    if len(rwg_files) > 1:
        raise RuntimeError(f"multiple RWG payloads found under {wrapper_root}")
    return None


def choose_config_path(wrapper_root: Path) -> Path | None:
    search_roots = [wrapper_root / "ReflexiveArcade", wrapper_root]
    for search_root in search_roots:
        for name in RAW2_FILENAMES:
            candidate = search_root / name
            if candidate.is_file():
                return candidate
    return None


def static_output_name(wrapper_binary: Path) -> str:
    name = wrapper_binary.name
    if name.lower().endswith(".exe.bak"):
        return name[:-4]
    return name


def choose_strategy(record: dict[str, Any], wrapper_root: Path) -> Strategy:
    primary = record["primary_wrapper_binary"]
    static_wrapper = choose_static_wrapper(record, wrapper_root)
    direct_executable = choose_direct_executable(record, wrapper_root)
    child_payload = choose_child_payload(wrapper_root)
    config_path = choose_config_path(wrapper_root)

    if child_payload is not None and config_path is not None and static_wrapper is not None:
        return Strategy(
            kind="static",
            reason=f"{record['layout_label']} with encrypted child payload",
            wrapper_binary=static_wrapper,
            output_executable_name=static_output_name(static_wrapper),
            child_payload=child_payload,
            config_path=config_path,
        )

    if direct_executable is not None and (
        primary is None or str(primary["role"]) == "support_exe" or record["layout_label"] == "dll_only_with_application_dat"
    ):
        return Strategy(
            kind="direct",
            reason=f"{record['layout_label']} with a non-wrapper top-level game executable",
            direct_executable=direct_executable,
            output_executable_name=direct_executable.name,
        )

    return Strategy(kind="unsupported", reason=f"no safe unwrap strategy for {record['layout_label']}")


def effective_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    roots = [Path(record["root"]) for record in records]
    root_set = set(roots)
    filtered: list[dict[str, Any]] = []

    for record in records:
        root = Path(record["root"])
        if record["primary_wrapper_binary"] is None:
            if any(other != root and other.is_relative_to(root) for other in root_set):
                continue
        filtered.append(record)
    return filtered


def hardlink_or_copy(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        if dest.exists():
            dest.unlink()
        os.link(source, dest)
    except OSError:
        shutil.copy2(source, dest)


def is_top_level_wrapper_sidecar(relative_path: Path) -> bool:
    if len(relative_path.parts) != 1:
        return False
    return relative_path.name.lower() in TOP_LEVEL_WRAPPER_SIDECARS


def should_skip_path(path: Path, relative_path: Path, strategy: Strategy, wrapper_paths: set[Path]) -> bool:
    if relative_path.parts and relative_path.parts[0] == "ReflexiveArcade":
        return True
    if path in wrapper_paths:
        return True
    if path.name.lower() in TOP_LEVEL_WRAPPER_JUNK:
        return True
    if strategy.kind == "static":
        if is_top_level_wrapper_sidecar(relative_path):
            return True
        if strategy.child_payload is not None and path == strategy.child_payload:
            return True
        if strategy.config_path is not None and path == strategy.config_path:
            return True
    return False


def copy_support_tree(source_root: Path, dest_root: Path, strategy: Strategy, wrapper_paths: set[Path]) -> None:
    for path in sorted(source_root.rglob("*")):
        relative_path = path.relative_to(source_root)
        if should_skip_path(path, relative_path, strategy, wrapper_paths):
            continue
        destination = dest_root / relative_path
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            hardlink_or_copy(path, destination)


def initialize_stream(seed: int) -> tuple[list[int], int, int]:
    state = [0] * STATE_WORDS
    current = seed & MASK32

    for index in range(STATE_WORDS - 1, -1, -1):
        product = (current * 0x41C64E6D + 0x3039) & 0xFFFFFFFFFFFFFFFF
        current = product & MASK32
        state[index] = (product >> 16) & MASK32

    clear_mask = MASK32
    bit = 0x80000000
    index = 3
    while bit != 0:
        state[index] = (state[index] & clear_mask) | bit
        clear_mask >>= 1
        bit >>= 1
        index += 7

    return state, 0, 0x67


def stream_next_byte(state: list[int], a: int, b: int) -> tuple[int, int, int]:
    state[a] = (state[a] ^ state[b]) & MASK32
    value = state[a] & 0xFF
    a = (a + 1) % STATE_WORDS
    b = (b + 1) % STATE_WORDS
    return value, a, b


def decrypt_with_stream(data: bytes, seed: int) -> bytes:
    state, a, b = initialize_stream(seed)
    output = bytearray(len(data))

    for index, value in enumerate(data):
        key, a, b = stream_next_byte(state, a, b)
        output[index] = (value - key) & 0xFF

    return bytes(output)


def looks_like_decrypted_config(data: bytes) -> bool:
    return b"Application Name=" in data and b"Demo Time Seconds=" in data


def looks_like_native_entrypoint(data: bytes) -> bool:
    if len(data) < 16:
        return False
    if data[0] not in {0x51, 0x53, 0x55, 0x56, 0x57, 0x6A, 0x81, 0x83, 0x8B}:
        return False
    if 0xE8 not in data[:16]:
        return False
    if not any(opcode in data[:32] for opcode in (0x74, 0x75, 0x84, 0x85)):
        return False
    return True


def parse_config(data: bytes) -> dict[str, str]:
    text = data.decode("latin-1", errors="ignore")
    config: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        config[key.strip()] = value.strip()
    return config


def config_flag(config: dict[str, str], key: str) -> bool:
    value = config.get(key, "").strip().lower()
    return value in {"1", "true", "yes"}


def unique_immediate_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(path for path in root.iterdir() if path.is_file())


def candidate_seed_dependency_files(wrapper_root: Path, config_path: Path, child_payload: Path) -> list[Path]:
    seen: set[Path] = set()
    candidates: list[Path] = []

    for search_root in (config_path.parent, wrapper_root / "ReflexiveArcade", wrapper_root):
        for path in unique_immediate_files(search_root):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)

            lower_name = path.name.lower()
            if path == config_path or path == child_payload:
                continue
            if lower_name.endswith(".exe") or lower_name.endswith(".exe.bak") or lower_name.endswith(".dll"):
                continue
            candidates.append(path)

    def sort_key(path: Path) -> tuple[int, int, int, str]:
        lower_name = path.name.lower()
        same_dir_penalty = 0 if path.parent == config_path.parent else 1
        known_name_penalty = 0 if lower_name in SECONDARY_SEED_DEPENDENCY_NAMES else 1
        return (same_dir_penalty, known_name_penalty, path.stat().st_size, lower_name)

    candidates.sort(key=sort_key)
    return candidates


def derive_seed_material(config_path: Path, child_payload: Path, wrapper_root: Path) -> SeedMaterial:
    encrypted_config = config_path.read_bytes()
    child_size = child_payload.stat().st_size
    candidates = candidate_seed_dependency_files(wrapper_root, config_path, child_payload)

    candidate_pools: list[list[Path]] = []
    primary_candidates = [path for path in candidates if path.name.lower() in PRIMARY_SEED_DEPENDENCY_NAMES]
    secondary_candidates = [path for path in candidates if path.name.lower() in SECONDARY_SEED_DEPENDENCY_NAMES]
    for pool in (primary_candidates, secondary_candidates, candidates):
        if pool and pool not in candidate_pools:
            candidate_pools.append(pool)

    for pool in candidate_pools:
        max_subset_size = min(6, len(pool))
        valid_by_seed: dict[int, SeedMaterial] = {}

        for subset_size in range(max_subset_size + 1):
            for subset in itertools.combinations(pool, subset_size):
                seed1 = (child_size + sum(path.stat().st_size for path in subset)) & MASK32
                if seed1 in valid_by_seed:
                    continue

                decrypted = decrypt_with_stream(encrypted_config, seed1)
                if looks_like_decrypted_config(decrypted):
                    valid_by_seed[seed1] = SeedMaterial(seed1, subset, decrypted)

        if not valid_by_seed:
            continue
        if len(valid_by_seed) != 1:
            seeds = ", ".join(str(seed) for seed in sorted(valid_by_seed))
            raise RuntimeError(f"ambiguous RAW_002 seed candidates for {config_path}: {seeds}")
        return next(iter(valid_by_seed.values()))

    raise RuntimeError(f"unable to derive RAW_002 seed from {config_path}")


def derive_seed2(encrypted_config: bytes) -> int:
    dword_count = len(encrypted_config) & 3
    total = 0
    for index in range(dword_count):
        start = index * 4
        total = (total + int.from_bytes(encrypted_config[start : start + 4], "little")) & MASK32
    return total


def native_encrypted_region(pe: pefile.PE, short_fixed: bool) -> tuple[int, int]:
    entrypoint = pe.OPTIONAL_HEADER.AddressOfEntryPoint

    for section in pe.sections:
        virtual_address = section.VirtualAddress
        virtual_size = int(section.Misc_VirtualSize)
        raw_size = int(section.SizeOfRawData)
        section_span = max(virtual_size, raw_size)

        if not (virtual_address <= entrypoint < virtual_address + section_span):
            continue

        usable_size = min(virtual_size, raw_size)
        offset_in_section = entrypoint - virtual_address
        if offset_in_section > usable_size:
            raise RuntimeError("entrypoint falls outside the section's usable raw range")

        raw_start = int(section.PointerToRawData) + offset_in_section
        decrypt_length = usable_size - offset_in_section
        if short_fixed:
            decrypt_length = min(decrypt_length, 0x80)
        return raw_start, decrypt_length

    raise RuntimeError("unable to locate entrypoint section for child payload")


def dotnet_encrypted_region(pe: pefile.PE) -> tuple[int, int]:
    cli_directory = pe.OPTIONAL_HEADER.DATA_DIRECTORY[14]
    if cli_directory.VirtualAddress == 0 or cli_directory.Size == 0:
        raise RuntimeError("missing CLR COM descriptor for .NET child payload")

    cli_offset = pe.get_offset_from_rva(cli_directory.VirtualAddress)
    cli_header = pe.__data__[cli_offset : cli_offset + cli_directory.Size]
    if len(cli_header) < 0x10:
        raise RuntimeError("truncated CLR header")

    cli_header_size = int.from_bytes(cli_header[0:4], "little")
    metadata_rva = int.from_bytes(cli_header[8:12], "little")
    if cli_header_size <= 0 or metadata_rva == 0:
        raise RuntimeError("invalid CLR header fields")

    region_start = cli_offset + cli_header_size
    metadata_offset = pe.get_offset_from_rva(metadata_rva)
    region_length = metadata_offset - region_start
    if region_length <= 0:
        raise RuntimeError("invalid .NET encrypted region")
    return region_start, region_length


def decrypt_empty_config_child(strategy: Strategy) -> tuple[bytes, dict[str, Any]]:
    assert strategy.child_payload is not None
    assert strategy.config_path is not None

    child_bytes = bytearray(strategy.child_payload.read_bytes())
    pe = pefile.PE(data=bytes(child_bytes), fast_load=True)
    region_start, region_length = native_encrypted_region(pe, False)
    decrypted_region = decrypt_with_stream(bytes(child_bytes[region_start : region_start + region_length]), 0)
    if not looks_like_native_entrypoint(decrypted_region[:64]):
        raise RuntimeError(f"empty RAW_002 fallback did not yield a plausible entrypoint for {strategy.child_payload}")
    child_bytes[region_start : region_start + region_length] = decrypted_region
    return bytes(child_bytes), {
        "seed1": None,
        "seed2": 0,
        "dependency_paths": [],
        "child_payload": str(strategy.child_payload),
        "config_path": str(strategy.config_path),
        "region_start": region_start,
        "region_length": region_length,
        "config_fallback": "empty_raw_002_seed0_native",
    }


def decrypt_static_child(wrapper_root: Path, strategy: Strategy) -> tuple[bytes, dict[str, Any]]:
    assert strategy.child_payload is not None
    assert strategy.config_path is not None

    if strategy.config_path.stat().st_size == 0:
        return decrypt_empty_config_child(strategy)

    seed_material = derive_seed_material(strategy.config_path, strategy.child_payload, wrapper_root)
    config = parse_config(seed_material.decrypted_config)

    child_bytes = bytearray(strategy.child_payload.read_bytes())
    pe = pefile.PE(data=bytes(child_bytes), fast_load=True)
    if config_flag(config, "Is .NET Executable"):
        region_start, region_length = dotnet_encrypted_region(pe)
    else:
        region_start, region_length = native_encrypted_region(pe, config_flag(config, "Game Needs Short Fixed Encryption"))
    encrypted_config = strategy.config_path.read_bytes()
    seed2 = derive_seed2(encrypted_config)
    decrypted_region = decrypt_with_stream(bytes(child_bytes[region_start : region_start + region_length]), seed2)
    child_bytes[region_start : region_start + region_length] = decrypted_region
    return bytes(child_bytes), {
        "seed1": seed_material.seed1,
        "seed2": seed2,
        "dependency_paths": [str(path) for path in seed_material.dependency_paths],
        "child_payload": str(strategy.child_payload),
        "config_path": str(strategy.config_path),
        "region_start": region_start,
        "region_length": region_length,
    }


def probe_static_child(wrapper_root: Path, strategy: Strategy) -> dict[str, Any]:
    _, summary = decrypt_static_child(wrapper_root, strategy)
    return summary


def static_unwrap_child(wrapper_root: Path, strategy: Strategy, output_executable: Path) -> dict[str, Any]:
    assert strategy.wrapper_binary is not None
    child_bytes, summary = decrypt_static_child(wrapper_root, strategy)
    output_executable.write_bytes(child_bytes)

    try:
        output_executable.chmod(strategy.wrapper_binary.stat().st_mode)
    except OSError:
        pass

    return summary


def materialize_record(record: dict[str, Any], extracted_root: Path, output_root: Path, force: bool) -> dict[str, Any]:
    relative_root = Path(record["root"])
    wrapper_root = extracted_root / relative_root
    destination_root = output_root / relative_root
    strategy = choose_strategy(record, wrapper_root)
    wrapper_paths = {
        repo_root() / Path(candidate["path"])
        for candidate in record["binary_candidates"]
        if candidate["looks_like_wrapper_binary"]
    }

    summary: dict[str, Any] = {
        "root": str(relative_root),
        "strategy": strategy.kind,
        "reason": strategy.reason,
        "output_root": str(destination_root),
    }

    if strategy.kind == "unsupported":
        summary["status"] = "unsupported"
        return summary

    if destination_root.exists():
        if not force:
            raise RuntimeError(f"{destination_root} already exists; pass --force to replace it")
        shutil.rmtree(destination_root)

    destination_root.mkdir(parents=True, exist_ok=True)
    copy_support_tree(wrapper_root, destination_root, strategy, wrapper_paths)

    if strategy.kind == "static":
        assert strategy.output_executable_name is not None
        output_executable = destination_root / strategy.output_executable_name
        static_summary = static_unwrap_child(wrapper_root, strategy, output_executable)
        summary["status"] = "ok"
        summary["wrapper_binary"] = None if strategy.wrapper_binary is None else str(strategy.wrapper_binary)
        summary["output_executable"] = str(output_executable)
        summary.update(static_summary)
        return summary

    assert strategy.direct_executable is not None
    summary["status"] = "ok"
    summary["output_executable"] = str(destination_root / strategy.direct_executable.name)
    summary["direct_executable"] = str(strategy.direct_executable)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize wrapper-free Reflexive game trees under artifacts/unwrapped."
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help="Optional relative or absolute extracted game roots. Defaults to all supported roots.",
    )
    parser.add_argument(
        "--extracted-root",
        type=Path,
        default=default_extracted_root(),
        help="Root containing extracted Reflexive Arcade directories.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=default_output_root(),
        help="Destination root for wrapper-free game trees.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing outputs.",
    )
    parser.add_argument(
        "--list-unsupported",
        action="store_true",
        help="Print unsupported roots after processing.",
    )
    return parser.parse_args()


def normalize_target(target: str, extracted_root: Path) -> str:
    path = Path(target)
    if path.is_absolute():
        return str(path.resolve().relative_to(extracted_root))
    return str(path)


def main() -> int:
    args = parse_args()
    extracted_root = args.extracted_root.resolve()
    output_root = args.output_root.resolve()
    selected = {normalize_target(target, extracted_root) for target in args.targets} if args.targets else None
    inventory = build_scan(extracted_root, selected)
    records = effective_records(inventory["roots"])
    if selected is not None:
        records = [record for record in records if record["root"] in selected]

    successes = 0
    unsupported: list[dict[str, Any]] = []

    for record in records:
        summary = materialize_record(record, extracted_root, output_root, args.force)
        if summary["status"] == "unsupported":
            unsupported.append(summary)
            print(f"UNSUPPORTED {summary['root']}: {summary['reason']}")
            continue

        successes += 1
        print(f"OK {summary['root']} -> {display_path(Path(summary['output_root']))}")
        if "output_executable" in summary:
            print(f"  executable: {display_path(Path(summary['output_executable']))}")

    print(f"Supported outputs materialized: {successes}")
    print(f"Unsupported roots: {len(unsupported)}")

    if args.list_unsupported and unsupported:
        for summary in unsupported:
            print(f"- {summary['root']}: {summary['reason']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
