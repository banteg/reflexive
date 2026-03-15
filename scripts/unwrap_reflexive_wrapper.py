#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pefile"]
# ///

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


UTILITY_EXE_NAMES = {
    "controls.exe",
    "config.exe",
    "launcher.exe",
    "play.exe",
    "readme.exe",
    "setup.exe",
    "unins000.exe",
}
TOP_LEVEL_WRAPPER_JUNK = {
    "RA_games.png",
    "ra_trial_dialog.png",
    "wraperr.log",
}


@dataclass(frozen=True)
class Strategy:
    kind: str
    reason: str
    wrapper_binary: Path | None = None
    direct_executable: Path | None = None
    output_executable_name: str | None = None


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_extracted_root() -> Path:
    return repo_root() / "artifacts" / "extracted"


def default_output_root() -> Path:
    return repo_root() / "artifacts" / "unwrapped"


def helper_source_path() -> Path:
    return repo_root() / "scripts" / "reflexive_runtime_unwrapper.c"


def helper_binary_path() -> Path:
    return repo_root() / "artifacts" / "tools" / "reflexive_runtime_unwrapper.exe"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def load_wrapper_scan_module() -> Any:
    module_path = repo_root() / "scripts" / "generate_reflexive_wrapper_versions.py"
    spec = importlib.util.spec_from_file_location("reflexive_wrapper_versions", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_scan(extracted_root: Path) -> dict[str, Any]:
    module = load_wrapper_scan_module()
    return module.build_scan(extracted_root)


def choose_runtime_wrapper(record: dict[str, Any], wrapper_root: Path) -> Path | None:
    candidates: list[tuple[int, Path]] = []

    for candidate in record["binary_candidates"]:
        if not candidate["looks_like_wrapper_binary"]:
            continue

        path = repo_root() / Path(candidate["path"])
        role = str(candidate["role"])
        if role == "top_level_exe":
            priority = 0
        elif role == "launcher_bak":
            priority = 1
        elif role == "support_exe":
            priority = 2
        else:
            priority = 3
        candidates.append((priority, path))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (item[0], item[1].name.lower()))
    chosen = candidates[0][1]

    # Prefer the patched top-level wrapper over the preserved .BAK copy when both exist.
    if chosen.name.lower().endswith(".exe.bak"):
        patched = wrapper_root / chosen.name[:-4]
        if patched.is_file():
            return patched
    return chosen


def choose_direct_executable(record: dict[str, Any], wrapper_root: Path) -> Path | None:
    candidates: list[Path] = []
    score_hints = wrapper_root.name.lower().replace("_", " ").replace("-", " ")

    for candidate in record["binary_candidates"]:
        if candidate["role"] != "top_level_exe" or candidate["looks_like_wrapper_binary"]:
            continue
        path = repo_root() / Path(candidate["path"])
        if path.name.lower() in UTILITY_EXE_NAMES:
            continue
        candidates.append(path)

    if not candidates:
        return None

    def sort_key(path: Path) -> tuple[int, int, int, str]:
        name = path.name.lower()
        stem = path.stem.lower().replace("_", " ").replace("-", " ")
        utility_penalty = 1 if name in UTILITY_EXE_NAMES else 0
        root_hint_penalty = 0 if any(token and token in stem for token in score_hints.split()) else 1
        size_penalty = -path.stat().st_size
        return (utility_penalty, root_hint_penalty, size_penalty, name)

    candidates.sort(key=sort_key)
    return candidates[0]


def runtime_output_name(wrapper_binary: Path) -> str:
    name = wrapper_binary.name
    if name.lower().endswith(".exe.bak"):
        return name[:-4]
    return name


def choose_strategy(record: dict[str, Any], wrapper_root: Path) -> Strategy:
    primary = record["primary_wrapper_binary"]
    runtime_wrapper = choose_runtime_wrapper(record, wrapper_root)
    direct_executable = choose_direct_executable(record, wrapper_root)
    has_runtime_child = any(wrapper_root.glob("*.RWG")) or (wrapper_root / "RAW_001.exe").is_file()

    if has_runtime_child and runtime_wrapper is not None:
        return Strategy(
            kind="runtime",
            reason=f"{record['layout_label']} with encrypted child payload",
            wrapper_binary=runtime_wrapper,
            output_executable_name=runtime_output_name(runtime_wrapper),
        )

    if direct_executable is not None and (
        primary is None or str(primary["role"]) == "support_exe" or record["layout_label"] == "dll_only_with_application_dat"
    ):
        return Strategy(
            kind="direct",
            reason=f"{record['layout_label']} with a non-wrapper top-level game executable",
            direct_executable=direct_executable,
            output_executable_name=direct_executable.name,
        )

    return Strategy(kind="unsupported", reason=f"no safe unwrap strategy for {record['layout_label']}")


def effective_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    roots = [Path(record["root"]) for record in records]
    root_set = set(roots)
    filtered: list[dict[str, Any]] = []

    for record in records:
        root = Path(record["root"])
        if record["primary_wrapper_binary"] is None:
            if any(other != root and other.is_relative_to(root) for other in root_set):
                continue
        filtered.append(record)
    return filtered


def ensure_runtime_helper() -> Path:
    source = helper_source_path()
    binary = helper_binary_path()
    binary.parent.mkdir(parents=True, exist_ok=True)

    if binary.exists() and binary.stat().st_mtime >= source.stat().st_mtime:
        return binary

    subprocess.run(
        [
            "i686-w64-mingw32-gcc",
            "-O2",
            "-Wall",
            "-Wextra",
            "-std=c11",
            str(source),
            "-limagehlp",
            "-o",
            str(binary),
        ],
        check=True,
    )
    return binary


