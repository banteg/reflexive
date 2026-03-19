#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pefile"]
# ///

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pefile

from . import rutracker_publisher_attribution
from .source_layout import display_path, repo_root


INSTALLER_MARKERS: tuple[tuple[str, str, tuple[bytes, ...]], ...] = (
    ("smart_install_maker", "Smart Install Maker", (b"smart install maker v",)),
    ("inno_setup", "Inno Setup signature", (b"inno setup setup data", b"inno setup")),
    ("nsis", "NSIS", (b"nullsoftinst", b"nsis error")),
    ("installshield", "InstallShield", (b"installshield",)),
    ("wise", "Wise Installer", (b"wise installation wizard", b"wise installer")),
    ("setup_factory", "Setup Factory", (b"setup factory",)),
    ("7zip_sfx", "7-Zip SFX", (b"7zs.sfx", b";!@install@!utf-8!")),
    ("rar_sfx", "RAR SFX", (b"rarsfx", b"winrar sfx")),
)
OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
PE_MAGIC = b"MZ"
MARKER_NEEDLES: tuple[bytes, ...] = (
    b"Inno Setup Setup Data (5.2.3)",
    b"Inno Setup Messages (5.1.11)",
    b"CHANNEL_NAME=Reflexive",
)


def default_source_root() -> Path:
    return repo_root() / "artifacts" / "sources" / "rutracker"


def default_torrent_path() -> Path:
    return repo_root() / "artifacts" / "rutracker-3687027.torrent"


def default_archive_extracted_root() -> Path:
    return repo_root() / "artifacts" / "extracted" / "archive"


def default_sweep_json() -> Path:
    return repo_root() / "docs" / "generated" / "archive" / "unwrapper_sweep.json"


def default_wrapper_json() -> Path:
    return repo_root() / "docs" / "generated" / "archive" / "wrapper_versions.json"


def default_markdown_path() -> Path:
    return repo_root() / "docs" / "generated" / "rutracker" / "probe.md"


def default_json_path() -> Path:
    return repo_root() / "docs" / "generated" / "rutracker" / "probe.json"


