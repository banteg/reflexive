from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class UnwrapTreeResult:
    ok_roots: tuple[str, ...]
    unsupported_roots: tuple[str, ...]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_unwrapper_module() -> Any:
    module_path = repo_root() / "scripts" / "unwrap_reflexive_wrapper.py"
    spec = importlib.util.spec_from_file_location("reflexive_unwrapper", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def unwrap_extracted_tree(extracted_tree: Path, output_root: Path, *, force: bool) -> UnwrapTreeResult:
    extracted_tree = extracted_tree.resolve()
    output_root = output_root.resolve()

    module = load_unwrapper_module()
    inventory = module.build_scan(extracted_tree)
    records = module.effective_records(inventory["roots"])
    if not records:
        raise RuntimeError(f"no effective wrapper roots found under {extracted_tree}")

    ok_roots: list[str] = []
    unsupported_roots: list[str] = []
    for record in records:
        summary = module.materialize_record(record, extracted_tree, output_root, force=force)
        if summary["status"] == "unsupported":
            unsupported_roots.append(str(record["root"]))
            continue
        ok_roots.append(str(record["root"]))

    return UnwrapTreeResult(ok_roots=tuple(ok_roots), unsupported_roots=tuple(unsupported_roots))
