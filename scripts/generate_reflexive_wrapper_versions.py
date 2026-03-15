#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pefile"]
# ///

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import pefile


DLL_SECTION_NAMES = (".text", ".data")
WRAPPER_MARKERS = {
    "has_reflexive_signature": b"ReflexiveArcade DLL Signature",
    "has_radll_get_dll_version": b"radll_GetDLLVersionAsInt",
    "has_radll_initialize": b"radll_Initialize",
    "has_wrapper_load_error": b"The ReflexiveArcade.dll file could not be loaded",
}
BUILD_STRING_RE = re.compile(rb"Build\s+(\d{2,4})\x00")
SKIP_EXE_NAMES = {"ReflexiveArcade.exe", "unins000.exe"}
DLL_MAJOR_BY_SECTION_HASH = {
    (
        "d8a3dbb9bc2bb23c02c9f435424adfc4810c302248440a98c7ffb7b44f441ddb",
        "18d5843eefdce6769ebfd3eb5d2a8acba3e73a3e66638e27ddf517557b7414b9",
    ): 5,
    (
        "fe252b9105c0b5b62efbf67a6ec3da7d10eaaeff8ce94ec68ab862df426569d7",
        "b5cd1913416f39d5f45bade94d76ea8ee7fc7a4a6cd88b6dc5b43b39c2e1b746",
    ): 3,
    (
        "7b346dff40795f96f533b9765c54c1326ef6ba97ad0bd31f8ffd41a2c4ce5de7",
        "959452bc016c1f37d1a96e8ec71953ffe3d8c177ff965e032c39b2b2229f7d36",
    ): 5,
    (
        "bb08623750681215195b8d84e591830f45fa66411dcb2d6695e814bf7ac3764f",
        "70b36def5dd39617ce7ee2b4e383d797699e0c2ce8a987fe689e5a40b72e28f0",
    ): 5,
}


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_extracted_root() -> Path:
    return repo_root() / "artifacts" / "extracted"


def default_markdown_path() -> Path:
    return repo_root() / "docs" / "reflexive_wrapper_versions.md"


def default_json_path() -> Path:
    return repo_root() / "docs" / "reflexive_wrapper_versions.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def utc_timestamp(value: int | None) -> str | None:
    if value is None:
        return None
    return dt.datetime.fromtimestamp(value, dt.UTC).isoformat().replace("+00:00", "Z")


def display_path(path: Path) -> str:
    root = repo_root()
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def discover_wrapper_roots(extracted_root: Path) -> list[Path]:
    roots: set[Path] = set()

    for marker in extracted_root.rglob("ReflexiveArcade/ReflexiveArcade.dll"):
        roots.add(marker.parent.parent.resolve())
    for marker in extracted_root.rglob("ReflexiveArcade/RAW_002.wdt"):
        roots.add(marker.parent.parent.resolve())
    for marker in extracted_root.rglob("ReflexiveArcade.exe"):
        roots.add(marker.parent.resolve())

    return sorted(roots)


def layout_label(wrapper_root: Path) -> str:
    reflexive_dir = wrapper_root / "ReflexiveArcade"
    has_reflexive_exe = (wrapper_root / "ReflexiveArcade.exe").is_file()
    has_raw_002 = (reflexive_dir / "RAW_002.wdt").is_file()
    has_raw_003 = (reflexive_dir / "RAW_003.wdt").is_file()
    has_rwg = any(wrapper_root.glob("*.RWG"))
    has_raw_001 = (wrapper_root / "RAW_001.exe").is_file()
    has_launcher_bak = any(wrapper_root.glob("*.exe.BAK"))
    has_application_dat = (reflexive_dir / "Application.dat").is_file()
    has_arcade_dat = (reflexive_dir / "Arcade.dat").is_file()

    if has_raw_002 and has_raw_003 and has_rwg and has_launcher_bak:
        return "wrapped_rwg_with_config"
    if has_raw_002 and has_raw_003 and has_raw_001 and has_launcher_bak:
        return "wrapped_raw001_with_config"
    if has_reflexive_exe and has_application_dat and has_arcade_dat and not has_raw_002 and not has_rwg and not has_raw_001:
        return "helper_exe_with_application_dat"
    if has_rwg and has_launcher_bak and not has_raw_002:
        return "wrapped_rwg_without_raw_002"
    if has_application_dat and has_arcade_dat and not has_rwg and not has_raw_001 and not has_launcher_bak and not has_reflexive_exe:
        return "dll_only_with_application_dat"
    return "other"