def load_attribution_report(torrent_path: Path, archive_extracted_root: Path) -> dict[str, Any]:
    return rutracker_publisher_attribution.build_report(torrent_path, archive_extracted_root)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def effective_root_map(archive_extracted_root: Path, sweep: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    status_roots = {row["root"] for row in sweep["ok_roots"]}
    status_roots.update(row["root"] for row in sweep["unsupported_roots"])
    sorted_status_roots = sorted(status_roots)

    def effective_root(game_root: str) -> str | None:
        if game_root in status_roots:
            return game_root
        prefix = game_root + "/"
        matches = [root for root in sorted_status_roots if root.startswith(prefix)]
        if len(matches) == 1:
            return matches[0]
        return None

    title_map: dict[str, str] = {}
    unresolved: list[str] = []

    for bundle_dir in sorted(archive_extracted_root.iterdir()):
        if not bundle_dir.is_dir() or not bundle_dir.name.startswith("Reflexive Arcade "):
            continue
        for game_dir in sorted(bundle_dir.iterdir()):
            if not game_dir.is_dir():
                continue
            game_root = f"{bundle_dir.name}/{game_dir.name}"
            resolved = effective_root(game_root)
            if resolved is None:
                unresolved.append(game_root)
                continue
            normalized = normalize_title(game_dir.name)
            title_map[normalized] = resolved

    return title_map, unresolved


def normalize_title(value: str) -> str:
    lowered = value.lower().removesuffix("setup.exe").removesuffix(".exe")
    lowered = lowered.replace("&", "and")
    return "".join(ch for ch in lowered if ch.isalnum())


def collect_overlap_analysis(
    attribution_report: dict[str, Any],
    sweep: dict[str, Any],
    wrapper_report: dict[str, Any],
    title_to_root: dict[str, str],
) -> dict[str, Any]:
    status_by_root = {row["root"]: row["strategy"] for row in sweep["ok_roots"]}
    status_by_root.update({row["root"]: "unsupported" for row in sweep["unsupported_roots"]})
    wrapper_by_root = {row["root"]: row for row in wrapper_report["roots"]}

    overlap_entries: list[dict[str, Any]] = []
    unmatched_archive_overlap: list[str] = []
    unsupported_titles: list[dict[str, str]] = []
    strategy_counter: Counter[str] = Counter()
    layout_counter: Counter[str] = Counter()
    build_counter: Counter[str] = Counter()
    dll_major_counter: Counter[str] = Counter()
    family_counter: Counter[str] = Counter()

    for entry in attribution_report["entries"]:
        normalized = str(entry["normalized_title"])
        if not entry["archive_overlap"]:
            continue

        effective_root = title_to_root.get(normalized)
        if effective_root is None:
            unmatched_archive_overlap.append(str(entry["file_name"]))
            continue

        wrapper_record = wrapper_by_root[effective_root]
        support_dll = wrapper_record.get("support_dll") or {}
        primary_wrapper = wrapper_record.get("primary_wrapper_binary") or {}
        builds = primary_wrapper.get("builds") or []
        build_value = str(builds[0]) if builds else "none"
        dll_major = support_dll.get("major_version")
        dll_major_value = "none" if dll_major is None else str(dll_major)
        strategy = status_by_root[effective_root]
        family_label = str(entry["family_label"])

        strategy_counter[strategy] += 1
        layout_counter[str(wrapper_record["layout_label"])] += 1
        build_counter[build_value] += 1
        dll_major_counter[dll_major_value] += 1
        family_counter[family_label] += 1

        overlap_entry = {
            "file_name": entry["file_name"],
            "family_label": family_label,
            "archive_title": entry["archive_title"],
            "effective_root": effective_root,
            "strategy": strategy,
            "layout_label": wrapper_record["layout_label"],
            "dll_major_version": dll_major,
            "launcher_build": builds[0] if builds else None,
        }
        overlap_entries.append(overlap_entry)

        if strategy == "unsupported":
            unsupported_titles.append(
                {
                    "file_name": str(entry["file_name"]),
                    "effective_root": effective_root,
                    "family_label": family_label,
                }
            )

    overlap_entries.sort(key=lambda item: str(item["file_name"]).lower())
    unsupported_titles.sort(key=lambda item: item["file_name"].lower())
    unmatched_archive_overlap.sort(key=str.lower)

    return {
        "summary": {
            "manifest_overlap_count": attribution_report["summary"]["archive_overlap_count"],
            "effective_overlap_count": len(overlap_entries),
            "ready_now_count": strategy_counter["static"] + strategy_counter["direct"],
            "strategy_counts": [{"strategy": key, "count": count} for key, count in sorted(strategy_counter.items())],
            "layout_counts": [{"layout": key, "count": count} for key, count in layout_counter.most_common()],
            "launcher_build_counts": [{"build": key, "count": count} for key, count in build_counter.most_common()],
            "dll_major_counts": [{"major_version": key, "count": count} for key, count in sorted(dll_major_counter.items())],
            "family_counts": [{"family_label": key, "count": count} for key, count in family_counter.most_common()],
            "unmatched_manifest_overlap_count": len(unmatched_archive_overlap),
        },
        "unsupported_titles": unsupported_titles,
        "unmatched_manifest_overlap": unmatched_archive_overlap,
    }


def extract_version_info(path: Path) -> dict[str, str]:
    info: dict[str, str] = {}
    pe: pefile.PE | None = None
    try:
        pe = pefile.PE(str(path), fast_load=True)
        pe.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]]
        )
        for file_info in getattr(pe, "FileInfo", []):
            key = getattr(file_info, "Key", b"")
            if key != b"StringFileInfo":
                continue
            for string_table in getattr(file_info, "StringTable", []):
                for raw_key, raw_value in string_table.entries.items():
                    decoded_key = raw_key.decode("utf-8", "ignore")
                    decoded_value = raw_value.decode("utf-8", "ignore")
                    if decoded_value:
                        info[decoded_key] = decoded_value
    except pefile.PEFormatError:
        return {}
    finally:
        if pe is not None:
            pe.close()
    return info


def read_probe_bytes(path: Path, chunk_size: int = 1 << 20) -> bytes:
    size = path.stat().st_size
    with path.open("rb") as handle:
        if size <= chunk_size * 2:
            return handle.read()
        head = handle.read(chunk_size)
        handle.seek(max(size - chunk_size, 0))
        tail = handle.read(chunk_size)
    return head + b"\x00" + tail


