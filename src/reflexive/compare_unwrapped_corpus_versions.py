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
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pefile


VERSION_PART_RE = re.compile(r"\d+")
SKIP_EXE_NAMES = {"unins000.exe"}
TEXT_EVIDENCE_NAMES = (
    "readme",
    "changelog",
    "release",
    "history",
    "version",
    "whatsnew",
    "what'snew",
)


@dataclass(frozen=True)
class ExeRecord:
    rel_path: str
    size: int
    sha256: str
    pe_timestamp: int | None
    pe_timestamp_utc: str | None
    file_version: str | None
    product_version: str | None
    product_name: str | None
    file_description: str | None


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_archive_root() -> Path:
    return repo_root() / "artifacts" / "unwrapped" / "archive"


def default_rutracker_root() -> Path:
    return repo_root() / "artifacts" / "unwrapped" / "rutracker"


def default_sweep_path() -> Path:
    return repo_root() / "docs" / "generated" / "archive" / "unwrapper_sweep.json"


def default_markdown_path() -> Path:
    return repo_root() / "docs" / "generated" / "comparisons" / "unwrapped_corpus_versions.md"


def default_json_path() -> Path:
    return repo_root() / "docs" / "generated" / "comparisons" / "unwrapped_corpus_versions.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_title(value: str) -> str:
    lowered = value.lower().removesuffix("setup.exe").removesuffix(".exe")
    lowered = lowered.replace("&", "and")
    return "".join(ch for ch in lowered if ch.isalnum())


def utc_timestamp(value: int | None) -> str | None:
    if value is None:
        return None
    return dt.datetime.fromtimestamp(value, dt.UTC).isoformat().replace("+00:00", "Z")


def effective_root_map(archive_root: Path, sweep: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
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

    for bundle_dir in sorted(archive_root.iterdir()):
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
            title_map[normalize_title(game_dir.name)] = resolved

    return title_map, unresolved


def rutracker_root_map(rutracker_root: Path) -> dict[str, str]:
    return {
        normalize_title(path.name): path.name
        for path in sorted(rutracker_root.iterdir())
        if path.is_dir()
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_version_info(path: Path) -> tuple[int | None, dict[str, str]]:
    pe: pefile.PE | None = None
    info: dict[str, str] = {}
    try:
        pe = pefile.PE(str(path), fast_load=True)
        timestamp = int(pe.FILE_HEADER.TimeDateStamp)
        pe.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]]
        )
        for file_info in getattr(pe, "FileInfo", []):
            if getattr(file_info, "Key", b"") != b"StringFileInfo":
                continue
            for string_table in getattr(file_info, "StringTable", []):
                for raw_key, raw_value in string_table.entries.items():
                    decoded_key = raw_key.decode("utf-8", "ignore")
                    decoded_value = raw_value.decode("utf-8", "ignore")
                    if decoded_value:
                        info[decoded_key] = decoded_value
        return timestamp, info
    except pefile.PEFormatError:
        return None, {}
    finally:
        if pe is not None:
            pe.close()


def executable_records(root: Path) -> list[ExeRecord]:
    records: list[ExeRecord] = []
    for path in sorted(root.rglob("*.exe")):
        if not path.is_file() or path.name.lower() in SKIP_EXE_NAMES:
            continue
        timestamp, version_info = extract_version_info(path)
        records.append(
            ExeRecord(
                rel_path=str(path.relative_to(root)),
                size=path.stat().st_size,
                sha256=sha256_file(path),
                pe_timestamp=timestamp,
                pe_timestamp_utc=utc_timestamp(timestamp),
                file_version=version_info.get("FileVersion"),
                product_version=version_info.get("ProductVersion"),
                product_name=version_info.get("ProductName"),
                file_description=version_info.get("FileDescription"),
            )
        )
    return records


