#!/usr/bin/env -S uv run --script
# ///
# ///

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FamilyRule:
    family_id: str
    label: str
    confidence: str
    patterns: tuple[str, ...]
    rationale: str


FAMILY_RULES: tuple[FamilyRule, ...] = (
    FamilyRule(
        family_id="popcap",
        label="PopCap",
        confidence="high",
        patterns=(
            "bejeweled",
            "bookworm",
            "peggle",
            "zuma",
            "insaniquarium",
            "feedingfrenzy",
            "chuzzle",
            "pizzafrenzy",
            "heavyweapon",
        ),
        rationale="Recognizable PopCap franchise names in installer filenames.",
    ),
    FamilyRule(
        family_id="playfirst",
        label="PlayFirst",
        confidence="high",
        patterns=(
            "dinerdash",
            "weddingdash",
            "hoteldash",
            "cookingdash",
            "fitnessdash",
            "avenueflo",
            "chocolatier",
            "diarydash",
            "planttycoon",
            "virtualvillagers",
        ),
        rationale="Recognizable PlayFirst franchise names in installer filenames.",
    ),
    FamilyRule(
        family_id="gamehouse",
        label="GameHouse",
        confidence="medium",
        patterns=(
            "collapse",
            "supercollapse",
            "slingo",
            "delicious",
            "dreamday",
            "texttwist",
            "superjigsaw",
            "jigsawboom",
            "littleshop",
        ),
        rationale="Installer names match long-running GameHouse portal lines and adjacent house brands.",
    ),
    FamilyRule(
        family_id="bigfish",
        label="Big Fish Games",
        confidence="high",
        patterns=(
            "mysterycasefiles",
            "hiddenexpedition",
            "azada",
            "drawn",
            "awakening",
            "strimko",
            "plantasia",
            "fishdom",
            "mysticinn",
        ),
        rationale="Installer names match Big Fish signature hidden-object and puzzle lines.",
    ),
    FamilyRule(
        family_id="mumbojumbo",
        label="MumboJumbo",
        confidence="high",
        patterns=("luxor", "7wonders", "chainz", "ricochet", "midasmagic"),
        rationale="Installer names match MumboJumbo house franchises.",
    ),
    FamilyRule(
        family_id="iwin",
        label="iWin",
        confidence="medium",
        patterns=("familyfeud", "jewelquest", "jojosfashionshow", "mahjongquest", "agathachristie"),
        rationale="Installer names match iWin-distributed casual franchises and branded lines.",
    ),
    FamilyRule(
        family_id="alawar",
        label="Alawar",
        confidence="medium",
        patterns=(
            "farmfrenzy",
            "snowy",
            "strikeball",
            "magicball",
            "standofood",
            "nataliebrooks",
            "treasuresofmontezuma",
            "thetreasuresofmontezuma",
            "hyperballoid",
            "alexgordon",
            "beetlebug",
            "fashioncraze",
            "wrapitup",
        ),
        rationale="Installer names match well-known Alawar arcade/time-management lines.",
    ),
    FamilyRule(
        family_id="oberon_realarcade",
        label="Oberon / RealArcade",
        confidence="medium",
        patterns=(
            "scrabble",
            "monopoly",
            "yahtzee",
            "risk",
            "chessmaster",
            "grandmasterchess",
            "kasparovchessmate",
            "mahjongescape",
        ),
        rationale="Installer names align with Oberon/RealArcade board and card catalog lines.",
    ),
    FamilyRule(
        family_id="sandlot",
        label="Sandlot",
        confidence="medium",
        patterns=("ballhalla", "cakemania", "supergranny", "tradewinds", "westward", "wanderingwillows"),
        rationale="Installer names match Sandlot-developed series commonly distributed by casual portals.",
    ),
    FamilyRule(
        family_id="playrix",
        label="Playrix",
        confidence="medium",
        patterns=("4elements", "7lands", "aroundtheworldin80days", "callofatlantis", "gardenscapes", "royalenvoy", "riseofatlantis"),
        rationale="Installer names match Playrix series and recurring branding.",
    ),
    FamilyRule(
        family_id="spiderweb",
        label="Spiderweb Software",
        confidence="high",
        patterns=("avernum", "geneforge", "nethergate", "queensthewish"),
        rationale="Installer names match Spiderweb RPG series.",
    ),
    FamilyRule(
        family_id="sigma_team",
        label="Sigma Team",
        confidence="medium",
        patterns=("alienshooter", "zombieshooter", "alienoutbreak", "aliensky", "alienstars", "astroavenger", "astrofury"),
        rationale="Installer names match Sigma Team shooter lines.",
    ),
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_torrent_path() -> Path:
    return repo_root() / "artifacts" / "rutracker-3687027.torrent"


def default_archive_extracted_root() -> Path:
    return repo_root() / "artifacts" / "extracted" / "archive"


def default_markdown_path() -> Path:
    return repo_root() / "docs" / "generated" / "rutracker" / "publisher_attribution.md"


def default_json_path() -> Path:
    return repo_root() / "docs" / "generated" / "rutracker" / "publisher_attribution.json"


def decode_bencode(buf: bytes, index: int = 0):
    token = buf[index : index + 1]
    if token == b"i":
        end = buf.index(b"e", index)
        return int(buf[index + 1 : end]), end + 1
    if token == b"l":
        items = []
        index += 1
        while buf[index : index + 1] != b"e":
            value, index = decode_bencode(buf, index)
            items.append(value)
        return items, index + 1
    if token == b"d":
        items = {}
        index += 1
        while buf[index : index + 1] != b"e":
            key, index = decode_bencode(buf, index)
            value, index = decode_bencode(buf, index)
            items[key] = value
        return items, index + 1
    colon = buf.index(b":", index)
    size = int(buf[index:colon])
    start = colon + 1
    end = start + size
    return buf[start:end], end


def decode_text(value: bytes) -> str:
    for encoding in ("utf-8", "cp1251", "latin-1"):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            continue
    return value.decode("utf-8", "replace")


def normalize_title(value: str) -> str:
    lowered = value.lower().removesuffix("setup.exe").removesuffix(".exe")
    lowered = lowered.replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "", lowered)


