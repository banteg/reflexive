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
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import pefile
from source_layout import DEFAULT_SOURCE_ID
from source_layout import extracted_root as source_extracted_root


DLL_SECTION_NAMES = (".text", ".data", ".rsrc", ".reloc")
EXE_SECTION_NAMES = (".text", ".rdata", ".data")
LAYOUT_FLAG_ORDER = (
    "has_application_dat",
    "has_arcade_dat",
    "has_launcher_bak",
    "has_raw_001",
    "has_raw_002",
    "has_raw_003",
    "has_reflexive_dll",
    "has_reflexive_exe",
    "has_rwg",
)
LAUNCHER_BUILD_RE = re.compile(rb"Build\s+(\d{2,4})")
VERSION_NUMBER_RE = re.compile(r"Version Number=(\d+)")
INFO_STRING_RE = re.compile(r"Info String=([^\r\n]+)")
MANAGER_INFO_VERSION_RE = re.compile(r"Manager Information Version=(\d+)")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_extracted_root() -> Path:
    return source_extracted_root(DEFAULT_SOURCE_ID)


def default_markdown_path() -> Path:
    return repo_root() / "docs" / "generated" / "archive" / "wrapper_inventory.md"


def default_json_path() -> Path:
    return repo_root() / "docs" / "generated" / "archive" / "wrapper_inventory.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def utc_timestamp(value: int | None) -> str | None:
    if value is None:
        return None
    return dt.datetime.fromtimestamp(value, dt.UTC).isoformat().replace("+00:00", "Z")


def discover_wrapper_roots(extracted_root: Path) -> list[Path]:
    roots: set[Path] = set()

    for marker in extracted_root.rglob("ReflexiveArcade/ReflexiveArcade.dll"):
        roots.add(marker.parent.parent.resolve())
    for marker in extracted_root.rglob("ReflexiveArcade/RAW_002.wdt"):
        roots.add(marker.parent.parent.resolve())
    for marker in extracted_root.rglob("ReflexiveArcade.exe"):
        roots.add(marker.parent.resolve())

    return sorted(roots)


def display_path(path: Path) -> str:
    root = repo_root()
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def pe_summary(path: Path, section_names: tuple[str, ...]) -> dict[str, object]:
    pe = pefile.PE(str(path), fast_load=True)
    sections = {
        section.Name.rstrip(b"\x00").decode("ascii", "ignore"): sha256_bytes(section.get_data())
        for section in pe.sections
    }
    return {
        "path": display_path(path),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "timestamp": pe.FILE_HEADER.TimeDateStamp,
        "timestamp_utc": utc_timestamp(pe.FILE_HEADER.TimeDateStamp),
        "section_hashes": {name: sections.get(name) for name in section_names},
    }


