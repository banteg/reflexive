#!/usr/bin/env -S uv run --script
# /// script
# ///

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from .source_layout import display_path, repo_root
from .source_layout import unwrapped_root as source_unwrapped_root


TEXT_PROBE_EXTENSIONS = {
    ".cfg",
    ".cs",
    ".htm",
    ".html",
    ".ini",
    ".md",
    ".py",
    ".rtf",
    ".txt",
    ".xml",
}
BINARY_PROBE_EXTENSIONS = {".assets", ".dcp", ".dll", ".exe", ".ttarch", ".ttarch2"}
RUNTIME_PATTERNS = {
    "SDL": {"sdl.dll", "sdl2.dll", "sdl_image.dll", "sdl_mixer.dll", "sdl_ttf.dll"},
    "BASS": {"bass.dll"},
    "FMOD": {"fmod.dll"},
    "FMOD Ex": {"fmodex.dll"},
    "OpenAL": {"openal32.dll"},
}
ABSENCE_MARKERS = {
    "Adventure Game Studio": {"acsetup.cfg", "agsgame.dat", "audio.vox", "speech.vox"},
    "Cocos2d-x": {"cocos2d.dll", "libcocos2d.dll"},
    "GameMaker": {"data.win", "game.unx", "audiogroup1.dat"},
    "Godot": {"engine.cfg", "project.godot"},
    "Unreal": {"globalshadercache-pc-d3d-sm3.bin", ".u", ".umap", ".upk"},
    "XNA / MonoGame": {".xnb", "microsoft.xna.framework.dll", "microsoft.xna.framework.game.dll"},
}
ENGINE_ORDER = (
    "renpy",
    "unity",
    "telltale_tool",
    "wintermute",
    "rpg_maker_rgss",
    "torque",
    "ogre",
    "irrlicht",
    "popcap_sexyapp",
    "hge",
)
ENGINE_METADATA = {
    "renpy": {
        "label": "Ren'Py",
        "evidence": "`renpy/` runtime tree and launcher scripts mentioning `Ren'Py`.",
    },
    "unity": {
        "label": "Unity",
        "evidence": "`UnityEngine.dll`, `sharedassets*.assets`, and Unity data files.",
    },
    "telltale_tool": {
        "label": "Telltale Tool",
        "evidence": "`.ttarch`/`.ttarch2` archives and embedded `Telltale` strings.",
    },
    "wintermute": {
        "label": "Wintermute Engine",
        "evidence": "`data.dcp`/`packages.dcp` bundles with `Wintermute Engine` strings.",
    },
    "rpg_maker_rgss": {
        "label": "RPG Maker XP / RGSS",
        "evidence": "`RGSS102*.dll` runtimes and `*.rgssad` archives.",
    },
    "torque": {
        "label": "Torque Game Engine",
        "evidence": "`main.cs` scripts whose header names `Torque Game Engine` / `GarageGames`.",
    },
    "ogre": {
        "label": "OGRE",
        "evidence": "`OgreMain.dll` plus OGRE renderer / plugin DLLs.",
    },
    "irrlicht": {
        "label": "Irrlicht",
        "evidence": "`Irrlicht.dll` and the bundled `License/irrlicht.txt` notice.",
    },
    "hge": {
        "label": "Haaf's Game Engine (HGE)",
        "evidence": "`hge.dll` or `Haaf's Game Engine` / `[HGESTRINGTABLE]` markers.",
    },
    "popcap_sexyapp": {
        "label": "PopCap / SexyApp Framework",
        "evidence": "`main.pak` and/or `SexyApp` / `PopCap Framework` markers.",
    },
}
KEYWORD_FEATURES: tuple[tuple[bytes, str, str], ...] = (
    (b"ren'py", "renpy_keyword", "keyword `Ren'Py`"),
    (b"import renpy", "renpy_keyword", "keyword `import renpy`"),
    (b"sexyapp", "popcap_keyword", "keyword `SexyApp`"),
    (b"popcap framework", "popcap_keyword", "keyword `PopCap Framework`"),
    (b"popcap games framework", "popcap_keyword", "keyword `PopCap Games Framework`"),
    (b"telltale", "telltale_keyword", "keyword `Telltale`"),
    (b"wintermute engine", "wintermute_keyword", "keyword `Wintermute Engine`"),
    (b"torque game engine", "torque_keyword", "keyword `Torque Game Engine`"),
    (b"garagegames", "torque_keyword", "keyword `GarageGames`"),
    (b"haaf's game engine", "hge_keyword", "keyword `Haaf's Game Engine`"),
    (b"[hgestringtable]", "hge_keyword", "keyword `[HGESTRINGTABLE]`"),
    (b"hgecreate", "hge_keyword", "keyword `hgeCreate`"),
    (b"irrlicht engine", "irrlicht_keyword", "keyword `Irrlicht Engine`"),
)