def parse_torrent_files(torrent_path: Path) -> list[dict[str, object]]:
    meta, end = decode_bencode(torrent_path.read_bytes())
    if end != torrent_path.stat().st_size:
        raise ValueError(f"failed to parse complete torrent file: {torrent_path}")

    info = meta[b"info"]
    files = info.get(b"files", [])
    parsed: list[dict[str, object]] = []
    for entry in files:
        path = "/".join(decode_text(part) for part in entry[b"path"])
        parsed.append({"path": path, "length": int(entry[b"length"])})
    return parsed


def collect_archive_titles(extracted_root: Path) -> dict[str, str]:
    titles: dict[str, str] = {}
    for bundle_dir in sorted(extracted_root.iterdir()):
        if not bundle_dir.is_dir() or not bundle_dir.name.startswith("Reflexive Arcade "):
            continue
        for game_dir in sorted(bundle_dir.iterdir()):
            if not game_dir.is_dir():
                continue
            titles[normalize_title(game_dir.name)] = game_dir.name
    return titles


def classify_installer(
    file_name: str,
    archive_titles: dict[str, str],
) -> dict[str, object]:
    normalized = normalize_title(file_name)
    stem = file_name.removesuffix("Setup.exe")

    for rule in FAMILY_RULES:
        for pattern in rule.patterns:
            if normalize_title(pattern) in normalized:
                return {
                    "family_id": rule.family_id,
                    "family_label": rule.label,
                    "confidence": rule.confidence,
                    "method": "series_rule",
                    "matched_pattern": pattern,
                    "rationale": rule.rationale,
                    "archive_overlap": normalized in archive_titles,
                    "archive_title": archive_titles.get(normalized),
                    "file_name": file_name,
                    "title_stem": stem,
                    "normalized_title": normalized,
                }

    if normalized in archive_titles:
        return {
            "family_id": "reflexive_portal_overlap",
            "family_label": "Reflexive Portal Overlap",
            "confidence": "medium",
            "method": "archive_overlap",
            "matched_pattern": None,
            "rationale": "The normalized title is present in the current archive-source Reflexive corpus.",
            "archive_overlap": True,
            "archive_title": archive_titles[normalized],
            "file_name": file_name,
            "title_stem": stem,
            "normalized_title": normalized,
        }

    return {
        "family_id": "unattributed_other",
        "family_label": "Unattributed Other",
        "confidence": "low",
        "method": "fallback",
        "matched_pattern": None,
        "rationale": "No specific family rule matched and the title does not overlap the current archive-source corpus.",
        "archive_overlap": False,
        "archive_title": None,
        "file_name": file_name,
        "title_stem": stem,
        "normalized_title": normalized,
    }