def extract_archive_member(archive_path: Path, member_path: str) -> str | None:
    try:
        return subprocess.check_output(
            ["bsdtar", "-xOf", str(archive_path), member_path],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def parse_asset_version(archive_path: Path, member_path: str) -> dict[str, object] | None:
    text = extract_archive_member(archive_path, member_path)
    if text is None:
        return None

    version_match = VERSION_NUMBER_RE.search(text)
    info_match = INFO_STRING_RE.search(text)
    if version_match is None:
        return None

    return {
        "version_number": int(version_match.group(1)),
        "info_string": info_match.group(1) if info_match is not None else None,
    }


def parse_manager_info_version(archive_path: Path, member_path: str) -> int | None:
    text = extract_archive_member(archive_path, member_path)
    if text is None:
        return None

    version_match = MANAGER_INFO_VERSION_RE.search(text)
    if version_match is None:
        return None
    return int(version_match.group(1))


def extract_launcher_builds(path: Path) -> list[int]:
    return sorted({int(match.group(1)) for match in LAUNCHER_BUILD_RE.finditer(path.read_bytes())})


def layout_flags(wrapper_root: Path) -> dict[str, bool]:
    reflexive_dir = wrapper_root / "ReflexiveArcade"
    return {
        "has_reflexive_dll": (reflexive_dir / "ReflexiveArcade.dll").is_file(),
        "has_reflexive_exe": (wrapper_root / "ReflexiveArcade.exe").is_file(),
        "has_raw_002": (reflexive_dir / "RAW_002.wdt").is_file(),
        "has_raw_003": (reflexive_dir / "RAW_003.wdt").is_file(),
        "has_rwg": any(wrapper_root.glob("*.RWG")),
        "has_raw_001": (wrapper_root / "RAW_001.exe").is_file(),
        "has_launcher_bak": any(wrapper_root.glob("*.exe.BAK")),
        "has_application_dat": (reflexive_dir / "Application.dat").is_file(),
        "has_arcade_dat": (reflexive_dir / "Arcade.dat").is_file(),
    }


def classify_layout(flags: dict[str, bool]) -> str:
    if (
        flags["has_raw_002"]
        and flags["has_raw_003"]
        and flags["has_rwg"]
        and flags["has_launcher_bak"]
    ):
        return "wrapped_rwg_with_config"
    if (
        flags["has_raw_002"]
        and flags["has_raw_003"]
        and flags["has_raw_001"]
        and flags["has_launcher_bak"]
    ):
        return "wrapped_raw001_with_config"
    if (
        flags["has_reflexive_exe"]
        and flags["has_application_dat"]
        and flags["has_arcade_dat"]
        and not flags["has_raw_002"]
        and not flags["has_rwg"]
        and not flags["has_raw_001"]
    ):
        return "helper_exe_with_application_dat"
    if flags["has_rwg"] and flags["has_launcher_bak"] and not flags["has_raw_002"]:
        return "wrapped_rwg_without_raw_002"
    if (
        flags["has_reflexive_dll"]
        and flags["has_application_dat"]
        and flags["has_arcade_dat"]
        and not flags["has_rwg"]
        and not flags["has_raw_001"]
        and not flags["has_launcher_bak"]
        and not flags["has_reflexive_exe"]
    ):
        return "dll_only_with_application_dat"
    return "other"


def root_record(extracted_root: Path, wrapper_root: Path) -> dict[str, object]:
    reflexive_dir = wrapper_root / "ReflexiveArcade"
    record: dict[str, object] = {
        "root": str(wrapper_root.relative_to(extracted_root)),
        "layout": {},
        "support_dll": None,
        "support_exe": None,
        "launcher_bak": None,
        "launcher_builds": [],
        "application_asset_version": None,
        "arcade_asset_version": None,
        "manager_info_version": None,
    }

    flags = layout_flags(wrapper_root)
    record["layout"] = {
        "flags": flags,
        "label": classify_layout(flags),
    }

    support_dll = reflexive_dir / "ReflexiveArcade.dll"
    if support_dll.is_file():
        record["support_dll"] = pe_summary(support_dll, DLL_SECTION_NAMES)

    support_exe = wrapper_root / "ReflexiveArcade.exe"
    if support_exe.is_file():
        record["support_exe"] = pe_summary(support_exe, EXE_SECTION_NAMES)

    launcher_baks = sorted(wrapper_root.glob("*.exe.BAK"))
    if launcher_baks:
        record["launcher_bak"] = pe_summary(launcher_baks[0], EXE_SECTION_NAMES)
        record["launcher_builds"] = extract_launcher_builds(launcher_baks[0])

    application_dat = reflexive_dir / "Application.dat"
    if application_dat.is_file():
        record["application_asset_version"] = parse_asset_version(
            application_dat,
            "Resources/Application.version.txt",
        )

    arcade_dat = reflexive_dir / "Arcade.dat"
    if arcade_dat.is_file():
        record["arcade_asset_version"] = parse_asset_version(
            arcade_dat,
            "Resources/Arcade.version.txt",
        )
        record["manager_info_version"] = parse_manager_info_version(
            arcade_dat,
            "Resources/RAManagerData.managerinfo.txt",
        )

    return record


def family_key(summary: dict[str, object] | None, section_names: tuple[str, ...]) -> tuple[str | None, ...] | None:
    if summary is None:
        return None
    hashes = summary["section_hashes"]
    assert isinstance(hashes, dict)
    return tuple(hashes.get(name) for name in section_names)


def assign_family_ids(items: list[dict[str, object]], key_name: str, family_prefix: str) -> dict[tuple[str | None, ...], str]:
    counter: Counter[tuple[str | None, ...]] = Counter()
    for item in items:
        key = item[key_name]
        if key is not None:
            counter[key] += 1

    ordered_keys = [key for key, _count in counter.most_common()]
    return {key: f"{family_prefix}_{index:02d}" for index, key in enumerate(ordered_keys, start=1)}


def build_inventory(extracted_root: Path) -> dict[str, object]:
    records = [root_record(extracted_root, wrapper_root) for wrapper_root in discover_wrapper_roots(extracted_root)]

    for record in records:
        record["support_dll_family_key"] = family_key(record["support_dll"], DLL_SECTION_NAMES)
        record["support_exe_family_key"] = family_key(record["support_exe"], EXE_SECTION_NAMES)
        record["launcher_family_key"] = family_key(record["launcher_bak"], EXE_SECTION_NAMES)

    dll_family_ids = assign_family_ids(records, "support_dll_family_key", "dll_family")
    support_exe_family_ids = assign_family_ids(records, "support_exe_family_key", "helper_exe_family")
    launcher_family_ids = assign_family_ids(records, "launcher_family_key", "launcher_family")

    xeno_root = "Reflexive Arcade X/Xeno Assault II"
    xeno_record = next(record for record in records if record["root"] == xeno_root)

    for record in records:
        record["support_dll_family"] = (
            dll_family_ids[record["support_dll_family_key"]] if record["support_dll_family_key"] is not None else None
        )
        record["support_exe_family"] = (
            support_exe_family_ids[record["support_exe_family_key"]]
            if record["support_exe_family_key"] is not None
            else None
        )
        record["launcher_family"] = (
            launcher_family_ids[record["launcher_family_key"]] if record["launcher_family_key"] is not None else None
        )

    def build_family_summaries(
        family_ids: dict[tuple[str | None, ...], str],
        source_key: str,
        family_label_key: str,
    ) -> list[dict[str, object]]:
        grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
        for record in records:
            family_id = record[family_label_key]
            if family_id is not None:
                grouped[family_id].append(record)

        families: list[dict[str, object]] = []
        for key, family_id in family_ids.items():
            members = grouped[family_id]
            source_values = [record[source_key] for record in members]
            source_values = [value for value in source_values if value is not None]
            full_sha_values = {
                str(value["sha256"])
                for value in source_values
            }
            size_values = sorted({int(value["size"]) for value in source_values})
            timestamp_values = sorted({int(value["timestamp"]) for value in source_values})
            observed_builds = sorted(
                {
                    build
                    for record in members
                    for build in record["launcher_builds"]
                }
            )
            families.append(
                {
                    "id": family_id,
                    "count": len(members),
                    "section_hashes": {
                        name: key[index] for index, name in enumerate(
                            DLL_SECTION_NAMES if source_key == "support_dll" else EXE_SECTION_NAMES
                        )
                    },
                    "unique_full_sha256_count": len(full_sha_values),
                    "sizes": size_values,
                    "timestamps": timestamp_values,
                    "timestamps_utc": [utc_timestamp(value) for value in timestamp_values],
                    "example_root": members[0]["root"],
                    "observed_builds": observed_builds,
                    "matches_prior_v5_sample": (
                        family_id == xeno_record.get("support_dll_family")
                        if source_key == "support_dll"
                        else family_id == xeno_record.get("launcher_family")
                    ),
                }
            )
        return families

    layout_counter: Counter[str] = Counter()
    layout_examples: dict[str, str] = {}
    exact_layout_counter: Counter[tuple[bool, ...]] = Counter()
    exact_layout_examples: dict[tuple[bool, ...], str] = {}
    for record in records:
        layout = record["layout"]
        assert isinstance(layout, dict)
        label = str(layout["label"])
        layout_counter[label] += 1
        layout_examples.setdefault(label, str(record["root"]))

        flags = layout["flags"]
        assert isinstance(flags, dict)
        exact_key = tuple(bool(flags[name]) for name in LAYOUT_FLAG_ORDER)
        exact_layout_counter[exact_key] += 1
        exact_layout_examples.setdefault(exact_key, str(record["root"]))

    pair_counter: Counter[tuple[str | None, str | None]] = Counter()
    pair_examples: dict[tuple[str | None, str | None], str] = {}
    for record in records:
        pair = (record["support_dll_family"], record["launcher_family"])
        pair_counter[pair] += 1
        pair_examples.setdefault(pair, str(record["root"]))

    launcher_build_counter: Counter[tuple[int, ...]] = Counter()
    launcher_build_examples: dict[tuple[int, ...], str] = {}
    launcher_build_families: defaultdict[tuple[int, ...], set[str]] = defaultdict(set)
    for record in records:
        if record["launcher_bak"] is None:
            continue
        build_key = tuple(record["launcher_builds"])
        launcher_build_counter[build_key] += 1
        launcher_build_examples.setdefault(build_key, str(record["root"]))
        if record["launcher_family"] is not None:
            launcher_build_families[build_key].add(str(record["launcher_family"]))

    application_asset_counter: Counter[tuple[int, str | None]] = Counter()
    application_asset_examples: dict[tuple[int, str | None], str] = {}
    arcade_asset_counter: Counter[tuple[int, str | None]] = Counter()
    arcade_asset_examples: dict[tuple[int, str | None], str] = {}
    manager_info_counter: Counter[int] = Counter()
    manager_info_examples: dict[int, str] = {}
    for record in records:
        application_asset_version = record["application_asset_version"]
        if application_asset_version is not None:
            app_key = (
                int(application_asset_version["version_number"]),
                str(application_asset_version["info_string"]) if application_asset_version["info_string"] is not None else None,
            )
            application_asset_counter[app_key] += 1
            application_asset_examples.setdefault(app_key, str(record["root"]))

        arcade_asset_version = record["arcade_asset_version"]
        if arcade_asset_version is not None:
            arcade_key = (
                int(arcade_asset_version["version_number"]),
                str(arcade_asset_version["info_string"]) if arcade_asset_version["info_string"] is not None else None,
            )
            arcade_asset_counter[arcade_key] += 1
            arcade_asset_examples.setdefault(arcade_key, str(record["root"]))

        manager_info_version = record["manager_info_version"]
        if manager_info_version is not None:
            manager_info_counter[int(manager_info_version)] += 1
            manager_info_examples.setdefault(int(manager_info_version), str(record["root"]))

    inventory = {
        "generated_from": str(extracted_root),
        "wrapper_root_count": len(records),
        "full_file_sha_uniqueness": {
            "support_dll": {
                "file_count": sum(record["support_dll"] is not None for record in records),
                "unique_sha256_count": len(
                    {
                        str(record["support_dll"]["sha256"])
                        for record in records
                        if record["support_dll"] is not None
                    }
                ),
            },
            "launcher_bak": {
                "file_count": sum(record["launcher_bak"] is not None for record in records),
                "unique_sha256_count": len(
                    {
                        str(record["launcher_bak"]["sha256"])
                        for record in records
                        if record["launcher_bak"] is not None
                    }
                ),
            },
            "support_exe": {
                "file_count": sum(record["support_exe"] is not None for record in records),
                "unique_sha256_count": len(
                    {
                        str(record["support_exe"]["sha256"])
                        for record in records
                        if record["support_exe"] is not None
                    }
                ),
            },
        },
        "layout_summary": [
            {"label": label, "count": count, "example_root": layout_examples[label]}
            for label, count in layout_counter.most_common()
        ],
        "layout_flag_order": sorted(layout_flags(Path(".")).keys()),
        "exact_layout_summary": [
            {
                "count": count,
                "flags": dict(zip(LAYOUT_FLAG_ORDER, exact_key, strict=True)),
                "example_root": exact_layout_examples[exact_key],
            }
            for exact_key, count in exact_layout_counter.most_common()
        ],
        "dll_families": build_family_summaries(dll_family_ids, "support_dll", "support_dll_family"),
        "launcher_families": build_family_summaries(launcher_family_ids, "launcher_bak", "launcher_family"),
        "support_exe_families": build_family_summaries(
            support_exe_family_ids,
            "support_exe",
            "support_exe_family",
        ),
        "launcher_build_summary": [
            {
                "builds": list(build_key),
                "count": count,
                "launcher_families": sorted(launcher_build_families[build_key]),
                "example_root": launcher_build_examples[build_key],
            }
            for build_key, count in sorted(
                launcher_build_counter.items(),
                key=lambda item: (item[0] == (), item[0]),
            )
        ],
        "application_asset_version_summary": [
            {
                "version_number": key[0],
                "info_string": key[1],
                "count": count,
                "example_root": application_asset_examples[key],
            }
            for key, count in sorted(application_asset_counter.items())
        ],
        "arcade_asset_version_summary": [
            {
                "version_number": key[0],
                "info_string": key[1],
                "count": count,
                "example_root": arcade_asset_examples[key],
            }
            for key, count in sorted(arcade_asset_counter.items())
        ],
        "manager_info_version_summary": [
            {
                "version_number": version_number,
                "count": count,
                "example_root": manager_info_examples[version_number],
            }
            for version_number, count in sorted(manager_info_counter.items())
        ],
        "pair_summary": [
            {
                "count": count,
                "support_dll_family": pair[0],
                "launcher_family": pair[1],
                "example_root": pair_examples[pair],
            }
            for pair, count in pair_counter.most_common()
        ],
        "roots": [
            {
                key: value
                for key, value in record.items()
                if not key.endswith("_family_key")
            }
            for record in records
        ],
    }

    return inventory


def short_hash(value: str | None) -> str:
    if value is None:
        return "-"
    return value[:16]


def render_markdown(inventory: dict[str, object], extracted_root: Path) -> str:
    root = repo_root()
    try:
        extracted_display = extracted_root.relative_to(root)
    except ValueError:
        extracted_display = extracted_root

    uniqueness = inventory["full_file_sha_uniqueness"]
    assert isinstance(uniqueness, dict)
    dll_families = inventory["dll_families"]
    launcher_families = inventory["launcher_families"]
    support_exe_families = inventory["support_exe_families"]
    layout_summary = inventory["layout_summary"]
    launcher_build_summary = inventory["launcher_build_summary"]
    application_asset_version_summary = inventory["application_asset_version_summary"]
    arcade_asset_version_summary = inventory["arcade_asset_version_summary"]
    manager_info_version_summary = inventory["manager_info_version_summary"]
    pair_summary = inventory["pair_summary"]

    lines = [
        "# Reflexive Wrapper Inventory",
        "",
        f"Generated from wrapper roots discovered under `{extracted_display}`.",
        "",
        f"- Wrapper roots: {inventory['wrapper_root_count']}",
        f"- `ReflexiveArcade.dll` files: {uniqueness['support_dll']['file_count']} total / {uniqueness['support_dll']['unique_sha256_count']} unique full SHA-256",
        f"- Launcher `.exe.BAK` files: {uniqueness['launcher_bak']['file_count']} total / {uniqueness['launcher_bak']['unique_sha256_count']} unique full SHA-256",
        f"- `ReflexiveArcade.exe` files: {uniqueness['support_exe']['file_count']} total / {uniqueness['support_exe']['unique_sha256_count']} unique full SHA-256",
        "",
        "Full-file SHA-256 is too granular for the support DLLs. The useful grouping signal is the PE section hash.",
        "",
        "## Layout Summary",
        "",
    ]

    for item in layout_summary:
        assert isinstance(item, dict)
        lines.append(f"- `{item['label']}`: {item['count']} roots. Example: `{item['example_root']}`")

    lines.extend(
        [
            "",
            "## Wrapper Asset Versions",
            "",
            "| Asset | Version | Roots | Info String | Example |",
            "| --- | ---: | ---: | --- | --- |",
        ]
    )

    for item in application_asset_version_summary:
        assert isinstance(item, dict)
        lines.append(
            f"| `Application.version.txt` | `{item['version_number']}` | {item['count']} | "
            f"`{item['info_string'] or '-'}` | `{item['example_root']}` |"
        )

    for item in arcade_asset_version_summary:
        assert isinstance(item, dict)
        lines.append(
            f"| `Arcade.version.txt` | `{item['version_number']}` | {item['count']} | "
            f"`{item['info_string'] or '-'}` | `{item['example_root']}` |"
        )

    for item in manager_info_version_summary:
        assert isinstance(item, dict)
        lines.append(
            f"| `RAManagerData.managerinfo.txt` | `{item['version_number']}` | {item['count']} | "
            f"`-` | `{item['example_root']}` |"
        )

    lines.extend(
        [
            "",
            "## Launcher Build Strings",
            "",
            "| Build | Roots | Launcher Families | Example |",
            "| --- | ---: | --- | --- |",
        ]
    )

    for item in launcher_build_summary:
        assert isinstance(item, dict)
        build_label = ", ".join(str(value) for value in item["builds"]) if item["builds"] else "-"
        launcher_families_display = ", ".join(f"`{family}`" for family in item["launcher_families"]) or "`-`"
        lines.append(
            f"| `{build_label}` | {item['count']} | {launcher_families_display} | `{item['example_root']}` |"
        )

    lines.extend(
        [
            "",
            "## DLL Families",
            "",
            "| Family | Roots | .text | .data | Timestamp | Example | Note |",
            "| --- | ---: | --- | --- | --- | --- | --- |",
        ]
    )

    for family in dll_families:
        assert isinstance(family, dict)
        section_hashes = family["section_hashes"]
        assert isinstance(section_hashes, dict)
        note = "Matches prior Xeno/Xango/XAvenger/Xmas v5 sample" if family["matches_prior_v5_sample"] else ""
        lines.append(
            f"| `{family['id']}` | {family['count']} | `{short_hash(str(section_hashes['.text']))}` | "
            f"`{short_hash(str(section_hashes['.data']))}` | `{family['timestamps_utc'][0]}` | "
            f"`{family['example_root']}` | {note} |"
        )

    lines.extend(
        [
            "",
            "## Launcher Families",
            "",
            "| Family | Roots | Builds | .text | .rdata | Timestamp | Example | Note |",
            "| --- | ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )

    for family in launcher_families:
        assert isinstance(family, dict)
        section_hashes = family["section_hashes"]
        assert isinstance(section_hashes, dict)
        note = "Matches prior Xeno/Xango/XAvenger/Xmas v5 sample" if family["matches_prior_v5_sample"] else ""
        builds_display = ", ".join(str(value) for value in family["observed_builds"]) if family["observed_builds"] else "-"
        lines.append(
            f"| `{family['id']}` | {family['count']} | `{builds_display}` | `{short_hash(str(section_hashes['.text']))}` | "
            f"`{short_hash(str(section_hashes['.rdata']))}` | `{family['timestamps_utc'][0]}` | "
            f"`{family['example_root']}` | {note} |"
        )

    lines.extend(
        [
            "",
            "## Helper EXE Families",
            "",
            "| Family | Roots | .text | .rdata | Timestamp | Example |",
            "| --- | ---: | --- | --- | --- | --- |",
        ]
    )

    for family in support_exe_families:
        assert isinstance(family, dict)
        section_hashes = family["section_hashes"]
        assert isinstance(section_hashes, dict)
        lines.append(
            f"| `{family['id']}` | {family['count']} | `{short_hash(str(section_hashes['.text']))}` | "
            f"`{short_hash(str(section_hashes['.rdata']))}` | `{family['timestamps_utc'][0]}` | "
            f"`{family['example_root']}` |"
        )

    lines.extend(
        [
            "",
            "## Dominant DLL/Launcher Pairs",
            "",
            "| Roots | DLL Family | Launcher Family | Example |",
            "| ---: | --- | --- | --- |",
        ]
    )

    for pair in pair_summary[:10]:
        assert isinstance(pair, dict)
        lines.append(
            f"| {pair['count']} | `{pair['support_dll_family'] or '-'}` | `{pair['launcher_family'] or '-'}` | "
            f"`{pair['example_root']}` |"
        )

    lines.extend(
        [
            "",
            "## Binja Priorities",
            "",
            "- The patcher README's `167-184` wording lines up with launcher build strings, not the coarse DLL export major. The corpus is overwhelmingly `Build 173`, with smaller `Build 172` and `Build 167` pockets still inside that range.",
            "- Start with the dominant pair `dll_family_01` + `launcher_family_01`. It covers 993 wrapper roots, reports `Build 173`, and matches the already-studied Xeno/Xango/XAvenger/Xmas sample.",
            "- Then look at the three one-off DLL outliers: `dll_family_02` (`Alpha Ball/bin`), `dll_family_03` (`Home Sweet Home`), and `dll_family_04` (`Turtle Bay`).",
            "- After that, inspect the small launcher outliers that still use `dll_family_01`, because they may be title-specific wrapper revisions rather than a new DLL generation. The four best targets are the no-literal-build launchers: `Orbz`, `Solitaire 2`, `Tablut`, and `Think Tanks`.",
            "- Use the JSON inventory for exact full hashes and per-root mapping.",
            "",
        ]
    )

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a wrapper-root inventory for the extracted Reflexive Arcade corpus."
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

    inventory = build_inventory(extracted_root)

    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.write_text(render_markdown(inventory, extracted_root) + "\n", encoding="utf-8")
    json_out.write_text(json.dumps(inventory, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    print(f"Wrote {markdown_out}")
    print(f"Wrote {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