def default_unwrapped_root() -> Path:
    return source_unwrapped_root("rutracker")


def default_markdown_path() -> Path:
    return repo_root() / "docs" / "generated" / "rutracker" / "game_engines.md"


def default_json_path() -> Path:
    return repo_root() / "docs" / "generated" / "rutracker" / "game_engines.json"


def add_feature(features: dict[str, list[str]], feature: str, evidence: str) -> None:
    bucket = features.setdefault(feature, [])
    if evidence not in bucket:
        bucket.append(evidence)


def read_probe_bytes(path: Path, chunk_size: int = 1 << 17) -> bytes:
    size = path.stat().st_size
    with path.open("rb") as handle:
        if size <= chunk_size * 2:
            return handle.read()
        head = handle.read(chunk_size)
        handle.seek(max(size - chunk_size, 0))
        tail = handle.read(chunk_size)
    return head + b"\x00" + tail


def should_probe(path: Path, root_path: Path) -> bool:
    relative = path.relative_to(root_path)
    if relative.parts and relative.parts[0].lower() == "license" and path.suffix.lower() == ".txt":
        return True
    if len(relative.parts) == 1:
        return path.suffix.lower() in TEXT_PROBE_EXTENSIONS | BINARY_PROBE_EXTENSIONS
    return path.suffix.lower() in {".dcp", ".ttarch", ".ttarch2"}