def wine_path(path: Path) -> str:
    return subprocess.run(
        ["winepath", "-w", str(path)],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def hardlink_or_copy(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        if dest.exists():
            dest.unlink()
        os.link(source, dest)
    except OSError:
        shutil.copy2(source, dest)


def should_skip_path(path: Path, relative_path: Path, strategy: Strategy, wrapper_paths: set[Path]) -> bool:
    if relative_path.parts and relative_path.parts[0] == "ReflexiveArcade":
        return True
    if path in wrapper_paths:
        return True
    if path.name in TOP_LEVEL_WRAPPER_JUNK:
        return True
    if strategy.kind == "runtime":
        if path.name == "RAW_001.exe":
            return True
        if path.suffix.lower() == ".rwg":
            return True
    return False


def copy_support_tree(source_root: Path, dest_root: Path, strategy: Strategy, wrapper_paths: set[Path]) -> None:
    for path in sorted(source_root.rglob("*")):
        relative_path = path.relative_to(source_root)
        if should_skip_path(path, relative_path, strategy, wrapper_paths):
            continue
        destination = dest_root / relative_path
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            hardlink_or_copy(path, destination)


def run_runtime_helper(wrapper_binary: Path, output_executable: Path) -> str:
    helper = ensure_runtime_helper()
    env = os.environ.copy()
    env.setdefault("WINEDEBUG", "-all")
    env.setdefault("MVK_CONFIG_LOG_LEVEL", "0")
    result = subprocess.run(
        [
            "wine",
            str(helper),
            wine_path(wrapper_binary),
            wine_path(output_executable),
        ],
        env=env,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "runtime helper failed")
    if not output_executable.is_file():
        raise RuntimeError("runtime helper exited successfully but did not create the output executable")
    return result.stdout.strip()


def materialize_record(record: dict[str, Any], extracted_root: Path, output_root: Path, force: bool) -> dict[str, Any]:
    relative_root = Path(record["root"])
    wrapper_root = extracted_root / relative_root
    destination_root = output_root / relative_root
    strategy = choose_strategy(record, wrapper_root)
    wrapper_paths = {
        repo_root() / Path(candidate["path"])
        for candidate in record["binary_candidates"]
        if candidate["looks_like_wrapper_binary"]
    }

    summary: dict[str, Any] = {
        "root": str(relative_root),
        "strategy": strategy.kind,
        "reason": strategy.reason,
        "output_root": str(destination_root),
    }

    if strategy.kind == "unsupported":
        summary["status"] = "unsupported"
        return summary

    if destination_root.exists():
        if not force:
            raise RuntimeError(f"{destination_root} already exists; pass --force to replace it")
        shutil.rmtree(destination_root)

    destination_root.mkdir(parents=True, exist_ok=True)
    copy_support_tree(wrapper_root, destination_root, strategy, wrapper_paths)

    if strategy.kind == "runtime":
        assert strategy.wrapper_binary is not None
        assert strategy.output_executable_name is not None
        output_executable = destination_root / strategy.output_executable_name
        helper_stdout = run_runtime_helper(strategy.wrapper_binary, output_executable)
        summary["status"] = "ok"
        summary["wrapper_binary"] = str(strategy.wrapper_binary)
        summary["output_executable"] = str(output_executable)
        summary["helper_stdout"] = helper_stdout
        return summary

    assert strategy.direct_executable is not None
    summary["status"] = "ok"
    summary["output_executable"] = str(destination_root / strategy.direct_executable.name)
    summary["direct_executable"] = str(strategy.direct_executable)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize wrapper-free Reflexive game trees under artifacts/unwrapped."
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help="Optional relative or absolute extracted game roots. Defaults to all supported roots.",
    )
    parser.add_argument(
        "--extracted-root",
        type=Path,
        default=default_extracted_root(),
        help="Root containing extracted Reflexive Arcade directories.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=default_output_root(),
        help="Destination root for wrapper-free game trees.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing outputs.",
    )
    parser.add_argument(
        "--list-unsupported",
        action="store_true",
        help="Print unsupported roots after processing.",
    )
    return parser.parse_args()


def normalize_target(target: str, extracted_root: Path) -> str:
    path = Path(target)
    if path.is_absolute():
        return str(path.resolve().relative_to(extracted_root))
    return str(path)


def main() -> int:
    args = parse_args()
    extracted_root = args.extracted_root.resolve()
    output_root = args.output_root.resolve()
    inventory = build_scan(extracted_root)
    records = effective_records(inventory["roots"])

    selected = {normalize_target(target, extracted_root) for target in args.targets} if args.targets else None
    if selected is not None:
        records = [record for record in records if record["root"] in selected]

    successes = 0
    unsupported: list[dict[str, Any]] = []

    for record in records:
        summary = materialize_record(record, extracted_root, output_root, args.force)
        if summary["status"] == "unsupported":
            unsupported.append(summary)
            print(f"UNSUPPORTED {summary['root']}: {summary['reason']}")
            continue

        successes += 1
        print(f"OK {summary['root']} -> {display_path(Path(summary['output_root']))}")
        if "output_executable" in summary:
            print(f"  executable: {display_path(Path(summary['output_executable']))}")

    print(f"Supported outputs materialized: {successes}")
    print(f"Unsupported roots: {len(unsupported)}")

    if args.list_unsupported and unsupported:
        for summary in unsupported:
            print(f"- {summary['root']}: {summary['reason']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
