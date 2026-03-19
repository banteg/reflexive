#!/usr/bin/env -S uv run --script
from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .source_layout import repo_root as source_repo_root
from .source_layout import source_label
from .source_layout import unwrapped_root as source_unwrapped_root


@dataclass(frozen=True)
class SignalRule:
    tag: str
    weight: int
    phrases: tuple[str, ...]


SIGNAL_RULES: tuple[SignalRule, ...] = (
    SignalRule(
        "code_fields",
        10,
        (
            "product code",
            "registration code",
            "unlock code",
            "activation code",
        ),
    ),
    SignalRule(
        "serial_or_key",
        8,
        (
            "serial number",
            "serial code",
            "license key",
            "registration key",
            "unlock key",
            "enter serial",
            "enter registration",
            "enter unlock",
        ),
    ),
    SignalRule(
        "registration_state",
        7,
        (
            "not registered",
            "unregistered",
            "registration information",
            "register now",
            "register today",
        ),
    ),
    SignalRule(
        "trial_or_upsell",
        5,
        (
            "full version",
            "trial version",
            "evaluation copy",
            "evaluation version",
            "buy now",
            "order now",
            "upgrade to full version",
        ),
    ),
    SignalRule(
        "demo_or_presentation",
        4,
        (
            "demo version",
            "presentation version",
            "not for sale",
            "shareware",
        ),
    ),
)


TOKEN_HINTS: tuple[str, ...] = (
    "product",
    "registration",
    "register",
    "unlock",
    "serial",
    "license",
    "activation",
    "trial",
    "evaluation",
    "buy",
    "purchase",
    "order",
    "demo",
    "presentation",
    "sale",
    "shareware",
    "full version",
)

IGNORED_SUBSTRINGS: tuple[str, ...] = (
    "save demo",
    "demo files",
    "*.dem",
    "class not registered",
    "input device not registered",
    "unregistered function",
    "unregistered type library",
    "created by unregistered swfkit",
    "device serial number",
    "machineinformation",
)

COARSE_ASCII_HINTS: tuple[bytes, ...] = tuple(hint.encode("ascii") for hint in TOKEN_HINTS)
COARSE_UTF16_HINTS: tuple[bytes, ...] = tuple(hint.encode("utf-16le") for hint in TOKEN_HINTS)
PRINTABLE_ASCII = set(range(0x20, 0x7F))
MAX_EVIDENCE_LENGTH = 200


def repo_root() -> Path:
    return source_repo_root()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def infer_source_id_from_sweep(sweep_json_path: Path, report: dict[str, object]) -> str | None:
    output_root = report.get("output_root")
    if isinstance(output_root, str):
        output_path = repo_root() / output_root
        parent = repo_root() / "artifacts" / "unwrapped"
        try:
            relative = output_path.resolve().relative_to(parent.resolve())
            if relative.parts:
                return relative.parts[0]
        except ValueError:
            pass

    generated_from = report.get("generated_from")
    if isinstance(generated_from, str):
        extracted_path = repo_root() / generated_from
        parent = repo_root() / "artifacts" / "extracted"
        try:
            relative = extracted_path.resolve().relative_to(parent.resolve())
            if relative.parts:
                return relative.parts[0]
        except ValueError:
            pass

    return None


def infer_source_id_from_unwrapped_root(path: Path) -> str | None:
    try:
        relative = path.resolve().relative_to((repo_root() / "artifacts" / "unwrapped").resolve())
    except ValueError:
        return None
    if not relative.parts:
        return None
    return relative.parts[0]


def default_markdown_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "native_registration_scan.md"


def default_json_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "native_registration_scan.json"


def maybe_has_signal_bytes(data: bytes) -> bool:
    lowered = data.lower()
    return any(hint in lowered for hint in COARSE_ASCII_HINTS) or any(hint in lowered for hint in COARSE_UTF16_HINTS)


def extract_ascii_string(data: bytes, offset: int) -> str:
    start = offset
    while start > 0 and data[start - 1] in PRINTABLE_ASCII:
        start -= 1
    end = offset
    while end < len(data) and data[end] in PRINTABLE_ASCII:
        end += 1
    return " ".join(data[start:end].decode("ascii", "ignore").split())


def extract_utf16_string(data: bytes, offset: int) -> str:
    start = offset - (offset % 2)
    while start >= 2 and data[start - 2] in PRINTABLE_ASCII and data[start - 1] == 0:
        start -= 2
    end = offset - (offset % 2)
    while end + 1 < len(data) and data[end] in PRINTABLE_ASCII and data[end + 1] == 0:
        end += 2
    return " ".join(data[start:end].decode("utf-16le", "ignore").split())