def collect_root_record(root_path: Path) -> dict[str, Any]:
    features: dict[str, list[str]] = {}
    runtime_tags: set[str] = set()
    absence_hits: set[str] = set()

    for dirpath, dirnames, filenames in os.walk(root_path):
        base = Path(dirpath)
        for dirname in dirnames:
            rel_dir = str((base / dirname).relative_to(root_path)).replace("\\", "/")
            rel_dir_lower = rel_dir.lower()
            name_lower = dirname.lower()

            if rel_dir_lower == "renpy" or rel_dir_lower.startswith("renpy/"):
                add_feature(features, "renpy_dir", f"directory `{rel_dir}`")
            if rel_dir_lower == "properties" or rel_dir_lower.startswith("properties/"):
                add_feature(features, "popcap_properties_dir", f"directory `{rel_dir}`")

            for label, markers in ABSENCE_MARKERS.items():
                if rel_dir_lower in markers or name_lower in markers:
                    absence_hits.add(label)

        for filename in filenames:
            path = base / filename
            rel_path = str(path.relative_to(root_path)).replace("\\", "/")
            rel_path_lower = rel_path.lower()
            name_lower = filename.lower()
            suffix_lower = path.suffix.lower()

            for runtime_label, names in RUNTIME_PATTERNS.items():
                if name_lower in names:
                    runtime_tags.add(runtime_label)

            for label, markers in ABSENCE_MARKERS.items():
                if rel_path_lower in markers or name_lower in markers or suffix_lower in markers:
                    absence_hits.add(label)

            if name_lower == "hge.dll":
                add_feature(features, "hge_dll", f"file `{rel_path}`")
            if suffix_lower in {".ttarch", ".ttarch2"}:
                add_feature(features, "telltale_archive", f"archive `{rel_path}`")
            if name_lower in {"data.dcp", "packages.dcp", "unbranded.dcp"}:
                add_feature(features, "wintermute_package", f"package `{rel_path}`")
            if name_lower == "main.pak":
                add_feature(features, "popcap_main_pak", f"package `{rel_path}`")
            if name_lower.startswith("rgss") and suffix_lower == ".dll":
                add_feature(features, "rpg_maker_rgss", f"runtime `{rel_path}`")
            if suffix_lower in {".rgssad", ".rgss2a", ".rgss3a"}:
                add_feature(features, "rpg_maker_rgss", f"archive `{rel_path}`")
            if name_lower == "ogremain.dll":
                add_feature(features, "ogre_dll", f"file `{rel_path}`")
            if name_lower == "irrlicht.dll" or rel_path_lower == "license/irrlicht.txt":
                add_feature(features, "irrlicht_file", f"file `{rel_path}`")
            if name_lower == "unityengine.dll":
                add_feature(features, "unity_file", f"file `{rel_path}`")
            if name_lower == "unitydomainload.exe":
                add_feature(features, "unity_file", f"file `{rel_path}`")
            if name_lower.startswith("sharedassets") and suffix_lower == ".assets":
                add_feature(features, "unity_assets", f"asset `{rel_path}`")
            if rel_path_lower == "data/maindata":
                add_feature(features, "unity_assets", f"data file `{rel_path}`")
            if rel_path_lower == "main.cs":
                add_feature(features, "torque_script", f"script `{rel_path}`")
            if name_lower.endswith(".rpy") or name_lower.endswith(".rpyc") or name_lower.endswith(".rpym") or name_lower.endswith(".rpymc"):
                add_feature(features, "renpy_dir", f"script `{rel_path}`")

            if not should_probe(path, root_path):
                continue

            probe = read_probe_bytes(path).lower()
            for keyword, feature, evidence_label in KEYWORD_FEATURES:
                if keyword in probe:
                    add_feature(features, feature, f"{evidence_label} in `{rel_path}`")

    engine_matches: list[dict[str, Any]] = []

    if "renpy_dir" in features or "renpy_keyword" in features:
        engine_matches.append(
            {
                "slug": "renpy",
                "label": ENGINE_METADATA["renpy"]["label"],
                "evidence": features.get("renpy_dir", []) + features.get("renpy_keyword", []),
            }
        )
    if "unity_file" in features or "unity_assets" in features:
        engine_matches.append(
            {
                "slug": "unity",
                "label": ENGINE_METADATA["unity"]["label"],
                "evidence": features.get("unity_file", []) + features.get("unity_assets", []),
            }
        )
    if "telltale_archive" in features or "telltale_keyword" in features:
        engine_matches.append(
            {
                "slug": "telltale_tool",
                "label": ENGINE_METADATA["telltale_tool"]["label"],
                "evidence": features.get("telltale_archive", []) + features.get("telltale_keyword", []),
            }
        )
    if "wintermute_package" in features or "wintermute_keyword" in features:
        engine_matches.append(
            {
                "slug": "wintermute",
                "label": ENGINE_METADATA["wintermute"]["label"],
                "evidence": features.get("wintermute_package", []) + features.get("wintermute_keyword", []),
            }
        )
    if "rpg_maker_rgss" in features:
        engine_matches.append(
            {
                "slug": "rpg_maker_rgss",
                "label": ENGINE_METADATA["rpg_maker_rgss"]["label"],
                "evidence": features.get("rpg_maker_rgss", []),
            }
        )
    if "torque_keyword" in features or "torque_script" in features:
        engine_matches.append(
            {
                "slug": "torque",
                "label": ENGINE_METADATA["torque"]["label"],
                "evidence": features.get("torque_script", []) + features.get("torque_keyword", []),
            }
        )
    if "ogre_dll" in features:
        engine_matches.append(
            {
                "slug": "ogre",
                "label": ENGINE_METADATA["ogre"]["label"],
                "evidence": features.get("ogre_dll", []),
            }
        )
    if "irrlicht_file" in features or "irrlicht_keyword" in features:
        engine_matches.append(
            {
                "slug": "irrlicht",
                "label": ENGINE_METADATA["irrlicht"]["label"],
                "evidence": features.get("irrlicht_file", []) + features.get("irrlicht_keyword", []),
            }
        )
    if "hge_dll" in features or "hge_keyword" in features:
        engine_matches.append(
            {
                "slug": "hge",
                "label": ENGINE_METADATA["hge"]["label"],
                "evidence": features.get("hge_dll", []) + features.get("hge_keyword", []),
            }
        )
    if "popcap_main_pak" in features or "popcap_keyword" in features:
        engine_matches.append(
            {
                "slug": "popcap_sexyapp",
                "label": ENGINE_METADATA["popcap_sexyapp"]["label"],
                "evidence": (
                    features.get("popcap_main_pak", [])
                    + features.get("popcap_keyword", [])
                    + features.get("popcap_properties_dir", [])
                ),
            }
        )

    primary_match = next((match for slug in ENGINE_ORDER for match in engine_matches if match["slug"] == slug), None)

    return {
        "root": root_path.name,
        "engine_matches": engine_matches,
        "primary_engine": primary_match["slug"] if primary_match is not None else None,
        "primary_engine_label": primary_match["label"] if primary_match is not None else None,
        "primary_evidence": primary_match["evidence"][:6] if primary_match is not None else [],
        "runtime_tags": sorted(runtime_tags),
        "absence_hits": sorted(absence_hits),
    }