def pe_section_hashes(path: Path, section_names: tuple[str, ...]) -> dict[str, str | None]:
    pe = pefile.PE(str(path), fast_load=True)
    sections = {
        section.Name.rstrip(b"\x00").decode("ascii", "ignore"): sha256_bytes(section.get_data())
        for section in pe.sections
    }
    return {name: sections.get(name) for name in section_names}


def scan_binary(path: Path, role: str) -> dict[str, object]:
    data = path.read_bytes()
    markers = {name: marker in data for name, marker in WRAPPER_MARKERS.items()}
    pe = pefile.PE(str(path), fast_load=True)
    return {
        "role": role,
        "path": display_path(path),
        "name": path.name,
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "timestamp": pe.FILE_HEADER.TimeDateStamp,
        "timestamp_utc": utc_timestamp(pe.FILE_HEADER.TimeDateStamp),
        "builds": sorted({int(match.group(1)) for match in BUILD_STRING_RE.finditer(data)}),
        "wrapper_markers": markers,
        "looks_like_wrapper_binary": any(markers.values()),
    }


def choose_primary_wrapper_binary(candidates: list[dict[str, object]]) -> dict[str, object] | None:
    for role in ("support_exe", "launcher_bak", "top_level_exe"):
        matches = [candidate for candidate in candidates if candidate["role"] == role and candidate["looks_like_wrapper_binary"]]
        if matches:
            matches.sort(key=lambda candidate: (not candidate["builds"], candidate["name"]))
            return matches[0]
    return None


def support_dll_record(path: Path) -> dict[str, object]:
    hashes = pe_section_hashes(path, DLL_SECTION_NAMES)
    hash_key = (hashes[".text"], hashes[".data"])
    return {
        "path": display_path(path),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "timestamp": pefile.PE(str(path), fast_load=True).FILE_HEADER.TimeDateStamp,
        "timestamp_utc": utc_timestamp(pefile.PE(str(path), fast_load=True).FILE_HEADER.TimeDateStamp),
        "section_hashes": hashes,
        "major_version": DLL_MAJOR_BY_SECTION_HASH.get(hash_key),
        "major_version_source": "verified representative family in Binja" if hash_key in DLL_MAJOR_BY_SECTION_HASH else None,
    }


def top_level_executable_candidates(wrapper_root: Path) -> list[Path]:
    return sorted(
        path
        for path in wrapper_root.glob("*.exe")
        if path.name not in SKIP_EXE_NAMES
    )