def normalize_evidence(value: str) -> str | None:
    lowered = value.casefold()
    if any(ignore in lowered for ignore in IGNORED_SUBSTRINGS):
        return None
    if len(value) > 400 and value.count("*") > 25:
        return None
    if len(value) > MAX_EVIDENCE_LENGTH:
        return value[: MAX_EVIDENCE_LENGTH - 3].rstrip() + "..."
    return value


def phrase_hits(data: bytes, phrase: str) -> list[str]:
    lowered = data.lower()
    ascii_phrase = phrase.encode("ascii")
    utf16_phrase = phrase.encode("utf-16le")
    hits: list[str] = []
    seen: set[str] = set()

    offset = lowered.find(ascii_phrase)
    while offset != -1 and len(hits) < 3:
        evidence = normalize_evidence(extract_ascii_string(data, offset))
        if evidence and evidence not in seen:
            hits.append(evidence)
            seen.add(evidence)
        offset = lowered.find(ascii_phrase, offset + 1)

    offset = lowered.find(utf16_phrase)
    while offset != -1 and len(hits) < 3:
        evidence = normalize_evidence(extract_utf16_string(data, offset))
        if evidence and evidence not in seen:
            hits.append(evidence)
            seen.add(evidence)
        offset = lowered.find(utf16_phrase, offset + 2)

    return hits


def classify_signals(data: bytes) -> tuple[int, list[dict[str, object]]]:
    score = 0
    signals: list[dict[str, object]] = []

    for rule in SIGNAL_RULES:
        matches: list[str] = []
        for phrase in rule.phrases:
            matches.extend(phrase_hits(data, phrase))
            if len(matches) >= 3:
                break
        deduped: list[str] = []
        seen: set[str] = set()
        for match in matches:
            if match in seen:
                continue
            seen.add(match)
            deduped.append(match)
            if len(deduped) >= 3:
                break
        if not deduped:
            continue
        signals.append(
            {
                "tag": rule.tag,
                "weight": rule.weight,
                "matches": deduped,
            }
        )
        score += rule.weight

    return score, signals


def severity_for(score: int, signals: list[dict[str, object]]) -> str:
    tags = {str(signal["tag"]) for signal in signals}
    if "code_fields" in tags or score >= 18:
        return "high"
    if score >= 10 or ("serial_or_key" in tags and "trial_or_upsell" in tags):
        return "medium"
    return "low"