def classify_installer_technology(path: Path, blob: bytes) -> dict[str, Any]:
    lowered = blob.lower()
    technology_id = "unknown"
    technology_label = "Unknown"
    evidence: list[str] = []

    if blob.startswith(OLE_MAGIC):
        technology_id = "msi"
        technology_label = "MSI"
        evidence.append("OLE compound file header")
    elif blob.startswith(PE_MAGIC):
        for candidate_id, label, markers in INSTALLER_MARKERS:
            if any(marker in lowered for marker in markers):
                technology_id = candidate_id
                technology_label = label
                evidence.extend(marker.decode("latin1") for marker in markers if marker in lowered)
                break
        else:
            technology_id = "pe_unknown"
            technology_label = "PE Stub (Unknown Installer)"
            evidence.append("MZ header")
    else:
        evidence.append("unrecognized container")

    reflexive_markers = [
        marker
        for marker in (
            b"reflexive",
            b"reflexivearcade",
            b"reflexivearcade.dll",
            b"radll_initialize",
            b"radll_getdllversionasint",
        )
        if marker in lowered
    ]

    return {
        "technology_id": technology_id,
        "technology_label": technology_label,
        "evidence": evidence,
        "has_reflexive_markers": bool(reflexive_markers),
        "reflexive_markers": [marker.decode("latin1") for marker in reflexive_markers],
    }


def probe_live_source(
    source_root: Path,
    attribution_report: dict[str, Any],
    title_to_root: dict[str, str],
    limit: int | None,
) -> dict[str, Any]:
    entry_by_name = {str(entry["file_name"]): entry for entry in attribution_report["entries"]}

    try:
        files = sorted(
            (
                path
                for path in source_root.iterdir()
                if path.is_file() and path.suffix.lower() == ".exe"
            ),
            key=lambda item: item.name.lower(),
        )
    except PermissionError as exc:
        return {"status": "blocked", "error": str(exc)}
    except FileNotFoundError as exc:
        return {"status": "missing", "error": str(exc)}

    if limit is not None:
        files = files[:limit]

    records: list[dict[str, Any]] = []
    technology_counter: Counter[str] = Counter()
    company_counter: Counter[str] = Counter()
    product_counter: Counter[str] = Counter()
    reflexive_marker_counter = 0

    for path in files:
        blob = read_probe_bytes(path)
        technology = classify_installer_technology(path, blob)
        version_info = extract_version_info(path)
        company = version_info.get("CompanyName")
        product = version_info.get("ProductName")
        archive_match = entry_by_name.get(path.name)
        normalized = normalize_title(path.name)

        technology_counter[str(technology["technology_label"])] += 1
        if company:
            company_counter[company] += 1
        if product:
            product_counter[product] += 1
        if technology["has_reflexive_markers"]:
            reflexive_marker_counter += 1

        records.append(
            {
                "file_name": path.name,
                "size": path.stat().st_size,
                "technology_id": technology["technology_id"],
                "technology_label": technology["technology_label"],
                "evidence": technology["evidence"],
                "has_reflexive_markers": technology["has_reflexive_markers"],
                "reflexive_markers": technology["reflexive_markers"],
                "company_name": company,
                "product_name": product,
                "file_description": version_info.get("FileDescription"),
                "archive_overlap": archive_match is not None,
                "effective_root": title_to_root.get(normalized),
                "family_label": archive_match.get("family_label") if archive_match is not None else None,
            }
        )

    return {
        "status": "readable",
        "scanned_installer_count": len(records),
        "summary": {
            "technology_counts": [{"technology": key, "count": count} for key, count in technology_counter.most_common()],
            "company_counts": [{"company_name": key, "count": count} for key, count in company_counter.most_common(15)],
            "product_counts": [{"product_name": key, "count": count} for key, count in product_counter.most_common(15)],
            "has_reflexive_marker_count": reflexive_marker_counter,
        },
        "records": records,
    }


def locate_marker_offsets(path: Path) -> list[dict[str, object]]:
    data = path.read_bytes()
    markers: list[dict[str, object]] = []
    for needle in MARKER_NEEDLES:
        offset = data.find(needle)
        markers.append({"marker": needle.decode("latin1"), "offset": offset if offset >= 0 else None})
    return markers


