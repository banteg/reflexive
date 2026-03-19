#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pefile"]
# ///

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from . import unwrap
from .source_layout import infer_source_id_from_extracted_root


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_markdown_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "unwrapper.md"


def default_json_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "unwrapper.json"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def child_type(wrapper_root: Path) -> str | None:
    if (wrapper_root / "RAW_001.exe").is_file():
        return "raw_001_exe"
    if (wrapper_root / "RAW_001.dat").is_file():
        return "raw_001_dat"
    if any(wrapper_root.glob("*.RWG")):
        return "rwg"
    return None


def build_report(extracted_root: Path) -> dict[str, Any]:
    module = unwrap
    inventory = module.build_scan(extracted_root)
    records = module.effective_records(inventory["roots"])
    source_id = infer_source_id_from_extracted_root(extracted_root)
    output_shape = (
        "Materialize wrapper-free trees under a source-scoped artifacts/unwrapped/<source_id> root by removing ReflexiveArcade/ content, wrapper launcher copies, encrypted child blobs, RAW_002/RAW_003 wrapper sidecars, and wrapper-only top-level assets such as Background.jpg, button_*.jpg, and wraperr.log."
        if source_id is None
        else f"Materialize wrapper-free trees under artifacts/unwrapped/{source_id} by removing ReflexiveArcade/ content, wrapper launcher copies, encrypted child blobs, RAW_002/RAW_003 wrapper sidecars, and wrapper-only top-level assets such as Background.jpg, button_*.jpg, and wraperr.log."
    )

    strategy_counter: Counter[str] = Counter()
    layout_strategy_counter: Counter[tuple[str, str]] = Counter()
    layout_examples: dict[tuple[str, str], str] = {}
    child_type_counter: Counter[str] = Counter()
    strategy_examples: dict[str, str] = {}
    unsupported_roots: list[dict[str, Any]] = []
    per_root: list[dict[str, Any]] = []

    for record in records:
        wrapper_root = extracted_root / record["root"]
        strategy = module.choose_strategy(record, wrapper_root)
        kind = strategy.kind
        layout = str(record["layout_label"])
        primary = record["primary_wrapper_binary"]
        child_kind = child_type(wrapper_root)

        strategy_counter[kind] += 1
        layout_strategy_counter[(layout, kind)] += 1
        layout_examples.setdefault((layout, kind), str(record["root"]))
        strategy_examples.setdefault(kind, str(record["root"]))
        if child_kind is not None and kind == "static":
            child_type_counter[child_kind] += 1

        entry = {
            "root": str(record["root"]),
            "layout_label": layout,
            "strategy": kind,
            "reason": strategy.reason,
            "wrapper_binary": None if strategy.wrapper_binary is None else display_path(strategy.wrapper_binary),
            "direct_executable": None if strategy.direct_executable is None else display_path(strategy.direct_executable),
            "output_executable_name": strategy.output_executable_name,
            "primary_wrapper_role": None if primary is None else primary["role"],
            "primary_wrapper_path": None if primary is None else primary["path"],
            "child_type": child_kind,
        }
        per_root.append(entry)

        if kind == "unsupported":
            unsupported_roots.append(
                {
                    "root": str(record["root"]),
                    "layout_label": layout,
                    "reason": strategy.reason,
                    "primary_wrapper_role": None if primary is None else primary["role"],
                    "primary_wrapper_path": None if primary is None else primary["path"],
                }
            )

    return {
        "generated_from": display_path(extracted_root),
        "methodology": {
            "static_strategy": "For wrapper roots that carry an encrypted child file (*.RWG, RAW_001.exe, or RAW_001.dat), derive the RAW_002 config seed from the wrapper-side dependency file sizes, decrypt RAW_002 statically, derive the child-payload seed from the encrypted RAW_002 header, and patch the decrypted entrypoint-to-section-end span back into the child PE on disk.",
            "direct_strategy": "For helper and dll-only layouts where a non-wrapper game executable is already present at the top level, carry that executable forward and drop Reflexive wrapper artifacts.",
            "output_shape": output_shape,
            "validation": "The static decryptor matches the earlier runtime-captured outputs byte-for-byte on eight cross-family roots: 10 Days Under The Sea, A Pirates Legend, Diamond Drop, Emperors Mahjong, Home Sweet Home, Astrobatics, Ice Cream Tycoon, and Alpha Ball/bin.",
        },
        "summary": {
            "effective_root_count": len(records),
            "strategy_counts": [{"strategy": key, "count": strategy_counter[key]} for key in sorted(strategy_counter)],
            "static_child_types": [{"child_type": key, "count": child_type_counter[key]} for key in sorted(child_type_counter)],
        },
        "layout_strategy_counts": [
            {
                "layout_label": layout,
                "strategy": strategy,
                "count": count,
                "example": layout_examples[(layout, strategy)],
            }
            for (layout, strategy), count in sorted(layout_strategy_counter.items())
        ],
        "validated_examples": [
            {
                "root": "Reflexive Arcade 0-9/10 Days Under The Sea",
                "strategy": "static",
                "child_type": "rwg",
                "output_executable": "10DaysUnderTheSea.exe",
            },
            {
                "root": "Reflexive Arcade A/A Pirates Legend",
                "strategy": "static",
                "child_type": "raw_001_exe",
                "output_executable": "APiratesLegend.exe",
            },
            {
                "root": "Reflexive Arcade D/Diamond Drop",
                "strategy": "static",
                "child_type": "raw_001_dat",
                "output_executable": "DiamondDrop.exe",
            },
            {
                "root": "Reflexive Arcade E/Emperors Mahjong",
                "strategy": "static",
                "child_type": "rwg",
                "output_executable": "Mahjong.exe",
            },
            {
                "root": "Reflexive Arcade E/Double Trump/Electric",
                "strategy": "direct",
                "child_type": None,
                "output_executable": "Electric.exe",
            },
            {
                "root": "Reflexive Arcade C/Crimsonland",
                "strategy": "direct",
                "child_type": None,
                "output_executable": "crimsonland.exe",
            },
        ],
        "unsupported_roots": unsupported_roots,
        "roots": per_root,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines: list[str] = [
        "# Reflexive Unwrapper",
        "",
        f"Generated from the extracted Reflexive Arcade corpus under `{report['generated_from']}`.",
        "",
        "## Methodology",
        "",
        f"- Static strategy: {report['methodology']['static_strategy']}",
        f"- Direct strategy: {report['methodology']['direct_strategy']}",
        f"- Output shape: {report['methodology']['output_shape']}",
        f"- Validation: {report['methodology']['validation']}",
        "",
        "## Summary",
        "",
        f"- Effective wrapper roots scanned: {summary['effective_root_count']}",
    ]

    for item in summary["strategy_counts"]:
        lines.append(f"- `{item['strategy']}` roots: {item['count']}")

    if summary["static_child_types"]:
        lines.append("- Static child types:")
        for item in summary["static_child_types"]:
            lines.append(f"  - `{item['child_type']}`: {item['count']}")

    lines.extend(
        [
            "",
            "## Layout Strategy Counts",
            "",
            "| Layout | Strategy | Roots | Example |",
            "| --- | --- | ---: | --- |",
        ]
    )

    for item in report["layout_strategy_counts"]:
        lines.append(
            f"| `{item['layout_label']}` | `{item['strategy']}` | {item['count']} | `{item['example']}` |"
        )

    lines.extend(
        [
            "",
            "## Validated Examples",
            "",
            "| Root | Strategy | Child Type | Output Executable |",
            "| --- | --- | --- | --- |",
        ]
    )

    for item in report["validated_examples"]:
        child_type_display = "-" if item["child_type"] is None else f"`{item['child_type']}`"
        lines.append(
            f"| `{item['root']}` | `{item['strategy']}` | {child_type_display} | `{item['output_executable']}` |"
        )

    lines.extend(
        [
            "",
            "## Unsupported Roots",
            "",
            "| Root | Layout | Primary Wrapper Role | Example Wrapper |",
            "| --- | --- | --- | --- |",
        ]
    )

    for item in report["unsupported_roots"]:
        role = "-" if item["primary_wrapper_role"] is None else f"`{item['primary_wrapper_role']}`"
        path = "-" if item["primary_wrapper_path"] is None else f"`{item['primary_wrapper_path']}`"
        lines.append(f"| `{item['root']}` | `{item['layout_label']}` | {role} | {path} |")

    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a support report for the current static Reflexive unwrapper."
    )
    parser.add_argument(
        "extracted_root",
        type=Path,
        help="Root containing extracted Reflexive Arcade directories.",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=None,
        help="Markdown output path. Defaults to docs/generated/<source_id>/unwrapper.md when the source can be inferred.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="JSON output path. Defaults to docs/generated/<source_id>/unwrapper.json when the source can be inferred.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    extracted_root = args.extracted_root.resolve()
    source_id = infer_source_id_from_extracted_root(extracted_root)
    if args.markdown_out is not None:
        markdown_out = args.markdown_out.resolve()
    else:
        if source_id is None:
            raise RuntimeError(f"unable to infer source id from {extracted_root}; pass --markdown-out explicitly")
        markdown_out = default_markdown_path(source_id)
    if args.json_out is not None:
        json_out = args.json_out.resolve()
    else:
        if source_id is None:
            raise RuntimeError(f"unable to infer source id from {extracted_root}; pass --json-out explicitly")
        json_out = default_json_path(source_id)
    report = build_report(extracted_root)

    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.write_text(render_markdown(report) + "\n", encoding="utf-8")
    json_out.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    print(f"Wrote {markdown_out}")
    print(f"Wrote {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