def build_report(sweep_json_path: Path, unwrapped_root: Path) -> dict[str, object]:
    sweep = json.loads(sweep_json_path.read_text())
    source_id = infer_source_id_from_sweep(sweep_json_path, sweep)
    roots = sweep["ok_roots"]

    suspicious: list[dict[str, object]] = []
    missing_outputs: list[str] = []
    severity_counter: Counter[str] = Counter()
    signal_counter: Counter[str] = Counter()

    for item in roots:
        output_executable = item.get("output_executable")
        if not output_executable:
            continue

        root = str(item["root"])
        executable_path = unwrapped_root / root / output_executable
        if not executable_path.exists():
            missing_outputs.append(root)
            continue

        data = executable_path.read_bytes()
        if not maybe_has_signal_bytes(data):
            continue

        score, signals = classify_signals(data)
        if not signals:
            continue

        severity = severity_for(score, signals)
        severity_counter[severity] += 1
        for signal in signals:
            signal_counter[str(signal["tag"])] += 1
        suspicious.append(
            {
                "root": root,
                "strategy": item["strategy"],
                "output_executable": str(output_executable),
                "score": score,
                "severity": severity,
                "signals": signals,
            }
        )

    suspicious.sort(key=lambda item: (-int(item["score"]), str(item["root"]).lower()))
    missing_outputs.sort()

    return {
        "generated_from": display_path(sweep_json_path),
        "source_id": source_id,
        "source_label": source_label(source_id),
        "unwrapped_root": display_path(unwrapped_root),
        "summary": {
            "effective_root_count": int(sweep["summary"]["effective_root_count"]),
            "ok_root_count": int(sweep["summary"]["ok_count"]),
            "suspicious_root_count": len(suspicious),
            "missing_output_count": len(missing_outputs),
            "severity_counts": [
                {"severity": severity, "count": severity_counter[severity]}
                for severity in ("high", "medium", "low")
                if severity_counter[severity]
            ],
            "signal_counts": [
                {"tag": tag, "count": signal_counter[tag]}
                for tag in sorted(signal_counter)
            ],
        },
        "suspicious_roots": suspicious,
        "missing_outputs": missing_outputs,
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    lines = [
        "# Native Registration Signal Scan",
        "",
        f"Executed against `{report['unwrapped_root']}` using primary output executables from `{report['generated_from']}`.",
        "",
        "This is a heuristic scan for strings that suggest a game may still implement its own",
        "registration, trial, or upsell logic even after Reflexive wrapper removal.",
        "",
        "## Summary",
        "",
        f"- Source: `{report['source_id']}` ({report['source_label']})",
        f"- Successful unwrapped roots considered: {summary['ok_root_count']}",
        f"- Roots with suspicious native-registration signals: {summary['suspicious_root_count']}",
        f"- Missing output executables while scanning: {summary['missing_output_count']}",
    ]

    if summary["severity_counts"]:
        lines.append("- Suspicious roots by severity:")
        for item in summary["severity_counts"]:
            lines.append(f"  - `{item['severity']}`: {item['count']}")

    if summary["signal_counts"]:
        lines.append("- Signal hits by tag:")
        for item in summary["signal_counts"]:
            lines.append(f"  - `{item['tag']}`: {item['count']}")

    lines.extend(
        [
            "",
            "## Suspicious Roots",
            "",
            "| Root | Severity | Score | Strategy | Output Executable | Signal Tags | Evidence |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    for item in report["suspicious_roots"]:
        signal_tags = ", ".join(f"`{signal['tag']}`" for signal in item["signals"])
        evidence: list[str] = []
        for signal in item["signals"]:
            evidence.extend(f"`{match}`" for match in signal["matches"][:1])
        evidence_cell = "<br>".join(evidence[:4])
        lines.append(
            f"| `{item['root']}` | `{item['severity']}` | `{item['score']}` | `{item['strategy']}` | "
            f"`{item['output_executable']}` | {signal_tags} | {evidence_cell} |"
        )

    if report["missing_outputs"]:
        lines.extend(
            [
                "",
                "## Missing Outputs",
                "",
            ]
        )
        for root in report["missing_outputs"]:
            lines.append(f"- `{root}`")

    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan unwrapped executables for strings that suggest native registration or trial logic."
    )
    parser.add_argument(
        "--sweep-json",
        type=Path,
        required=True,
        help="Unwrapper sweep JSON that supplies the root list and primary output executable names.",
    )
    parser.add_argument(
        "--unwrapped-root",
        type=Path,
        default=None,
        help="Root containing materialized unwrapped game trees. Defaults to artifacts/unwrapped/<source_id>.",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=None,
        help="Markdown report output path. Defaults to docs/generated/<source_id>/native_registration_scan.md.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="JSON report output path. Defaults to docs/generated/<source_id>/native_registration_scan.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sweep_json = args.sweep_json.resolve()
    sweep = json.loads(sweep_json.read_text())
    source_id = infer_source_id_from_sweep(sweep_json, sweep)
    if source_id is None and args.unwrapped_root is not None:
        source_id = infer_source_id_from_unwrapped_root(args.unwrapped_root)

    if args.unwrapped_root is not None:
        unwrapped_root = args.unwrapped_root.resolve()
    else:
        if source_id is None:
            raise RuntimeError(f"unable to infer source id from {sweep_json}; pass --unwrapped-root explicitly")
        unwrapped_root = source_unwrapped_root(source_id)

    if args.markdown_out is not None:
        markdown_out = args.markdown_out.resolve()
    else:
        if source_id is None:
            raise RuntimeError(f"unable to infer source id from {sweep_json}; pass --markdown-out explicitly")
        markdown_out = default_markdown_path(source_id)
    if args.json_out is not None:
        json_out = args.json_out.resolve()
    else:
        if source_id is None:
            raise RuntimeError(f"unable to infer source id from {sweep_json}; pass --json-out explicitly")
        json_out = default_json_path(source_id)

    report = build_report(sweep_json, unwrapped_root)
    markdown = render_markdown(report)

    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.write_text(markdown)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2))

    print(f"Wrote {markdown_out}")
    print(f"Wrote {json_out}")
    print(
        "Summary:",
        f"suspicious={report['summary']['suspicious_root_count']}",
        f"missing={report['summary']['missing_output_count']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
