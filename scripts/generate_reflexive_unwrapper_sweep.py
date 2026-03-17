#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pefile"]
# ///

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from source_layout import DEFAULT_SOURCE_ID
from source_layout import extracted_root as source_extracted_root
from source_layout import infer_source_id_from_extracted_root
from source_layout import unwrapped_root as source_unwrapped_root


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def default_extracted_root() -> Path:
    return source_extracted_root(DEFAULT_SOURCE_ID)


def default_output_root(extracted_root: Path) -> Path:
    source_id = infer_source_id_from_extracted_root(extracted_root)
    if source_id is None:
        return repo_root() / "artifacts" / "unwrapped"
    return source_unwrapped_root(source_id)


def default_markdown_path() -> Path:
    return repo_root() / "docs" / "reflexive_unwrapper_sweep.md"


def default_json_path() -> Path:
    return repo_root() / "docs" / "reflexive_unwrapper_sweep.json"


def load_unwrapper_module() -> Any:
    module_path = repo_root() / "scripts" / "unwrap_reflexive_wrapper.py"
    spec = importlib.util.spec_from_file_location("reflexive_unwrapper", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    success_heading = "Successfully Materialized" if report["mode"] == "materialize" else "Decryptable Roots"
    lines: list[str] = [
        "# Reflexive Unwrapper Sweep",
        "",
        f"Executed against `{report['generated_from']}` in `{report['mode']}` mode.",
        "",
        "## Summary",
        "",
        f"- Effective wrapper roots scanned: {summary['effective_root_count']}",
        f"- Successful roots: {summary['ok_count']}",
        f"- Not yet decryptable roots: {summary['not_decryptable_count']}",
        f"- Reported unsupported: {summary['unsupported_count']}",
        f"- Execution errors: {summary['error_count']}",
    ]

    for item in summary["ok_by_strategy"]:
        lines.append(f"- Successful `{item['strategy']}` roots: {item['count']}")

    if summary["error_by_strategy"]:
        lines.append("- Error roots by predicted strategy:")
        for item in summary["error_by_strategy"]:
            lines.append(f"  - `{item['strategy']}`: {item['count']}")

    lines.extend(
        [
            "",
            f"## {success_heading}",
            "",
            "| Root | Strategy | Output Executable |",
            "| --- | --- | --- |",
        ]
    )
    for item in report["ok_roots"]:
        output_executable = "-" if item["output_executable"] is None else f"`{item['output_executable']}`"
        lines.append(f"| `{item['root']}` | `{item['strategy']}` | {output_executable} |")

    lines.extend(
        [
            "",
            "## Unsupported Roots",
            "",
            "| Root | Strategy | Reason |",
            "| --- | --- | --- |",
        ]
    )
    for item in report["unsupported_roots"]:
        lines.append(f"| `{item['root']}` | `{item['strategy']}` | `{item['reason']}` |")

    lines.extend(
        [
            "",
            "## Error Roots",
            "",
            "| Root | Strategy | Error |",
            "| --- | --- | --- |",
        ]
    )
    for item in report["error_roots"]:
        lines.append(f"| `{item['root']}` | `{item['strategy']}` | `{item['error']}` |")

    lines.append("")
    return "\n".join(lines)


def build_report(extracted_root: Path, output_root: Path, force: bool, probe_only: bool) -> dict[str, Any]:
    module = load_unwrapper_module()
    inventory = module.build_scan(extracted_root)
    records = module.effective_records(inventory["roots"])

    ok_roots: list[dict[str, Any]] = []
    unsupported_roots: list[dict[str, Any]] = []
    error_roots: list[dict[str, Any]] = []
    ok_strategy_counter: Counter[str] = Counter()
    error_strategy_counter: Counter[str] = Counter()

    if not probe_only:
        output_root.mkdir(parents=True, exist_ok=True)

    total = len(records)
    for index, record in enumerate(records, start=1):
        relative_root = Path(record["root"])
        wrapper_root = extracted_root / relative_root
        predicted = module.choose_strategy(record, wrapper_root)
        destination_root = output_root / relative_root

        print(f"[{index}/{total}] {relative_root}")

        try:
            if probe_only:
                if predicted.kind == "unsupported":
                    summary = {
                        "status": "unsupported",
                        "reason": predicted.reason,
                        "strategy": predicted.kind,
                    }
                elif predicted.kind == "direct":
                    summary = {
                        "status": "ok",
                        "strategy": predicted.kind,
                        "output_executable": None if predicted.direct_executable is None else predicted.direct_executable.name,
                    }
                else:
                    probe_summary = module.probe_static_child(wrapper_root, predicted)
                    summary = {
                        "status": "ok",
                        "strategy": predicted.kind,
                        "output_executable": predicted.output_executable_name,
                        **probe_summary,
                    }
            else:
                summary = module.materialize_record(record, extracted_root, output_root, force=force)
        except Exception as exc:
            if not probe_only:
                shutil.rmtree(destination_root, ignore_errors=True)
            error_roots.append(
                {
                    "root": str(relative_root),
                    "strategy": predicted.kind,
                    "error": str(exc),
                }
            )
            error_strategy_counter[predicted.kind] += 1
            continue

        if summary["status"] == "unsupported":
            unsupported_roots.append(
                {
                    "root": str(relative_root),
                    "strategy": predicted.kind,
                    "reason": summary["reason"],
                }
            )
            continue

        ok_roots.append(
            {
                "root": str(relative_root),
                "strategy": summary["strategy"],
                "output_executable": summary.get("output_executable"),
            }
        )
        ok_strategy_counter[summary["strategy"]] += 1

    ok_roots.sort(key=lambda item: item["root"])
    unsupported_roots.sort(key=lambda item: item["root"])
    error_roots.sort(key=lambda item: item["root"])

    return {
        "generated_from": display_path(extracted_root),
        "output_root": display_path(output_root),
        "mode": "probe" if probe_only else "materialize",
        "summary": {
            "effective_root_count": len(records),
            "ok_count": len(ok_roots),
            "not_decryptable_count": len(unsupported_roots) + len(error_roots),
            "unsupported_count": len(unsupported_roots),
            "error_count": len(error_roots),
            "ok_by_strategy": [
                {"strategy": strategy, "count": ok_strategy_counter[strategy]}
                for strategy in sorted(ok_strategy_counter)
            ],
            "error_by_strategy": [
                {"strategy": strategy, "count": error_strategy_counter[strategy]}
                for strategy in sorted(error_strategy_counter)
            ],
        },
        "ok_roots": ok_roots,
        "unsupported_roots": unsupported_roots,
        "error_roots": error_roots,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Reflexive unwrapper across the full extracted corpus and write a sweep report."
    )
    parser.set_defaults(probe_only=True)
    parser.add_argument(
        "--extracted-root",
        type=Path,
        default=default_extracted_root(),
        help="Root containing extracted Reflexive Arcade directories.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Destination root for the materialized wrapper-free game trees. Defaults to artifacts/unwrapped/<source_id>.",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=default_markdown_path(),
        help="Markdown report output path.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=default_json_path(),
        help="JSON report output path.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing per-root outputs.",
    )
    parser.add_argument(
        "--materialize",
        dest="probe_only",
        action="store_false",
        help="Materialize wrapper-free outputs instead of running a probe-only decryptability sweep.",
    )
    parser.add_argument(
        "--probe-only",
        action="store_true",
        help="Validate decryptability without materializing support trees (default).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    extracted_root = args.extracted_root.resolve()
    output_root = args.output_root.resolve() if args.output_root else default_output_root(extracted_root)
    markdown_out = args.markdown_out.resolve()
    json_out = args.json_out.resolve()

    report = build_report(extracted_root, output_root, force=args.force, probe_only=args.probe_only)

    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.write_text(render_markdown(report) + "\n", encoding="utf-8")
    json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {markdown_out}")
    print(f"Wrote {json_out}")
    print(
        "Summary:"
        f" ok={report['summary']['ok_count']}"
        f" unsupported={report['summary']['unsupported_count']}"
        f" error={report['summary']['error_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