def command_summary(completed: subprocess.CompletedProcess[str]) -> str:
    chunks: list[str] = []
    for stream in (completed.stdout, completed.stderr):
        for line in stream.splitlines():
            stripped = line.strip()
            if stripped:
                chunks.append(stripped)
    if not chunks:
        return f"exit {completed.returncode}"
    return " | ".join(chunks[:4])


def run_tool_probe(command: list[str]) -> dict[str, object]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
        )
    except FileNotFoundError:
        return {"available": False, "ok": False, "exit_code": None, "summary": "tool not installed"}

    return {
        "available": True,
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
        "summary": command_summary(completed),
    }


def run_seven_zip_probe(seven_zip: str, path: Path) -> dict[str, object]:
    completed = subprocess.run(
        [seven_zip, "l", "-slt", str(path)],
        check=False,
        capture_output=True,
        text=True,
        errors="replace",
    )
    archive_type = None
    files = None
    warnings = None
    data_after_archive = False

    for line in completed.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("Type = "):
            archive_type = stripped.split("=", 1)[1].strip()
        elif stripped.startswith("Files = "):
            files = stripped.split("=", 1)[1].strip()
        elif stripped.startswith("Warnings: "):
            warnings = stripped.split(":", 1)[1].strip()
    combined = completed.stdout + "\n" + completed.stderr
    if "There are data after the end of archive" in combined:
        data_after_archive = True

    if completed.returncode == 0 and archive_type == "zip" and data_after_archive:
        summary = f"tail zip only (files={files or '?'}, warnings={warnings or '1'})"
    else:
        summary = command_summary(completed)

    return {
        "available": True,
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
        "summary": summary,
        "archive_type": archive_type,
        "files": files,
        "warnings": warnings,
        "data_after_archive": data_after_archive,
    }


def sample_extraction_probe(source_root: Path, sample_names: list[str]) -> dict[str, Any]:
    innoextract = shutil.which("innoextract")
    seven_zip = shutil.which("7z")
    records: list[dict[str, Any]] = []

    for file_name in sample_names:
        path = source_root / file_name
        if not path.is_file():
            continue

        marker_offsets = locate_marker_offsets(path)
        inno_result = (
            run_tool_probe([innoextract, "-i", str(path)]) if innoextract is not None else {"available": False, "ok": False, "exit_code": None, "summary": "tool not installed"}
        )
        seven_zip_result = (
            run_seven_zip_probe(seven_zip, path)
            if seven_zip is not None
            else {"available": False, "ok": False, "exit_code": None, "summary": "tool not installed"}
        )

        records.append(
            {
                "file_name": file_name,
                "size": path.stat().st_size,
                "marker_offsets": marker_offsets,
                "innoextract": inno_result,
                "seven_zip": seven_zip_result,
            }
        )

    return {
        "sample_count": len(records),
        "records": records,
    }