def choose_primary_exe(title: str, records: list[ExeRecord]) -> ExeRecord | None:
    if not records:
        return None

    normalized_title = normalize_title(title)

    def score(record: ExeRecord) -> tuple[int, int, int, str]:
        rel_path = Path(record.rel_path)
        stem_normalized = normalize_title(rel_path.stem)
        name_match_rank = 2
        if stem_normalized == normalized_title:
            name_match_rank = 0
        elif stem_normalized in normalized_title or normalized_title in stem_normalized:
            name_match_rank = 1
        depth = len(rel_path.parts) - 1
        return (name_match_rank, depth, -record.size, record.rel_path.lower())

    return min(records, key=score)


def parse_version_tuple(value: str | None) -> tuple[int, ...] | None:
    if not value:
        return None
    parts = tuple(int(match.group(0)) for match in VERSION_PART_RE.finditer(value))
    return parts or None


def compare_primary(
    archive_record: ExeRecord | None,
    rutracker_record: ExeRecord | None,
) -> tuple[str, str | None]:
    if archive_record is None or rutracker_record is None:
        return "missing_primary", "missing primary executable in one corpus"

    if archive_record.sha256 == rutracker_record.sha256:
        return "identical", "primary executable hashes match"

    archive_version = parse_version_tuple(archive_record.file_version) or parse_version_tuple(
        archive_record.product_version
    )
    rutracker_version = parse_version_tuple(rutracker_record.file_version) or parse_version_tuple(
        rutracker_record.product_version
    )

    if archive_version is not None and rutracker_version is not None and archive_version != rutracker_version:
        if archive_version > rutracker_version:
            return "archive_newer", "archive primary executable version is higher"
        return "rutracker_newer", "rutracker primary executable version is higher"

    if archive_record.pe_timestamp is not None and rutracker_record.pe_timestamp is not None:
        if archive_record.pe_timestamp > rutracker_record.pe_timestamp:
            return "archive_newer", "archive primary executable PE timestamp is newer"
        if rutracker_record.pe_timestamp > archive_record.pe_timestamp:
            return "rutracker_newer", "rutracker primary executable PE timestamp is newer"
        return "different_same_timestamp", "primary executable hashes differ but PE timestamps match"

    return "different_unknown", "primary executable hashes differ without comparable version metadata"


def inventory_status(archive_records: list[ExeRecord], rutracker_records: list[ExeRecord]) -> str:
    archive_inventory = {(record.rel_path, record.sha256) for record in archive_records}
    rutracker_inventory = {(record.rel_path, record.sha256) for record in rutracker_records}
    if archive_inventory == rutracker_inventory:
        return "identical"

    archive_paths = {record.rel_path for record in archive_records}
    rutracker_paths = {record.rel_path for record in rutracker_records}
    if archive_paths == rutracker_paths:
        return "same_paths_different_content"
    return "different_paths"


def collect_text_evidence(root: Path) -> list[str]:
    evidence: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        name = path.name.lower()
        stem = path.stem.lower()
        if any(token in stem or token in name for token in TEXT_EVIDENCE_NAMES):
            evidence.append(str(path.relative_to(root)))
    return evidence


def primary_year(record: ExeRecord | None) -> int | None:
    if record is None or record.pe_timestamp is None:
        return None
    return dt.datetime.fromtimestamp(record.pe_timestamp, dt.UTC).year


