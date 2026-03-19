from __future__ import annotations

import argparse
import json
import random
import re
import struct
from collections import Counter
from dataclasses import asdict, dataclass
from functools import lru_cache
from math import gcd
from pathlib import Path

import pefile

from .reflexive_listkg import DEFAULT_LIST_PATH, decode_payload_integer, load_entries
from .source_layout import infer_source_id_from_extracted_root, repo_root as source_repo_root
from .source_layout import source_label

try:
    from sympy import factorint as sympy_factorint
except ImportError:
    sympy_factorint = None


KEY_DATA_RE = re.compile(rb"Decryption Key Data=([A-Z0-9])(/([A-Z0-9]+))")
APP_ID_HEX_RE = re.compile(rb"[0-9A-Fa-f]{8}")
FIXED_EXPONENT_BLOB = "CAAB"
MILLER_RABIN_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


@dataclass(frozen=True)
class EmbeddedKeyMaterial:
    revision: str
    encoded_modulus: str
    encoded_public_exponent: str
    modulus_hex: str
    public_exponent: int


@dataclass(frozen=True)
class FactorizationResult:
    prime_factors_hex: list[str]
    private_exponent_hex: str


@dataclass(frozen=True)
class KeyInventoryRecord:
    game_name_guess: str
    dll_path: str
    app_id: int | None
    app_id_hex: str | None
    key_revision: str | None
    encoded_modulus: str | None
    encoded_public_exponent: str | None
    modulus_hex: str | None
    public_exponent: int | None
    public_exponent_hex: str | None
    private_exponent_hex: str | None
    prime_factors_hex: list[str]
    list_name: str | None
    list_modulus_hex: str | None
    list_private_exponent_hex: str | None
    list_modulus_match: bool | None
    list_private_exponent_match: bool | None
    errors: list[str]


def repo_root() -> Path:
    return source_repo_root()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def default_markdown_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "key_inventory.md"


def default_json_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "key_inventory.json"


def discover_support_dlls(extracted_root: Path) -> list[Path]:
    return sorted(path.resolve() for path in extracted_root.rglob("ReflexiveArcade/ReflexiveArcade.dll"))


def format_hex(value: int) -> str:
    hex_text = format(value, "X")
    if len(hex_text) % 2:
        hex_text = "0" + hex_text
    return hex_text


def extract_embedded_key_material(data: bytes) -> tuple[EmbeddedKeyMaterial | None, list[str]]:
    errors: list[str] = []
    matches = {
        (match.group(1).decode("ascii"), match.group(3).decode("ascii"))
        for match in KEY_DATA_RE.finditer(data)
    }
    if not matches:
        return None, ["missing Decryption Key Data string"]
    if len(matches) > 1:
        errors.append("multiple distinct Decryption Key Data strings found")
    revision, encoded_modulus = sorted(matches)[0]

    if b"/CAAB" not in data:
        return None, errors + ["missing /CAAB exponent blob"]

    modulus = decode_payload_integer(encoded_modulus)
    public_exponent = decode_payload_integer(FIXED_EXPONENT_BLOB)
    return (
        EmbeddedKeyMaterial(
            revision=revision,
            encoded_modulus=encoded_modulus,
            encoded_public_exponent=FIXED_EXPONENT_BLOB,
            modulus_hex=format_hex(modulus),
            public_exponent=public_exponent,
        ),
        errors,
    )


def parse_export_rva(pe: pefile.PE, export_name: str) -> int | None:
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
    directory = getattr(pe, "DIRECTORY_ENTRY_EXPORT", None)
    if directory is None:
        return None
    target = export_name.encode("ascii")
    for symbol in directory.symbols:
        if symbol.name == target:
            return symbol.address
    return None


def follow_unconditional_jumps(pe: pefile.PE, data: bytes, rva: int, max_hops: int = 8) -> int:
    current = rva
    for _ in range(max_hops):
        offset = pe.get_offset_from_rva(current)
        opcode = data[offset]
        if opcode == 0xE9 and offset + 5 <= len(data):
            displacement = struct.unpack_from("<i", data, offset + 1)[0]
            current = current + 5 + displacement
            continue
        if opcode == 0xEB and offset + 2 <= len(data):
            displacement = struct.unpack_from("<b", data, offset + 1)[0]
            current = current + 2 + displacement
            continue
        break
    return current