def build_report(torrent_path: Path, archive_extracted_root: Path) -> dict[str, object]:
    torrent_files = parse_torrent_files(torrent_path)
    setup_files = [item for item in torrent_files if str(item["path"]).lower().endswith("setup.exe")]
    archive_titles = collect_archive_titles(archive_extracted_root)

    entries = [classify_installer(str(item["path"]), archive_titles) for item in setup_files]
    entries.sort(key=lambda item: str(item["file_name"]).lower())

    family_counter = Counter(str(item["family_id"]) for item in entries)
    family_examples: dict[str, list[str]] = defaultdict(list)
    family_confidence: dict[str, str] = {}
    family_labels: dict[str, str] = {}
    family_methods: dict[str, Counter[str]] = defaultdict(Counter)
    archive_overlap_counter = Counter(bool(item["archive_overlap"]) for item in entries)
    method_counter = Counter(str(item["method"]) for item in entries)

    for entry in entries:
        family_id = str(entry["family_id"])
        family_labels[family_id] = str(entry["family_label"])
        family_confidence[family_id] = str(entry["confidence"])
        family_methods[family_id][str(entry["method"])] += 1
        if len(family_examples[family_id]) < 12:
            family_examples[family_id].append(str(entry["file_name"]))

    family_summary = []
    for family_id, count in family_counter.most_common():
        family_summary.append(
            {
                "family_id": family_id,
                "family_label": family_labels[family_id],
                "count": count,
                "confidence": family_confidence[family_id],
                "methods": [
                    {"method": method, "count": method_count}
                    for method, method_count in sorted(family_methods[family_id].items())
                ],
                "examples": family_examples[family_id],
            }
        )

    unresolved_examples = [str(entry["file_name"]) for entry in entries if entry["family_id"] == "unattributed_other"][:80]

    return {
        "source_id": "rutracker",
        "generated_from_torrent": str(torrent_path.relative_to(repo_root())),
        "archive_comparison_root": str(archive_extracted_root.relative_to(repo_root())),
        "methodology": {
            "scope": "This is a likely publisher or portal-family attribution pass over rutracker setup installer filenames, not a claim of exact legal rights ownership for every title.",
            "series_rule": "High- or medium-confidence franchise keyword rules assign titles to specific publisher-family buckets such as PopCap, PlayFirst, Big Fish Games, MumboJumbo, iWin, Alawar, Oberon/RealArcade, Sandlot, Playrix, Spiderweb, and Sigma Team.",
            "archive_overlap": "Titles not matched by a specific franchise rule but present in the current archive-source corpus fall back to `Reflexive Portal Overlap`.",
            "fallback": "Titles with neither a series-rule match nor archive overlap fall into `Unattributed Other`.",
        },
        "summary": {
            "setup_installer_count": len(entries),
            "archive_overlap_count": archive_overlap_counter[True],
            "non_archive_count": archive_overlap_counter[False],
            "method_counts": [{"method": method, "count": count} for method, count in sorted(method_counter.items())],
        },
        "family_summary": family_summary,
        "unresolved_examples": unresolved_examples,
        "entries": entries,
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    family_summary = report["family_summary"]
    methodology = report["methodology"]

    lines = [
        "# RuTracker Publisher Attribution",
        "",
        f"- Source id: `{report['source_id']}`",
        f"- Generated from: `{report['generated_from_torrent']}`",
        f"- Archive comparison root: `{report['archive_comparison_root']}`",
        "",
        "## Methodology",
        "",
        f"- {methodology['scope']}",
        f"- {methodology['series_rule']}",
        f"- {methodology['archive_overlap']}",
        f"- {methodology['fallback']}",
        "",
        "## Summary",
        "",
        f"- Setup installers classified: {summary['setup_installer_count']}",
        f"- Titles overlapping the current archive corpus: {summary['archive_overlap_count']}",
        f"- Titles outside the current archive corpus: {summary['non_archive_count']}",
    ]

    for item in summary["method_counts"]:
        lines.append(f"- `{item['method']}` assignments: {item['count']}")

    lines.extend(
        [
            "",
            "## Family Summary",
            "",
            "| Family | Installers | Confidence | Methods | Examples |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )

    for item in family_summary:
        methods = ", ".join(f"`{method['method']}`:{method['count']}" for method in item["methods"])
        examples = ", ".join(f"`{example}`" for example in item["examples"][:4])
        lines.append(
            f"| `{item['family_label']}` | {item['count']} | `{item['confidence']}` | {methods} | {examples} |"
        )

    lines.extend(
        [
            "",
            "## Unattributed Other Samples",
            "",
            "These are titles that did not match a specific publisher-family rule and do not overlap the current archive corpus.",
            "",
        ]
    )
    lines.extend(f"- `{name}`" for name in report["unresolved_examples"])
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a likely publisher-family attribution report for the rutracker installer corpus.")
    parser.add_argument("torrent_path", nargs="?", type=Path, default=default_torrent_path(), help="Path to the rutracker torrent file.")
    parser.add_argument(
        "--archive-extracted-root",
        type=Path,
        default=default_archive_extracted_root(),
        help="Extracted archive-source root used for archive-overlap attribution fallback.",
    )
    parser.add_argument("--markdown-out", type=Path, default=default_markdown_path(), help="Markdown output path.")
    parser.add_argument("--json-out", type=Path, default=default_json_path(), help="JSON output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.torrent_path.resolve(), args.archive_extracted_root.resolve())

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
        f" installers={report['summary']['setup_installer_count']}"
        f" overlap={report['summary']['archive_overlap_count']}"
        f" outside_archive={report['summary']['non_archive_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