def choose_priority_samples(attribution_report: dict[str, Any], overlap_analysis: dict[str, Any]) -> dict[str, list[str]]:
    entry_by_family: dict[str, list[str]] = defaultdict(list)
    for entry in attribution_report["entries"]:
        entry_by_family[str(entry["family_label"])].append(str(entry["file_name"]))

    overlap_supported = [
        str(entry["file_name"])
        for entry in overlap_analysis["unsupported_titles"]
    ]
    supported_overlap_candidates = [
        str(entry["file_name"])
        for entry in attribution_report["entries"]
        if entry["archive_overlap"] and str(entry["family_label"]) == "Reflexive Portal Overlap"
    ]

    def unique_preserving(values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result

    return {
        "known_overlap_supported": unique_preserving(
            [
                "10DaysUnderTheSeaSetup.exe",
                "AlienShooterSetup.exe",
                "FamilyFeudSetup.exe",
                "AbraAcademySetup.exe",
                "AirportManiaSetup.exe",
            ]
            + supported_overlap_candidates
        )[:5],
        "known_overlap_unsupported": unique_preserving(
            [
                "BudRedheadSetup.exe",
                "DigbysDonutsSetup.exe",
                "OrbzSetup.exe",
                "Solitaire2Setup.exe",
                "ThinkTanksSetup.exe",
            ]
            + overlap_supported
        )[:5],
        "non_overlap_publishers": unique_preserving(
            [
                "Bejeweled2DeluxeSetup.exe",
                "DinerDashSetup.exe",
                "MysteryCaseFilesHuntsvilleSetup.exe",
                "LuxorSetup.exe",
                "FarmFrenzySetup.exe",
            ]
            + entry_by_family.get("PopCap", [])
            + entry_by_family.get("PlayFirst", [])
            + entry_by_family.get("Big Fish Games", [])
            + entry_by_family.get("MumboJumbo", [])
            + entry_by_family.get("Alawar", [])
        )[:5],
    }


def build_plan(
    overlap_analysis: dict[str, Any],
    live_probe: dict[str, Any],
    extraction_probe: dict[str, Any] | None,
) -> list[str]:
    summary = overlap_analysis["summary"]
    lines = [
        (
            f"Manifest overlap titles already look favorable: {summary['ready_now_count']} of "
            f"{summary['effective_overlap_count']} effective overlap roots are already unwrap-capable in the "
            "current archive corpus if extraction yields comparable wrapper trees."
        ),
        (
            "The existing static/direct unwrapper path should remain the default for extracted trees that contain "
            "`RAW_001*`, `RAW_002*`, `*.RWG`, or familiar `ReflexiveArcade.dll` layouts."
        ),
        (
            "The main new engineering work is likely installer extraction rather than new decryption logic: "
            "we need to detect the original portal installer families first, then feed their extracted output into "
            "the current wrapper scanner and unwrapper."
        ),
        (
            "The currently known archive-side gaps are concentrated in the integrated-wrapper cohort, so titles that "
            "line up with those roots should be treated as likely post-extraction reversing targets rather than "
            "simple extractor work."
        ),
    ]

    if live_probe["status"] == "readable":
        technologies = ", ".join(
            f"{item['technology']} ({item['count']})"
            for item in live_probe["summary"]["technology_counts"][:5]
        )
        lines.append(
            "Once the live source is readable, extractor work should be split by detected installer technology rather "
            f"than by publisher guesswork. Current top observed technologies: {technologies}."
        )
        if extraction_probe is not None and extraction_probe["records"]:
            tail_zip_samples = [
                row["file_name"]
                for row in extraction_probe["records"]
                if row["seven_zip"].get("data_after_archive")
            ]
            lines.append(
                "Representative overlap and non-overlap samples all expose Reflexive-branded Inno Setup markers, but "
                "standard `innoextract` and `7z` fail on those same installers, so the first new script should target "
                "this Reflexive-customized Inno variant rather than a new wrapper decryption family."
            )
            if tail_zip_samples:
                lines.append(
                    "Where `7z` does succeed, it only reveals a trailing branding ZIP rather than the installer "
                    f"payload itself, as seen in {', '.join(tail_zip_samples[:3])}."
                )
    else:
        lines.append(
            "The live `rutracker` source is still unreadable through the Downloads symlink, so byte-level installer "
            "technology clustering remains blocked until the source is copied repo-local or this app gets access."
        )

    return lines


def build_report(
    source_root: Path,
    torrent_path: Path,
    archive_extracted_root: Path,
    sweep_json: Path,
    wrapper_json: Path,
    live_probe_limit: int | None,
) -> dict[str, Any]:
    attribution_report = load_attribution_report(torrent_path, archive_extracted_root)
    sweep = load_json(sweep_json)
    wrapper_report = load_json(wrapper_json)
    title_to_root, unresolved_archive_titles = effective_root_map(archive_extracted_root, sweep)
    overlap_analysis = collect_overlap_analysis(attribution_report, sweep, wrapper_report, title_to_root)
    live_probe = probe_live_source(source_root, attribution_report, title_to_root, live_probe_limit)
    priority_samples = choose_priority_samples(attribution_report, overlap_analysis)
    extraction_probe_names = (
        priority_samples["known_overlap_supported"][:2]
        + priority_samples["known_overlap_unsupported"][:2]
        + priority_samples["non_overlap_publishers"][:3]
    )
    extraction_probe_names = list(dict.fromkeys(extraction_probe_names))
    extraction_probe = sample_extraction_probe(source_root, extraction_probe_names) if live_probe["status"] == "readable" else None
    plan = build_plan(overlap_analysis, live_probe, extraction_probe)

    return {
        "source_id": "rutracker",
        "generated_from": {
            "source_root": display_path(source_root),
            "torrent_path": display_path(torrent_path),
            "archive_extracted_root": display_path(archive_extracted_root),
            "archive_unwrapper_sweep": display_path(sweep_json),
            "archive_wrapper_versions": display_path(wrapper_json),
        },
        "manifest_summary": attribution_report["summary"],
        "methodology": {
            "manifest": "Use the readable rutracker torrent manifest as the stable installer list and title namespace.",
            "overlap": "Map manifest installer names onto the current archive extracted corpus by normalized title, then translate those matches onto effective unwrap roots.",
            "unwrap_readiness": "Use the archive unwrapper sweep to determine whether a matched title is already handled via `static`, `direct`, or remains `unsupported`.",
            "stub_probe": "When the live rutracker source is readable, classify installer stubs from their container header, embedded marker strings, and PE version metadata.",
        },
        "live_source_probe": live_probe,
        "sample_extraction_probe": extraction_probe,
        "archive_overlap_analysis": overlap_analysis,
        "priority_samples": priority_samples,
        "plan": plan,
        "archive_effective_root_gaps": unresolved_archive_titles,
    }


def render_markdown(report: dict[str, Any]) -> str:
    generated_from = report["generated_from"]
    manifest_summary = report["manifest_summary"]
    overlap_summary = report["archive_overlap_analysis"]["summary"]
    live_probe = report["live_source_probe"]
    extraction_probe = report["sample_extraction_probe"]
    priority_samples = report["priority_samples"]

    lines = [
        "# RuTracker Probe",
        "",
        "- Source id: `rutracker`",
        f"- Source root: `{generated_from['source_root']}`",
        f"- Torrent manifest: `{generated_from['torrent_path']}`",
        f"- Archive comparison root: `{generated_from['archive_extracted_root']}`",
        f"- Archive unwrapper sweep: `{generated_from['archive_unwrapper_sweep']}`",
        f"- Archive wrapper version scan: `{generated_from['archive_wrapper_versions']}`",
        "",
        "## Live Source Status",
        "",
    ]

    if live_probe["status"] == "readable":
        lines.extend(
            [
                "- Live rutracker source is readable.",
                f"- Installer stubs scanned: {live_probe['scanned_installer_count']}",
                f"- Stubs with explicit Reflexive markers: {live_probe['summary']['has_reflexive_marker_count']}",
                "",
                "### Installer Technology Summary",
                "",
                "| Technology | Count |",
                "| --- | ---: |",
            ]
        )
        for item in live_probe["summary"]["technology_counts"]:
            lines.append(f"| `{item['technology']}` | {item['count']} |")

        if live_probe["summary"]["company_counts"]:
            lines.extend(["", "### Top PE Company Names", "", "| Company | Count |", "| --- | ---: |"])
            for item in live_probe["summary"]["company_counts"]:
                lines.append(f"| `{item['company_name']}` | {item['count']} |")

        if extraction_probe is not None:
            lines.extend(
                [
                    "",
                    "### Sample Extraction Results",
                    "",
                    "| Installer | Inno markers | `innoextract -i` | `7z l` |",
                    "| --- | --- | --- | --- |",
                ]
            )
            for item in extraction_probe["records"]:
                markers = ", ".join(
                    f"`{marker['marker']}`@{marker['offset']}"
                    for marker in item["marker_offsets"]
                    if marker["offset"] is not None
                )
                inno_summary = str(item["innoextract"]["summary"]).replace("|", "\\|")
                seven_zip_summary = str(item["seven_zip"]["summary"]).replace("|", "\\|")
                lines.append(
                    f"| `{item['file_name']}` | {markers} | `{inno_summary}` | `{seven_zip_summary}` |"
                )
    else:
        lines.extend(
            [
                f"- Live rutracker source status: `{live_probe['status']}`",
                f"- Probe error: `{live_probe['error']}`",
                "- Byte-level installer classification is deferred until the source becomes readable through a repo-local copy or a permission change.",
            ]
        )

    lines.extend(["", "## Archive Overlap Readiness", ""])
    lines.append(f"- Torrent setup installers: {manifest_summary['setup_installer_count']}")
    lines.append(f"- Title matches against the archive corpus: {overlap_summary['manifest_overlap_count']}")
    lines.append(f"- Effective archive overlap roots with unwrap data: {overlap_summary['effective_overlap_count']}")
    lines.append(f"- Already unwrap-capable if extraction yields familiar layouts: {overlap_summary['ready_now_count']}")
    for item in overlap_summary["strategy_counts"]:
        lines.append(f"- Overlap `{item['strategy']}` roots: {item['count']}")
    lines.append(f"- Overlap titles that matched by name but do not map cleanly onto an effective archive root: {overlap_summary['unmatched_manifest_overlap_count']}")

    lines.extend(["", "### Dominant Overlap Layouts", "", "| Layout | Count |", "| --- | ---: |"])
    for item in overlap_summary["layout_counts"][:8]:
        lines.append(f"| `{item['layout']}` | {item['count']} |")

    lines.extend(["", "### Dominant Overlap Launcher Builds", "", "| Build | Count |", "| --- | ---: |"])
    for item in overlap_summary["launcher_build_counts"][:8]:
        lines.append(f"| `{item['build']}` | {item['count']} |")

    lines.extend(["", "### Dominant Overlap DLL Major Versions", "", "| DLL major | Count |", "| --- | ---: |"])
    for item in overlap_summary["dll_major_counts"]:
        lines.append(f"| `{item['major_version']}` | {item['count']} |")

    lines.extend(["", "## Known Overlap Unsupported Titles", ""])
    if report["archive_overlap_analysis"]["unsupported_titles"]:
        for item in report["archive_overlap_analysis"]["unsupported_titles"]:
            lines.append(
                f"- `{item['file_name']}` -> `{item['effective_root']}`"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## Probe Priorities", ""])
    lines.append("Known overlap titles that should already fit the current unwrapper once extraction works:")
    lines.extend(f"- `{name}`" for name in priority_samples["known_overlap_supported"])
    lines.append("")
    lines.append("Known overlap titles that are likely post-extraction reversing targets:")
    lines.extend(f"- `{name}`" for name in priority_samples["known_overlap_unsupported"])
    lines.append("")
    lines.append("Non-overlap titles worth sampling to see whether rutracker also carries non-Reflexive installer families:")
    lines.extend(f"- `{name}`" for name in priority_samples["non_overlap_publishers"])

    lines.extend(["", "## Plan", ""])
    lines.extend(f"- {line}" for line in report["plan"])
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a RuTracker installer probe report from the local torrent manifest and current archive unwrap data."
    )
    parser.add_argument("--source-root", type=Path, default=default_source_root(), help="Live rutracker source root.")
    parser.add_argument("--torrent-path", type=Path, default=default_torrent_path(), help="RuTracker torrent manifest path.")
    parser.add_argument(
        "--archive-extracted-root",
        type=Path,
        default=default_archive_extracted_root(),
        help="Archive extracted root used for overlap and unwrap readiness analysis.",
    )
    parser.add_argument(
        "--archive-sweep-json",
        type=Path,
        default=default_sweep_json(),
        help="Archive unwrapper sweep JSON path.",
    )
    parser.add_argument(
        "--archive-wrapper-json",
        type=Path,
        default=default_wrapper_json(),
        help="Archive wrapper version JSON path.",
    )
    parser.add_argument(
        "--live-probe-limit",
        type=int,
        default=None,
        help="Optional limit for the number of readable live installer stubs to probe.",
    )
    parser.add_argument("--markdown-out", type=Path, default=default_markdown_path(), help="Markdown output path.")
    parser.add_argument("--json-out", type=Path, default=default_json_path(), help="JSON output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        source_root=args.source_root.resolve(),
        torrent_path=args.torrent_path.resolve(),
        archive_extracted_root=args.archive_extracted_root.resolve(),
        sweep_json=args.archive_sweep_json.resolve(),
        wrapper_json=args.archive_wrapper_json.resolve(),
        live_probe_limit=args.live_probe_limit,
    )

    markdown_out = args.markdown_out.resolve()
    json_out = args.json_out.resolve()
    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.write_text(render_markdown(report), encoding="utf-8")
    json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {markdown_out}")
    print(f"Wrote {json_out}")
    print(
        "Summary:"
        f" overlap={report['archive_overlap_analysis']['summary']['effective_overlap_count']}"
        f" ready_now={report['archive_overlap_analysis']['summary']['ready_now_count']}"
        f" live_source_status={report['live_source_probe']['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
