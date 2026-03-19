from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import unwrap


@dataclass(frozen=True)
class UnwrapTreeResult:
    ok_roots: tuple[str, ...]
    unsupported_roots: tuple[str, ...]

def load_unwrapper_module() -> Any:
    return unwrap


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