def build_scan(extracted_root: Path) -> dict[str, object]:
    roots: list[dict[str, object]] = []

    for wrapper_root in discover_wrapper_roots(extracted_root):
        record: dict[str, object] = {
            "root": str(wrapper_root.relative_to(extracted_root)),
            "layout_label": layout_label(wrapper_root),
            "support_dll": None,
            "binary_candidates": [],
            "primary_wrapper_binary": None,
            "notes": [],
        }

        support_dll = wrapper_root / "ReflexiveArcade" / "ReflexiveArcade.dll"
        if support_dll.is_file():
            record["support_dll"] = support_dll_record(support_dll)

        candidates: list[dict[str, object]] = []
        support_exe = wrapper_root / "ReflexiveArcade.exe"
        if support_exe.is_file():
            candidates.append(scan_binary(support_exe, "support_exe"))

        for path in sorted(wrapper_root.glob("*.exe.BAK")):
            candidates.append(scan_binary(path, "launcher_bak"))

        for path in top_level_executable_candidates(wrapper_root):
            candidates.append(scan_binary(path, "top_level_exe"))

        record["binary_candidates"] = candidates
        primary = choose_primary_wrapper_binary(candidates)
        record["primary_wrapper_binary"] = primary

        if primary is not None and primary["role"] == "support_exe":
            if any(candidate["role"] == "launcher_bak" for candidate in candidates):
                record["notes"].append("support_exe_is_wrapper_entrypoint")
            if any(candidate["role"] == "launcher_bak" and not candidate["looks_like_wrapper_binary"] for candidate in candidates):
                record["notes"].append("launcher_bak_is_not_wrapper_binary")
        if primary is None:
            record["notes"].append("no_wrapper_entry_binary_detected")

        roots.append(record)

    dll_major_counter: Counter[int | None] = Counter()
    role_build_counter: Counter[tuple[str, bool]] = Counter()
    build_counter: Counter[int] = Counter()
    build_examples: dict[int, str] = {}
    build_roles: defaultdict[int, set[str]] = defaultdict(set)
    buildless_wrapper_roots: list[dict[str, object]] = []
    roots_without_wrapper_binary: list[dict[str, object]] = []
    top_level_build_roots: list[dict[str, object]] = []
    mixed_layout_roots: list[dict[str, object]] = []

    for record in roots:
        support_dll = record["support_dll"]
        if support_dll is not None:
            dll_major_counter[support_dll["major_version"]] += 1

        primary = record["primary_wrapper_binary"]
        if primary is None:
            role_build_counter[("none", False)] += 1
            roots_without_wrapper_binary.append(
                {
                    "root": record["root"],
                    "layout_label": record["layout_label"],
                }
            )
            continue

        has_build = bool(primary["builds"])
        role_build_counter[(str(primary["role"]), has_build)] += 1
        if has_build:
            for build in primary["builds"]:
                build_counter[build] += 1
                build_examples.setdefault(build, str(record["root"]))
                build_roles[build].add(str(primary["role"]))
        else:
            buildless_wrapper_roots.append(
                {
                    "root": record["root"],
                    "primary_wrapper_role": primary["role"],
                    "primary_wrapper_path": primary["path"],
                }
            )

        if primary["role"] == "top_level_exe" and primary["builds"]:
            top_level_build_roots.append(
                {
                    "root": record["root"],
                    "path": primary["path"],
                    "builds": primary["builds"],
                }
            )

        if record["notes"]:
            mixed_layout_roots.append(
                {
                    "root": record["root"],
                    "notes": record["notes"],
                }
            )

    inventory = {
        "generated_from": str(extracted_root),
        "methodology": {
            "wrapper_binary_detection": "A binary is treated as Reflexive wrapper code if it contains any of: ReflexiveArcade DLL Signature, radll_GetDLLVersionAsInt, radll_Initialize, or the standard ReflexiveArcade.dll load-error string.",
            "build_string_detection": "Build numbers are only accepted from standalone null-terminated ASCII strings of the form 'Build NNN'.",
            "dll_major_version_source": "DLL major versions are assigned by matching ReflexiveArcade.dll .text/.data section hashes to the four families whose radll_GetDLLVersionAsInt exports were verified in Binja.",
        },
        "summary": {
            "root_count": len(roots),
            "dll_major_versions": [
                {
                    "major_version": major_version,
                    "count": count,
                }
                for major_version, count in sorted(
                    dll_major_counter.items(),
                    key=lambda item: (-1 if item[0] is None else item[0]),
                )
            ],
            "primary_wrapper_entrypoints": [
                {
                    "role": role,
                    "has_literal_build": has_build,
                    "count": count,
                }
                for (role, has_build), count in sorted(role_build_counter.items())
            ],
            "primary_build_histogram": [
                {
                    "build": build,
                    "count": count,
                    "roles": sorted(build_roles[build]),
                    "example_root": build_examples[build],
                }
                for build, count in sorted(build_counter.items())
            ],
        },
        "top_level_build_roots": top_level_build_roots,
        "buildless_wrapper_roots": buildless_wrapper_roots,
        "roots_without_wrapper_binary": roots_without_wrapper_binary,
        "mixed_layout_roots": mixed_layout_roots,
        "roots": roots,
    }

    return inventory


