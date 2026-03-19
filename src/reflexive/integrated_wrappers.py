#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pefile"]
# ///

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from . import key_inventory, unwrap, wrapper_versions
from .source_layout import display_path, infer_source_id_from_extracted_root, repo_root, source_label


REFLEXIVE_DLL_NAME = "ReflexiveArcade.dll"
RADLL_PREFIX = b"radll_"
LOAD_LIBRARY_NAMES = (b"LoadLibraryA", b"LoadLibraryW")
GET_PROC_ADDRESS_NAME = b"GetProcAddress"


def default_markdown_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "integrated_wrappers.md"


def default_json_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "integrated_wrappers.json"


def structural_candidate(record: dict[str, Any], wrapper_root: Path) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    strategy = unwrap.choose_strategy(record, wrapper_root)
    if strategy.kind != "unsupported":
        reasons.append(f"strategy={strategy.kind}")

    primary = record["primary_wrapper_binary"]
    if primary is None:
        reasons.append("missing primary wrapper binary")
    elif primary["role"] != "top_level_exe":
        reasons.append(f"primary role={primary['role']}")

    if any(candidate["role"] == "launcher_bak" for candidate in record["binary_candidates"]):
        reasons.append("has launcher_bak")
    if any(candidate["role"] == "support_exe" for candidate in record["binary_candidates"]):
        reasons.append("has support_exe")
    if unwrap.choose_child_payload(wrapper_root) is not None:
        reasons.append("has child payload")
    if unwrap.choose_config_path(wrapper_root) is not None:
        reasons.append("has wrapper config")

    return not reasons, reasons