def corpus_title_records(root_map: dict[str, str], base_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for normalized, relative_root in sorted(root_map.items()):
        root = base_root / relative_root
        executables = executable_records(root)
        primary = choose_primary_exe(Path(relative_root).name, executables)
        records.append(
            {
                "normalized_title": normalized,
                "root": relative_root,
                "primary_exe": None if primary is None else asdict(primary),
                "exe_count": len(executables),
            }
        )
    return records


def build_report(archive_root: Path, rutracker_root: Path, sweep_path: Path) -> dict[str, Any]:
    sweep = load_json(sweep_path)
    archive_map, unresolved_archive_titles = effective_root_map(archive_root, sweep)
    rutracker_map = rutracker_root_map(rutracker_root)

    shared_titles = sorted(set(archive_map) & set(rutracker_map))
    archive_only_titles = sorted(set(archive_map) - set(rutracker_map))
    rutracker_only_titles = sorted(set(rutracker_map) - set(archive_map))

    shared_records: list[dict[str, Any]] = []
    primary_counter: Counter[str] = Counter()
    inventory_counter: Counter[str] = Counter()
    explicit_version_counter: Counter[str] = Counter()

    for normalized in shared_titles:
        archive_relative_root = archive_map[normalized]
        rutracker_relative_root = rutracker_map[normalized]
        archive_game_root = archive_root / archive_relative_root
        rutracker_game_root = rutracker_root / rutracker_relative_root

        archive_records = executable_records(archive_game_root)
        rutracker_records = executable_records(rutracker_game_root)
        archive_primary = choose_primary_exe(Path(archive_relative_root).name, archive_records)
        rutracker_primary = choose_primary_exe(Path(rutracker_relative_root).name, rutracker_records)

        primary_status, primary_reason = compare_primary(archive_primary, rutracker_primary)
        inventory = inventory_status(archive_records, rutracker_records)

        primary_counter[primary_status] += 1
        inventory_counter[inventory] += 1
        if archive_primary and (archive_primary.file_version or archive_primary.product_version):
            explicit_version_counter["archive"] += 1
        if rutracker_primary and (rutracker_primary.file_version or rutracker_primary.product_version):
            explicit_version_counter["rutracker"] += 1

        shared_records.append(
            {
                "normalized_title": normalized,
                "archive_root": archive_relative_root,
                "rutracker_root": rutracker_relative_root,
                "archive_exe_count": len(archive_records),
                "rutracker_exe_count": len(rutracker_records),
                "archive_primary": None if archive_primary is None else asdict(archive_primary),
                "rutracker_primary": None if rutracker_primary is None else asdict(rutracker_primary),
                "primary_status": primary_status,
                "primary_reason": primary_reason,
                "inventory_status": inventory,
                "archive_text_evidence": collect_text_evidence(archive_game_root),
                "rutracker_text_evidence": collect_text_evidence(rutracker_game_root),
            }
        )

    archive_primary_records = corpus_title_records(archive_map, archive_root)
    rutracker_primary_records = corpus_title_records(rutracker_map, rutracker_root)

    def year_span(records: list[dict[str, Any]]) -> dict[str, int | None]:
        years = [
            primary_year(
                None
                if item["primary_exe"] is None
                else ExeRecord(**item["primary_exe"])
            )
            for item in records
        ]
        values = sorted(year for year in years if year is not None)
        return {
            "min_year": values[0] if values else None,
            "max_year": values[-1] if values else None,
        }

    return {
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
        "archive_root": str(archive_root),
        "rutracker_root": str(rutracker_root),
        "summary": {
            "archive_title_count": len(archive_map),
            "rutracker_title_count": len(rutracker_map),
            "shared_title_count": len(shared_titles),
            "archive_only_title_count": len(archive_only_titles),
            "rutracker_only_title_count": len(rutracker_only_titles),
            "primary_status_counts": [
                {"status": status, "count": count} for status, count in sorted(primary_counter.items())
            ],
            "inventory_status_counts": [
                {"status": status, "count": count} for status, count in sorted(inventory_counter.items())
            ],
            "primary_version_resource_counts": [
                {"corpus": corpus, "count": count} for corpus, count in sorted(explicit_version_counter.items())
            ],
            "archive_primary_year_span": year_span(archive_primary_records),
            "rutracker_primary_year_span": year_span(rutracker_primary_records),
            "unresolved_archive_titles": len(unresolved_archive_titles),
        },
        "shared_records": shared_records,
        "archive_only_titles": archive_only_titles,
        "rutracker_only_titles": rutracker_only_titles,
        "unresolved_archive_titles": unresolved_archive_titles,
        "archive_title_records": archive_primary_records,
        "rutracker_title_records": rutracker_primary_records,
    }


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    summary = report["summary"]
    differing_shared = [
        entry
        for entry in report["shared_records"]
        if entry["primary_status"] != "identical" or entry["inventory_status"] != "identical"
    ]
    differing_shared.sort(
        key=lambda entry: (
            entry["primary_status"],
            entry["archive_root"].lower(),
        )
    )

    archive_only_examples = report["archive_only_titles"][:20]
    rutracker_only_examples = report["rutracker_only_titles"][:20]

    lines = [
        "# Unwrapped Corpus Version Comparison",
        "",
        f"- Generated: `{report['generated_at_utc']}`",
        f"- Archive root: `{report['archive_root']}`",
        f"- RuTracker root: `{report['rutracker_root']}`",
        "",
        "## Summary",
        "",
        f"- Archive titles: {summary['archive_title_count']}",
        f"- RuTracker titles: {summary['rutracker_title_count']}",
        f"- Shared titles: {summary['shared_title_count']}",
        f"- Archive-only titles: {summary['archive_only_title_count']}",
        f"- RuTracker-only titles: {summary['rutracker_only_title_count']}",
        f"- Archive primary PE year span: {summary['archive_primary_year_span']['min_year']}..{summary['archive_primary_year_span']['max_year']}",
        f"- RuTracker primary PE year span: {summary['rutracker_primary_year_span']['min_year']}..{summary['rutracker_primary_year_span']['max_year']}",
        f"- Unresolved archive title roots: {summary['unresolved_archive_titles']}",
        "",
        "### Shared Title Primary Executable Status",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]

    for item in summary["primary_status_counts"]:
        lines.append(f"| `{item['status']}` | {item['count']} |")

    lines.extend(
        [
            "",
            "### Shared Title Executable Inventory Status",
            "",
            "| Status | Count |",
            "| --- | ---: |",
        ]
    )
    for item in summary["inventory_status_counts"]:
        lines.append(f"| `{item['status']}` | {item['count']} |")

    lines.extend(
        [
            "",
            "### Shared Titles With Differences",
            "",
            "| Archive root | RuTracker root | Primary status | Inventory status | Archive primary | RuTracker primary |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for entry in differing_shared[:100]:
        archive_primary = entry["archive_primary"]
        rutracker_primary = entry["rutracker_primary"]
        archive_label = "none" if archive_primary is None else f"{archive_primary['rel_path']} @ {archive_primary['pe_timestamp_utc']}"
        rutracker_label = "none" if rutracker_primary is None else f"{rutracker_primary['rel_path']} @ {rutracker_primary['pe_timestamp_utc']}"
        lines.append(
            f"| `{entry['archive_root']}` | `{entry['rutracker_root']}` | "
            f"`{entry['primary_status']}` | `{entry['inventory_status']}` | "
            f"`{archive_label}` | `{rutracker_label}` |"
        )

    lines.extend(["", "### Archive-only Title Examples", ""])
    for title in archive_only_examples:
        lines.append(f"- `{title}`")

    lines.extend(["", "### RuTracker-only Title Examples", ""])
    for title in rutracker_only_examples:
        lines.append(f"- `{title}`")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare archive and RuTracker unwrapped corpuses by primary executable metadata "
            "and full executable inventories."
        )
    )
    parser.add_argument("--archive-root", type=Path, default=default_archive_root())
    parser.add_argument("--rutracker-root", type=Path, default=default_rutracker_root())
    parser.add_argument("--sweep-json", type=Path, default=default_sweep_path())
    parser.add_argument("--markdown-out", type=Path, default=default_markdown_path())
    parser.add_argument("--json-out", type=Path, default=default_json_path())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        args.archive_root.resolve(),
        args.rutracker_root.resolve(),
        args.sweep_json.resolve(),
    )
    write_json(args.json_out.resolve(), report)
    write_markdown(args.markdown_out.resolve(), report)
    summary = report["summary"]
    print(
        "Compared"
        f" shared={summary['shared_title_count']}"
        f" archive_only={summary['archive_only_title_count']}"
        f" rutracker_only={summary['rutracker_only_title_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