def render_markdown(inventory: dict[str, object], extracted_root: Path) -> str:
    root = repo_root()
    try:
        extracted_display = extracted_root.relative_to(root)
    except ValueError:
        extracted_display = extracted_root

    summary = inventory["summary"]
    assert isinstance(summary, dict)
    dll_major_versions = summary["dll_major_versions"]
    primary_wrapper_entrypoints = summary["primary_wrapper_entrypoints"]
    primary_build_histogram = summary["primary_build_histogram"]
    top_level_build_roots = inventory["top_level_build_roots"]
    buildless_wrapper_roots = inventory["buildless_wrapper_roots"]
    roots_without_wrapper_binary = inventory["roots_without_wrapper_binary"]
    mixed_layout_roots = inventory["mixed_layout_roots"]
    methodology = inventory["methodology"]

    lines = [
        "# Reflexive Wrapper Versions",
        "",
        f"Generated from wrapper roots discovered under `{extracted_display}`.",
        "",
        "## Methodology",
        "",
        f"- {methodology['wrapper_binary_detection']}",
        f"- {methodology['build_string_detection']}",
        f"- {methodology['dll_major_version_source']}",
        "",
        "## Summary",
        "",
        f"- Wrapper roots scanned: {summary['root_count']}",
        f"- Primary wrapper binaries with a literal `Build NNN` string: {sum(item['count'] for item in primary_wrapper_entrypoints if item['has_literal_build'])}",
        f"- Primary wrapper binaries without a literal build string: {sum(item['count'] for item in primary_wrapper_entrypoints if not item['has_literal_build'] and item['role'] != 'none')}",
        f"- Roots with no preserved wrapper entry binary: {sum(item['count'] for item in primary_wrapper_entrypoints if item['role'] == 'none')}",
        "",
        "## DLL API Major Versions",
        "",
        "| DLL Major | Roots |",
        "| --- | ---: |",
    ]

    for item in dll_major_versions:
        assert isinstance(item, dict)
        major = item["major_version"]
        label = "-" if major is None else str(major)
        lines.append(f"| `{label}` | {item['count']} |")

    lines.extend(
        [
            "",
            "## Primary Wrapper Entry Binaries",
            "",
            "| Role | Literal Build | Roots |",
            "| --- | --- | ---: |",
        ]
    )

    for item in primary_wrapper_entrypoints:
        assert isinstance(item, dict)
        literal_build = "yes" if item["has_literal_build"] else "no"
        lines.append(f"| `{item['role']}` | `{literal_build}` | {item['count']} |")

    lines.extend(
        [
            "",
            "## Wrapper Build Histogram",
            "",
            "| Build | Roots | Roles | Example |",
            "| --- | ---: | --- | --- |",
        ]
    )

    for item in primary_build_histogram:
        assert isinstance(item, dict)
        roles_display = ", ".join(f"`{role}`" for role in item["roles"])
        lines.append(f"| `{item['build']}` | {item['count']} | {roles_display} | `{item['example_root']}` |")

    lines.extend(
        [
            "",
            "## Top-Level EXE Roots With Build Strings",
            "",
            "| Root | Primary Wrapper | Build |",
            "| --- | --- | --- |",
        ]
    )

    for item in top_level_build_roots:
        assert isinstance(item, dict)
        lines.append(f"| `{item['root']}` | `{item['path']}` | `{', '.join(str(build) for build in item['builds'])}` |")

    lines.extend(
        [
            "",
            "## Buildless Wrapper Binaries",
            "",
            "| Root | Primary Wrapper Role | Primary Wrapper |",
            "| --- | --- | --- |",
        ]
    )

    for item in buildless_wrapper_roots:
        assert isinstance(item, dict)
        lines.append(f"| `{item['root']}` | `{item['primary_wrapper_role']}` | `{item['primary_wrapper_path']}` |")

    lines.extend(
        [
            "",
            "## Roots Without Preserved Wrapper Entry Binary",
            "",
            "| Root | Layout |",
            "| --- | --- |",
        ]
    )

    for item in roots_without_wrapper_binary:
        assert isinstance(item, dict)
        lines.append(f"| `{item['root']}` | `{item['layout_label']}` |")

    lines.extend(
        [
            "",
            "## Mixed Layout Notes",
            "",
            "| Root | Notes |",
            "| --- | --- |",
        ]
    )

    for item in mixed_layout_roots:
        assert isinstance(item, dict)
        notes_display = ", ".join(f"`{note}`" for note in item["notes"])
        lines.append(f"| `{item['root']}` | {notes_display} |")

    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a wrapper-version scan for the extracted Reflexive Arcade corpus."
    )
    parser.add_argument(
        "extracted_root",
        nargs="?",
        type=Path,
        default=default_extracted_root(),
        help="Root containing extracted Reflexive Arcade directories.",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=default_markdown_path(),
        help="Markdown output path.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=default_json_path(),
        help="JSON output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    extracted_root = args.extracted_root.resolve()
    markdown_out = args.markdown_out.resolve()
    json_out = args.json_out.resolve()

    inventory = build_scan(extracted_root)

    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.write_text(render_markdown(inventory, extracted_root) + "\n", encoding="utf-8")
    json_out.write_text(json.dumps(inventory, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    print(f"Wrote {markdown_out}")
    print(f"Wrote {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