def scan_binding_signals(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    radll_names = sorted(
        {
            chunk.decode("ascii", "ignore")
            for chunk in data.split(b"\x00")
            if chunk.startswith(RADLL_PREFIX)
        }
    )
    references_reflexive_dll = REFLEXIVE_DLL_NAME.encode("ascii") in data
    references_radll_exports = bool(radll_names)
    references_load_library_name = any(name in data for name in LOAD_LIBRARY_NAMES)
    references_get_proc_address_name = GET_PROC_ADDRESS_NAME in data

    if (
        references_reflexive_dll
        and references_radll_exports
        and references_load_library_name
        and references_get_proc_address_name
    ):
        binding_mode = "dynamic_loader"
    elif references_reflexive_dll and references_radll_exports:
        binding_mode = "direct_reflexive_reference"
    else:
        binding_mode = "unclear"

    return {
        "binding_mode": binding_mode,
        "likely_integrated": binding_mode in {"dynamic_loader", "direct_reflexive_reference"},
        "references_reflexive_dll_string": references_reflexive_dll,
        "references_radll_exports": references_radll_exports,
        "radll_export_count": len(radll_names),
        "radll_export_names": radll_names,
        "references_load_library_name": references_load_library_name,
        "references_get_proc_address_name": references_get_proc_address_name,
    }


def scan_support_dll(wrapper_root: Path) -> dict[str, object]:
    support_dll = wrapper_root / "ReflexiveArcade" / "ReflexiveArcade.dll"
    if not support_dll.is_file():
        return {
            "path": None,
            "app_id": None,
            "app_id_hex": None,
            "key_revision": None,
            "modulus_hex": None,
            "errors": ["missing support DLL"],
        }

    errors: list[str] = []
    app_id, app_errors = key_inventory.extract_app_id(support_dll)
    errors.extend(app_errors)
    material, material_errors = key_inventory.extract_embedded_key_material(support_dll.read_bytes())
    errors.extend(material_errors)

    return {
        "path": display_path(support_dll),
        "app_id": app_id,
        "app_id_hex": None if app_id is None else format(app_id, "08X"),
        "key_revision": None if material is None else material.revision,
        "modulus_hex": None if material is None else material.modulus_hex,
        "errors": errors,
    }


def build_report(extracted_root: Path) -> dict[str, Any]:
    source_id = infer_source_id_from_extracted_root(extracted_root)
    scan = wrapper_versions.build_scan(extracted_root)
    effective_records = unwrap.effective_records(scan["roots"])

    layout_counter: Counter[str] = Counter()
    binding_counter: Counter[str] = Counter()
    support_counter: Counter[str] = Counter()
    roots: list[dict[str, Any]] = []

    for record in effective_records:
        wrapper_root = extracted_root / record["root"]
        is_candidate, exclusion_reasons = structural_candidate(record, wrapper_root)
        if not is_candidate:
            continue

        primary = record["primary_wrapper_binary"]
        assert primary is not None
        exe_path = repo_root() / Path(primary["path"])
        binding = scan_binding_signals(exe_path)
        support = scan_support_dll(wrapper_root)

        layout_counter[str(record["layout_label"])] += 1
        binding_counter[str(binding["binding_mode"])] += 1
        if support["app_id"] is not None:
            support_counter["with_app_id"] += 1
        if support["key_revision"] is not None:
            support_counter["with_key_revision"] += 1
        if support["modulus_hex"] is not None:
            support_counter["with_modulus"] += 1

        roots.append(
            {
                "root": str(record["root"]),
                "layout_label": str(record["layout_label"]),
                "primary_executable_path": primary["path"],
                "binding": binding,
                "support_dll": support,
                "candidate_exclusion_reasons": exclusion_reasons,
                "top_level_executables": [
                    candidate["path"]
                    for candidate in record["binary_candidates"]
                    if candidate["role"] == "top_level_exe"
                ],
            }
        )

    likely_roots = [entry for entry in roots if entry["binding"]["likely_integrated"]]
    uncertain_roots = [entry for entry in roots if not entry["binding"]["likely_integrated"]]

    methodology = {
        "structural_filter": "Select effective unwrap roots where the unwrapper has no safe strategy, the primary wrapper binary is the top-level EXE, there is no Reflexive helper EXE, no launcher .exe.BAK, no encrypted child payload, and no RAW_002 wrapper config.",
        "binding_filter": "Treat the top-level EXE as an integrated Reflexive wrapper when it carries either a direct Reflexive binding reference (ReflexiveArcade.dll plus one or more radll_* export-name strings) or the stronger dynamic-loader pattern that also references LoadLibrary* and GetProcAddress.",
        "interpretation": "These roots are not peelable classic wrappers; the game executable itself appears to host the Reflexive binding layer.",
    }
    if source_id is not None:
        methodology["source"] = source_label(source_id)

    return {
        "generated_from": display_path(extracted_root),
        "methodology": methodology,
        "summary": {
            "effective_root_count": len(effective_records),
            "structural_candidate_count": len(roots),
            "likely_integrated_count": len(likely_roots),
            "uncertain_candidate_count": len(uncertain_roots),
            "layout_counts": [{"layout_label": key, "count": layout_counter[key]} for key in sorted(layout_counter)],
            "binding_mode_counts": [{"binding_mode": key, "count": binding_counter[key]} for key in sorted(binding_counter)],
            "support_dll_counts": [{"name": key, "count": support_counter[key]} for key in sorted(support_counter)],
        },
        "likely_integrated_roots": likely_roots,
        "uncertain_roots": uncertain_roots,
    }


def render_root_table(roots: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Root | Layout | Main EXE | Binding | App ID | Rev | radll_* |",
        "| --- | --- | --- | --- | ---: | --- | ---: |",
    ]
    for item in roots:
        binding = item["binding"]
        support = item["support_dll"]
        app_id = "-" if support["app_id"] is None else str(support["app_id"])
        revision = "-" if support["key_revision"] is None else f"`{support['key_revision']}`"
        lines.append(
            f"| `{item['root']}` | `{item['layout_label']}` | `{Path(item['primary_executable_path']).name}` | `{binding['binding_mode']}` | {app_id} | {revision} | {binding['radll_export_count']} |"
        )
    return lines


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Integrated Reflexive Wrappers",
        "",
        f"Generated from `{report['generated_from']}`.",
        "",
        "## Methodology",
        "",
        f"- Structural filter: {report['methodology']['structural_filter']}",
        f"- Binding filter: {report['methodology']['binding_filter']}",
        f"- Interpretation: {report['methodology']['interpretation']}",
        "",
        "## Summary",
        "",
        f"- Effective unwrap roots scanned: {summary['effective_root_count']}",
        f"- Structural candidates: {summary['structural_candidate_count']}",
        f"- Likely integrated wrappers: {summary['likely_integrated_count']}",
        f"- Uncertain candidates: {summary['uncertain_candidate_count']}",
    ]

    if summary["layout_counts"]:
        lines.append("- Layout counts:")
        for item in summary["layout_counts"]:
            lines.append(f"  - `{item['layout_label']}`: {item['count']}")

    if summary["binding_mode_counts"]:
        lines.append("- Binding modes:")
        for item in summary["binding_mode_counts"]:
            lines.append(f"  - `{item['binding_mode']}`: {item['count']}")

    lines.extend(
        [
            "",
            "## Likely Integrated Roots",
            "",
        ]
    )
    lines.extend(render_root_table(report["likely_integrated_roots"]))

    if report["uncertain_roots"]:
        lines.extend(
            [
                "",
                "## Uncertain Candidates",
                "",
            ]
        )
        lines.extend(render_root_table(report["uncertain_roots"]))

    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report likely Reflexive wrappers fused into the main game executable."
    )
    parser.add_argument(
        "extracted_root",
        type=Path,
        help="Root containing extracted Reflexive game directories.",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=None,
        help="Markdown output path. Defaults to docs/generated/<source_id>/integrated_wrappers.md when the source can be inferred.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="JSON output path. Defaults to docs/generated/<source_id>/integrated_wrappers.json when the source can be inferred.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    extracted_root = args.extracted_root.resolve()
    report = build_report(extracted_root)

    markdown_out = args.markdown_out
    json_out = args.json_out

    source_id = infer_source_id_from_extracted_root(extracted_root)
    if markdown_out is None and source_id is not None:
        markdown_out = default_markdown_path(source_id)
    if json_out is None and source_id is not None:
        json_out = default_json_path(source_id)

    markdown_text = render_markdown(report)
    json_text = json.dumps(report, indent=2) + "\n"

    if markdown_out is not None:
        markdown_out.parent.mkdir(parents=True, exist_ok=True)
        markdown_out.write_text(markdown_text, encoding="utf-8")
    if json_out is not None:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json_text, encoding="utf-8")

    summary = report["summary"]
    print(f"effective_roots={summary['effective_root_count']}")
    print(f"structural_candidates={summary['structural_candidate_count']}")
    print(f"likely_integrated={summary['likely_integrated_count']}")
    print(f"uncertain_candidates={summary['uncertain_candidate_count']}")
    if markdown_out is not None:
        print(f"markdown_out={display_path(markdown_out)}")
    if json_out is not None:
        print(f"json_out={display_path(json_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