def va_to_offset(pe: pefile.PE, va: int) -> int:
    rva = va - pe.OPTIONAL_HEADER.ImageBase
    if rva < 0:
        raise pefile.PEFormatError(f"virtual address before image base: 0x{va:X}")
    return pe.get_offset_from_rva(rva)


def read_c_string(data: bytes, offset: int) -> bytes:
    end = data.find(b"\x00", offset)
    if end == -1:
        end = len(data)
    return data[offset:end]


def extract_app_id(path: Path) -> tuple[int | None, list[str]]:
    errors: list[str] = []
    try:
        pe = pefile.PE(str(path), fast_load=True)
    except pefile.PEFormatError as exc:
        return None, [f"invalid PE: {exc}"]

    data = path.read_bytes()
    rva = parse_export_rva(pe, "unittest_GetBrandedApplicationID")
    if rva is None:
        return None, ["missing unittest_GetBrandedApplicationID export"]

    target_rva = follow_unconditional_jumps(pe, data, rva)
    offset = pe.get_offset_from_rva(target_rva)
    window = data[offset : offset + 0x30]
    for index in range(max(0, len(window) - 5)):
        if window[index] != 0x68:
            continue
        string_va = struct.unpack_from("<I", window, index + 1)[0]
        try:
            string_offset = va_to_offset(pe, string_va)
        except pefile.PEFormatError:
            continue
        candidate = read_c_string(data, string_offset)
        if APP_ID_HEX_RE.fullmatch(candidate):
            return int(candidate.decode("ascii"), 16), errors

    return None, ["could not locate pushed branded application id string"]


def is_probable_prime(value: int) -> bool:
    if value < 2:
        return False
    for base in MILLER_RABIN_BASES:
        if value % base == 0:
            return value == base

    d = value - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for base in MILLER_RABIN_BASES:
        if base >= value:
            continue
        witness = pow(base, d, value)
        if witness in {1, value - 1}:
            continue
        for _ in range(s - 1):
            witness = pow(witness, 2, value)
            if witness == value - 1:
                break
        else:
            return False
    return True


def pollard_brent(value: int) -> int:
    if value % 2 == 0:
        return 2
    if value % 3 == 0:
        return 3

    for attempt in range(1, 33):
        rng = random.Random((value << 8) ^ attempt)
        y = rng.randrange(1, value)
        c = rng.randrange(1, value)
        m = 128
        g = 1
        r = 1
        x = 0
        ys = 0

        while g == 1:
            x = y
            for _ in range(r):
                y = (pow(y, 2, value) + c) % value
            k = 0
            while k < r and g == 1:
                ys = y
                q = 1
                for _ in range(min(m, r - k)):
                    y = (pow(y, 2, value) + c) % value
                    q = (q * abs(x - y)) % value
                g = gcd(q, value)
                k += m
            r *= 2

        if g == value:
            g = 1
            while g == 1:
                ys = (pow(ys, 2, value) + c) % value
                g = gcd(abs(x - ys), value)

        if g != value:
            return g

    raise ValueError(f"pollard rho failed for 0x{value:X}")