def build_report(unwrapped_root: Path) -> dict[str, Any]:
    roots = sorted(path for path in unwrapped_root.iterdir() if path.is_dir())
    records = [collect_root_record(root_path) for root_path in roots]

    engine_counter = Counter(
        record["primary_engine"] for record in records if record["primary_engine"] is not None
    )
    runtime_counter = Counter(tag for record in records for tag in record["runtime_tags"])
    absence_counter = Counter(tag for record in records for tag in record["absence_hits"])
    overlap_count = sum(1 for record in records if len(record["engine_matches"]) > 1)
    root_count = len(records)
    classified_count = sum(engine_counter.values())

    engines_summary = []
    for slug in ENGINE_ORDER:
        count = engine_counter.get(slug, 0)
        if count == 0:
            continue
        examples = [record["root"] for record in records if record["primary_engine"] == slug][:8]
        engines_summary.append(
            {
                "slug": slug,
                "label": ENGINE_METADATA[slug]["label"],
                "count": count,
                "share": count / root_count if root_count else 0.0,
                "evidence_basis": ENGINE_METADATA[slug]["evidence"],
                "examples": examples,
            }
        )

    runtime_summary = [
        {
            "label": label,
            "count": count,
            "share": count / root_count if root_count else 0.0,
            "examples": [record["root"] for record in records if label in record["runtime_tags"]][:8],
        }
        for label, count in runtime_counter.most_common()
    ]

    absence_summary = [
        {
            "label": label,
            "count": absence_counter.get(label, 0),
        }
        for label in sorted(ABSENCE_MARKERS)
    ]

    return {
        "summary": {
            "root_count": root_count,
            "classified_root_count": classified_count,
            "unknown_root_count": root_count - classified_count,
            "classified_share": classified_count / root_count if root_count else 0.0,
            "overlap_count": overlap_count,
            "engines": engines_summary,
            "runtime_tags": runtime_summary,
            "absence_markers": absence_summary,
        },
        "roots": records,
    }


def render_markdown(report: dict[str, Any], unwrapped_root: Path, json_path: Path) -> str:
    summary = report["summary"]
    lines = [
        "# RuTracker Game Engine Probe",
        "",
        f"- Scanned unwrapped roots under `{display_path(unwrapped_root)}`.",
        f"- JSON report: `{display_path(json_path)}`.",
        f"- Roots scanned: {summary['root_count']}",
        f"- Confident primary engine assignments: {summary['classified_root_count']} ({summary['classified_share']:.1%})",
        f"- Unclassified roots after this static pass: {summary['unknown_root_count']}",
        f"- Roots matching more than one engine family before precedence: {summary['overlap_count']}",
        "",
        "This pass only counts engine families with direct static evidence. Runtime and audio middleware are reported separately and are not treated as engine assignments.",
        "",
        "## Confirmed Engine Families",
        "",
        "| Engine | Roots | Share | Evidence Basis | Example Roots |",
        "| --- | ---: | ---: | --- | --- |",
    ]

    for item in summary["engines"]:
        examples = ", ".join(f"`{example}`" for example in item["examples"][:4])
        lines.append(
            f"| {item['label']} | {item['count']} | {item['share']:.1%} | {item['evidence_basis']} | {examples} |"
        )

    lines.extend(
        [
            "",
            "## Common Runtime / Middleware Tags",
            "",
            "| Runtime | Roots | Share | Example Roots |",
            "| --- | ---: | ---: | --- |",
        ]
    )

    for item in summary["runtime_tags"]:
        examples = ", ".join(f"`{example}`" for example in item["examples"][:4])
        lines.append(f"| {item['label']} | {item['count']} | {item['share']:.1%} | {examples} |")

    lines.extend(
        [
            "",
            "## Zero-Hit Marker Families",
            "",
            "| Engine Family Marker | Roots |",
            "| --- | ---: |",
        ]
    )

    for item in summary["absence_markers"]:
        if item["count"] == 0:
            lines.append(f"| {item['label']} | {item['count']} |")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--unwrapped-root",
        type=Path,
        default=default_unwrapped_root(),
        help="Path to the unwrapped RuTracker corpus.",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=default_markdown_path(),
        help="Where to write the Markdown report.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=default_json_path(),
        help="Where to write the JSON report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.unwrapped_root)

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.markdown_out.write_text(
        render_markdown(report, args.unwrapped_root, args.json_out),
        encoding="utf-8",
    )

    print(f"wrote {display_path(args.markdown_out)}")
    print(f"wrote {display_path(args.json_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