def factor_into_primes(value: int, output: list[int]) -> None:
    if value == 1:
        return
    if is_probable_prime(value):
        output.append(value)
        return
    divisor = pollard_brent(value)
    factor_into_primes(divisor, output)
    factor_into_primes(value // divisor, output)


@lru_cache(maxsize=None)
def derive_private_exponent(modulus: int, public_exponent: int) -> FactorizationResult:
    if sympy_factorint is not None:
        counts = Counter({int(prime): exponent for prime, exponent in sympy_factorint(modulus).items()})
    else:
        factors: list[int] = []
        factor_into_primes(modulus, factors)
        counts = Counter(factors)
    totient = 1
    for prime, exponent in counts.items():
        totient *= (prime - 1) * pow(prime, exponent - 1)
    private_exponent = pow(public_exponent, -1, totient)
    flattened_factors = sorted(prime for prime, exponent in counts.items() for _ in range(exponent))
    return FactorizationResult(
        prime_factors_hex=[format_hex(factor) for factor in flattened_factors],
        private_exponent_hex=format_hex(private_exponent),
    )


def build_record(dll_path: Path, entries_by_id: dict[int, object], derive_private: bool) -> KeyInventoryRecord:
    errors: list[str] = []
    app_id, app_id_errors = extract_app_id(dll_path)
    errors.extend(app_id_errors)

    key_material, key_errors = extract_embedded_key_material(dll_path.read_bytes())
    errors.extend(key_errors)

    private_exponent_hex: str | None = None
    prime_factors_hex: list[str] = []
    if key_material is not None and derive_private:
        try:
            factorization = derive_private_exponent(int(key_material.modulus_hex, 16), key_material.public_exponent)
        except ValueError as exc:
            errors.append(f"failed to derive private exponent: {exc}")
        else:
            private_exponent_hex = factorization.private_exponent_hex
            prime_factors_hex = factorization.prime_factors_hex

    list_entry = entries_by_id.get(app_id) if app_id is not None else None
    list_modulus_hex = getattr(list_entry, "modulus_hex", None)
    list_private_exponent_hex = getattr(list_entry, "exponent_hex", None)

    modulus_hex = key_material.modulus_hex if key_material is not None else None
    list_modulus_match = None
    list_private_exponent_match = None
    if list_entry is not None and modulus_hex is not None:
        list_modulus_match = modulus_hex.upper() == list_modulus_hex.upper()
    if list_entry is not None and private_exponent_hex is not None:
        list_private_exponent_match = private_exponent_hex.upper() == list_private_exponent_hex.upper()

    return KeyInventoryRecord(
        game_name_guess=dll_path.parent.parent.name,
        dll_path=display_path(dll_path),
        app_id=app_id,
        app_id_hex=f"{app_id:08X}" if app_id is not None else None,
        key_revision=key_material.revision if key_material is not None else None,
        encoded_modulus=key_material.encoded_modulus if key_material is not None else None,
        encoded_public_exponent=key_material.encoded_public_exponent if key_material is not None else None,
        modulus_hex=modulus_hex,
        public_exponent=key_material.public_exponent if key_material is not None else None,
        public_exponent_hex=format_hex(key_material.public_exponent) if key_material is not None else None,
        private_exponent_hex=private_exponent_hex,
        prime_factors_hex=prime_factors_hex,
        list_name=getattr(list_entry, "name", None),
        list_modulus_hex=list_modulus_hex,
        list_private_exponent_hex=list_private_exponent_hex,
        list_modulus_match=list_modulus_match,
        list_private_exponent_match=list_private_exponent_match,
        errors=errors,
    )


def summarize_records(records: list[KeyInventoryRecord]) -> dict[str, object]:
    revision_counts = Counter(record.key_revision for record in records if record.key_revision is not None)
    public_matches = [record for record in records if record.list_modulus_match is True]
    exact_matches = [
        record
        for record in records
        if record.list_modulus_match is True and record.list_private_exponent_match is True
    ]
    failures = [record for record in records if record.errors]
    list_mismatches = [
        record
        for record in records
        if (record.list_modulus_match is False) or (record.list_private_exponent_match is False)
    ]
    missing_list_entries = [record for record in records if record.app_id is not None and record.list_name is None]
    return {
        "dll_count": len(records),
        "app_id_count": sum(record.app_id is not None for record in records),
        "public_key_count": sum(record.modulus_hex is not None for record in records),
        "private_key_count": sum(record.private_exponent_hex is not None for record in records),
        "public_list_matches": len(public_matches),
        "exact_list_matches": len(exact_matches),
        "failure_count": len(failures),
        "list_mismatch_count": len(list_mismatches),
        "missing_list_entry_count": len(missing_list_entries),
        "revision_counts": dict(sorted(revision_counts.items())),
    }


def render_markdown(
    source_id: str | None,
    extracted_root: Path,
    summary: dict[str, object],
    records: list[KeyInventoryRecord],
) -> str:
    title = "Reflexive Key Inventory"
    if source_id is not None:
        title = f"{title} ({source_label(source_id)})"

    lines = [
        f"# {title}",
        "",
        f"- Extracted root: `{display_path(extracted_root)}`",
        f"- Support DLLs scanned: {summary['dll_count']}",
        f"- App ids recovered: {summary['app_id_count']}",
        f"- Public keys recovered: {summary['public_key_count']}",
        f"- Private exponents derived: {summary['private_key_count']}",
        f"- Public modulus matches in `list.txt`: {summary['public_list_matches']}",
        f"- Exact `list.txt` matches: {summary['exact_list_matches']}",
        f"- Records with extraction errors: {summary['failure_count']}",
        f"- Records missing from `list.txt`: {summary['missing_list_entry_count']}",
        f"- Records mismatching `list.txt`: {summary['list_mismatch_count']}",
        "",
        "## Key Revisions",
        "",
        "| Revision | Count |",
        "| --- | ---: |",
    ]

    revision_counts = summary["revision_counts"]
    if revision_counts:
        for revision, count in revision_counts.items():
            lines.append(f"| {revision} | {count} |")
    else:
        lines.append("| none | 0 |")

    exact_matches = [
        record
        for record in records
        if record.list_modulus_match is True and record.list_private_exponent_match is True
    ]
    if exact_matches:
        lines.extend(
            [
                "",
                "## Exact Matches",
                "",
                "| Game | App ID | Revision | Modulus | D |",
                "| --- | ---: | --- | --- | --- |",
            ]
        )
        for record in exact_matches[:20]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        record.game_name_guess,
                        str(record.app_id),
                        record.key_revision or "",
                        record.modulus_hex or "",
                        record.private_exponent_hex or "",
                    ]
                )
                + " |"
            )

    failures = [record for record in records if record.errors]
    if failures:
        lines.extend(
            [
                "",
                "## Extraction Failures",
                "",
                "| DLL | Errors |",
                "| --- | --- |",
            ]
        )
        for record in failures[:40]:
            lines.append(f"| `{record.dll_path}` | {'; '.join(record.errors)} |")

    mismatches = [
        record
        for record in records
        if (record.list_modulus_match is False) or (record.list_private_exponent_match is False)
    ]
    if mismatches:
        lines.extend(
            [
                "",
                "## list.txt Mismatches",
                "",
                "| Game | App ID | Modulus Match | D Match | DLL |",
                "| --- | ---: | --- | --- | --- |",
            ]
        )
        for record in mismatches[:40]:
            lines.append(
                f"| {record.game_name_guess} | {record.app_id or ''} | "
                f"{record.list_modulus_match} | {record.list_private_exponent_match} | `{record.dll_path}` |"
            )

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract embedded Reflexive RSA key material from branded DLLs.")
    parser.add_argument("extracted_root", type=Path, help="root of an extracted Reflexive corpus")
    parser.add_argument("--list-path", type=Path, default=DEFAULT_LIST_PATH, help="path to list.txt for comparison")
    parser.add_argument("--json-out", type=Path, help="write JSON inventory output")
    parser.add_argument("--markdown-out", type=Path, help="write Markdown report output")
    parser.add_argument("--limit", type=int, help="scan at most this many DLLs")
    parser.add_argument("--skip-factor", action="store_true", help="skip private-exponent derivation and only inventory embedded public keys")
    parser.add_argument("--stdout-json", action="store_true", help="emit the JSON report to stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    extracted_root = args.extracted_root.resolve()
    source_id = infer_source_id_from_extracted_root(extracted_root)
    entries = load_entries(args.list_path.resolve())

    dll_paths = discover_support_dlls(extracted_root)
    if args.limit is not None:
        dll_paths = dll_paths[: args.limit]

    records = [build_record(dll_path, entries, derive_private=not args.skip_factor) for dll_path in dll_paths]
    records.sort(key=lambda record: (record.app_id is None, record.app_id or -1, record.game_name_guess.casefold()))
    summary = summarize_records(records)

    report = {
        "source_id": source_id,
        "source_label": source_label(source_id) if source_id is not None else None,
        "extracted_root": display_path(extracted_root),
        "list_path": display_path(args.list_path.resolve()),
        "summary": summary,
        "records": [asdict(record) for record in records],
    }

    json_out = args.json_out
    markdown_out = args.markdown_out
    if source_id is not None:
        if json_out is None:
            json_out = default_json_path(source_id)
        if markdown_out is None:
            markdown_out = default_markdown_path(source_id)

    if json_out is not None:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if markdown_out is not None:
        markdown_out.parent.mkdir(parents=True, exist_ok=True)
        markdown_out.write_text(render_markdown(source_id, extracted_root, summary, records), encoding="utf-8")

    if args.stdout_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"dlls={summary['dll_count']}")
        print(f"app_ids={summary['app_id_count']}")
        print(f"public_keys={summary['public_key_count']}")
        print(f"private_keys={summary['private_key_count']}")
        print(f"public_list_matches={summary['public_list_matches']}")
        print(f"exact_list_matches={summary['exact_list_matches']}")
        print(f"errors={summary['failure_count']}")
        print(f"missing_list_entries={summary['missing_list_entry_count']}")
        print(f"list_mismatches={summary['list_mismatch_count']}")
        if json_out is not None:
            print(f"json_out={display_path(json_out.resolve())}")
        if markdown_out is not None:
            print(f"markdown_out={display_path(markdown_out.resolve())}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
