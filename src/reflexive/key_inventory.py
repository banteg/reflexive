from __future__ import annotations

import argparse
import json
import random
import re
import struct
import subprocess
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from functools import lru_cache
from math import gcd
from pathlib import Path

import pefile

from .keygen import decode_payload_integer, load_entries
from .source_layout import display_path, repo_root, infer_source_id_from_extracted_root, source_label

HISTORICAL_LIST_PATH = repo_root() / "artifacts" / "rutracker" / "_Crack" / "listkg_1421_by_russiankid" / "list.txt"

try:
    from sympy import factorint as sympy_factorint
except ImportError:
    sympy_factorint = None


KEY_DATA_RE = re.compile(rb"Decryption Key Data=([A-Z0-9])(/([A-Z0-9]+))")
APP_ID_HEX_RE = re.compile(rb"[0-9A-Fa-f]{8}")
MSIEVE_FACTOR_RE = re.compile(r"^(?:p|prp|c)\d+:\s+(\d+)$", re.IGNORECASE)
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
    backend: str
    prime_factors_hex: list[str]
    private_exponent_hex: str
    elapsed_seconds: float | None = None


@dataclass(frozen=True)
class HistoricalListEntry:
    name: str
    game_id: int
    modulus_hex: str
    private_exponent_hex: str
    source_path: str


@dataclass(frozen=True)
class ScannedKeyRecord:
    game_name_guess: str
    dll_path: str
    app_id: int | None
    key_material: EmbeddedKeyMaterial | None
    historical_entry: HistoricalListEntry | None
    list_name: str | None
    list_modulus_hex: str | None
    list_private_exponent_hex: str | None
    errors: list[str]


@dataclass(frozen=True)
class FactorCacheEntry:
    modulus_hex: str
    public_exponent: int
    backend: str
    prime_factors_hex: list[str]
    private_exponent_hex: str
    elapsed_seconds: float | None = None


@dataclass(frozen=True)
class FactorWorkItem:
    modulus_hex: str
    public_exponent: int
    game_name_guess: str
    dll_path: str
    app_id: int | None
    reason: str


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
    private_exponent_source: str | None
    prime_factors_hex: list[str]
    factored_private_exponent_hex: str | None
    factored_private_exponent_source: str | None
    factored_prime_factors_hex: list[str]
    factored_elapsed_seconds: float | None
    list_name: str | None
    list_modulus_hex: str | None
    list_private_exponent_hex: str | None
    list_modulus_match: bool | None
    list_private_exponent_match: bool | None
    factored_private_exponent_match: bool | None
    errors: list[str]


def default_markdown_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "key_inventory.md"


def default_json_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "key_inventory.json"


def default_factor_cache_path(source_id: str) -> Path:
    return repo_root() / "docs" / "generated" / source_id / "key_inventory_factors.jsonl"


def default_list_history_root() -> Path:
    return repo_root() / "artifacts" / "rutracker" / "_Crack"


def default_msieve_path() -> Path:
    return repo_root() / "artifacts" / "tools" / "msieve" / "msieve"


def discover_support_dlls(extracted_root: Path) -> list[Path]:
    return sorted(path.resolve() for path in extracted_root.rglob("ReflexiveArcade/ReflexiveArcade.dll"))


def format_hex(value: int) -> str:
    hex_text = format(value, "X")
    if len(hex_text) % 2:
        hex_text = "0" + hex_text
    return hex_text


def hex_values_equal(left: str, right: str) -> bool:
    return int(left, 16) == int(right, 16)


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
    data = path.read_bytes()
    try:
        pe = pefile.PE(data=data, fast_load=True)
    except pefile.PEFormatError as exc:
        return None, [f"invalid PE: {exc}"]
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


def load_historical_private_entries(root: Path) -> dict[tuple[int, str], HistoricalListEntry]:
    entries: dict[tuple[int, str], HistoricalListEntry] = {}
    for path in sorted(root.glob("listkg_*_by_russiankid/list.txt")):
        for raw_line in path.read_text(encoding="latin-1").splitlines():
            line = raw_line.strip().strip("|")
            if not line:
                continue
            parts = line.split("|")
            if len(parts) < 4:
                continue
            name, game_id_text, modulus_hex, private_exponent_hex = parts[:4]
            game_id = int(game_id_text)
            entries[(game_id, modulus_hex.upper())] = HistoricalListEntry(
                name=name,
                game_id=game_id,
                modulus_hex=modulus_hex.upper(),
                private_exponent_hex=private_exponent_hex.upper(),
                source_path=display_path(path.resolve()),
            )
    return entries


@lru_cache(maxsize=None)
def derive_private_exponent(modulus: int, public_exponent: int) -> FactorizationResult:
    return derive_private_exponent_internal(modulus, public_exponent)


def derive_private_exponent_from_counts(
    counts: Counter[int],
    public_exponent: int,
    *,
    backend: str,
    elapsed_seconds: float | None = None,
) -> FactorizationResult:
    if not counts:
        raise ValueError("no factors supplied")
    totient = 1
    for prime, exponent in counts.items():
        totient *= (prime - 1) * pow(prime, exponent - 1)
    private_exponent = pow(public_exponent, -1, totient)
    flattened_factors = sorted(prime for prime, exponent in counts.items() for _ in range(exponent))
    return FactorizationResult(
        backend=backend,
        prime_factors_hex=[format_hex(factor) for factor in flattened_factors],
        private_exponent_hex=format_hex(private_exponent),
        elapsed_seconds=elapsed_seconds,
    )


@lru_cache(maxsize=None)
def derive_private_exponent_internal(modulus: int, public_exponent: int) -> FactorizationResult:
    if sympy_factorint is not None:
        counts = Counter({int(prime): exponent for prime, exponent in sympy_factorint(modulus).items()})
    else:
        factors: list[int] = []
        factor_into_primes(modulus, factors)
        counts = Counter(factors)
    return derive_private_exponent_from_counts(counts, public_exponent, backend="internal")


def parse_msieve_factor_output(output: str, modulus: int) -> list[int]:
    raw_factors: list[int] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        match = MSIEVE_FACTOR_RE.match(line)
        if match is None:
            continue
        raw_factors.append(int(match.group(1)))
    if not raw_factors:
        raise ValueError("msieve returned no factor lines")

    flattened_factors: list[int] = []
    for factor in raw_factors:
        factor_into_primes(factor, flattened_factors)
    flattened_factors.sort()

    product = 1
    for factor in flattened_factors:
        product *= factor
    if product != modulus:
        raise ValueError("msieve factors did not multiply back to the modulus")
    return flattened_factors


def derive_private_exponent_msieve(modulus: int, public_exponent: int, msieve_bin: Path) -> FactorizationResult:
    if not msieve_bin.is_file():
        raise ValueError(f"msieve binary not found: {display_path(msieve_bin)}")

    start = time.perf_counter()
    proc = subprocess.run(
        [str(msieve_bin), "-q", f"0x{format(modulus, 'X')}"],
        check=False,
        capture_output=True,
        text=True,
    )
    elapsed_seconds = time.perf_counter() - start
    if proc.returncode != 0:
        stderr = proc.stderr.strip()
        if stderr:
            raise ValueError(f"msieve exited with {proc.returncode}: {stderr}")
        raise ValueError(f"msieve exited with {proc.returncode}")

    prime_factors = parse_msieve_factor_output(proc.stdout, modulus)
    return derive_private_exponent_from_counts(
        Counter(prime_factors),
        public_exponent,
        backend="msieve",
        elapsed_seconds=elapsed_seconds,
    )


def resolve_factor_backend(name: str, msieve_bin: Path) -> str:
    if name == "auto":
        return "msieve" if msieve_bin.is_file() else "internal"
    if name == "msieve" and not msieve_bin.is_file():
        raise ValueError(f"msieve binary not found: {display_path(msieve_bin)}")
    return name


def load_factor_cache(path: Path | None) -> dict[tuple[str, int], FactorCacheEntry]:
    if path is None or not path.is_file():
        return {}

    entries: dict[tuple[str, int], FactorCacheEntry] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        modulus_hex = payload["modulus_hex"].upper()
        public_exponent = int(payload["public_exponent"])
        entries[(modulus_hex, public_exponent)] = FactorCacheEntry(
            modulus_hex=modulus_hex,
            public_exponent=public_exponent,
            backend=payload["backend"],
            prime_factors_hex=[factor.upper() for factor in payload["prime_factors_hex"]],
            private_exponent_hex=payload["private_exponent_hex"].upper(),
            elapsed_seconds=payload.get("elapsed_seconds"),
        )
    return entries


def append_factor_cache_entry(handle, entry: FactorCacheEntry) -> None:
    handle.write(json.dumps(asdict(entry), sort_keys=True) + "\n")
    handle.flush()


def factor_modulus(
    modulus_hex: str,
    public_exponent: int,
    *,
    factor_backend: str,
    msieve_bin: Path,
) -> FactorCacheEntry:
    modulus = int(modulus_hex, 16)
    resolved_backend = resolve_factor_backend(factor_backend, msieve_bin)
    if resolved_backend == "msieve":
        result = derive_private_exponent_msieve(modulus, public_exponent, msieve_bin)
    elif resolved_backend == "internal":
        result = derive_private_exponent_internal(modulus, public_exponent)
    else:
        raise ValueError(f"unsupported factor backend: {resolved_backend}")

    return FactorCacheEntry(
        modulus_hex=modulus_hex.upper(),
        public_exponent=public_exponent,
        backend=result.backend,
        prime_factors_hex=result.prime_factors_hex,
        private_exponent_hex=result.private_exponent_hex,
        elapsed_seconds=result.elapsed_seconds,
    )


def scan_record(
    dll_path: Path,
    entries_by_id: dict[int, object],
    historical_entries: dict[tuple[int, str], HistoricalListEntry],
) -> ScannedKeyRecord:
    errors: list[str] = []
    app_id, app_id_errors = extract_app_id(dll_path)
    errors.extend(app_id_errors)

    key_material, key_errors = extract_embedded_key_material(dll_path.read_bytes())
    errors.extend(key_errors)

    historical_entry = None
    if app_id is not None and key_material is not None:
        historical_entry = historical_entries.get((app_id, key_material.modulus_hex.upper()))

    list_entry = entries_by_id.get(app_id) if app_id is not None else None
    return ScannedKeyRecord(
        game_name_guess=dll_path.parent.parent.name,
        dll_path=display_path(dll_path),
        app_id=app_id,
        key_material=key_material,
        historical_entry=historical_entry,
        list_name=getattr(list_entry, "name", None),
        list_modulus_hex=getattr(list_entry, "modulus_hex", None),
        list_private_exponent_hex=getattr(list_entry, "exponent_hex", None),
        errors=errors,
    )


def collect_factor_work_items(
    scanned_records: list[ScannedKeyRecord],
    *,
    derive_private: bool,
    factor_remaining: bool,
    verify_known: bool,
) -> list[FactorWorkItem]:
    items: dict[tuple[str, int], FactorWorkItem] = {}
    for record in scanned_records:
        if record.key_material is None:
            continue
        should_factor_unknown = derive_private and factor_remaining and record.historical_entry is None
        should_verify_known = verify_known and record.historical_entry is not None
        if not should_factor_unknown and not should_verify_known:
            continue

        reason = "verify_known" if should_verify_known else "derive_unknown"
        key = (record.key_material.modulus_hex.upper(), record.key_material.public_exponent)
        items.setdefault(
            key,
            FactorWorkItem(
                modulus_hex=record.key_material.modulus_hex.upper(),
                public_exponent=record.key_material.public_exponent,
                game_name_guess=record.game_name_guess,
                dll_path=record.dll_path,
                app_id=record.app_id,
                reason=reason,
            ),
        )
    return sorted(items.values(), key=lambda item: (item.app_id is None, item.app_id or -1, item.game_name_guess.casefold()))


def factor_work_items(
    work_items: list[FactorWorkItem],
    *,
    existing_cache: dict[tuple[str, int], FactorCacheEntry],
    factor_backend: str,
    msieve_bin: Path,
    factor_cache_path: Path | None,
) -> tuple[dict[tuple[str, int], FactorCacheEntry], dict[tuple[str, int], str]]:
    factor_results = dict(existing_cache)
    factor_errors: dict[tuple[str, int], str] = {}
    pending_items = [
        item for item in work_items if (item.modulus_hex.upper(), item.public_exponent) not in factor_results
    ]
    if not pending_items:
        return factor_results, factor_errors

    cache_handle = None
    if factor_cache_path is not None:
        factor_cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_handle = factor_cache_path.open("a", encoding="utf-8")

    try:
        print(
            f"factoring_pending={len(pending_items)} backend={resolve_factor_backend(factor_backend, msieve_bin)}",
            file=sys.stderr,
        )
        for index, item in enumerate(pending_items, 1):
            key = (item.modulus_hex.upper(), item.public_exponent)
            try:
                entry = factor_modulus(
                    item.modulus_hex,
                    item.public_exponent,
                    factor_backend=factor_backend,
                    msieve_bin=msieve_bin,
                )
            except ValueError as exc:
                factor_errors[key] = str(exc)
            else:
                factor_results[key] = entry
                if cache_handle is not None:
                    append_factor_cache_entry(cache_handle, entry)

            if index == len(pending_items) or index % 50 == 0:
                print(f"factoring_progress={index}/{len(pending_items)}", file=sys.stderr)
    finally:
        if cache_handle is not None:
            cache_handle.close()

    return factor_results, factor_errors


def build_record(
    scanned_record: ScannedKeyRecord,
    *,
    factor_results: dict[tuple[str, int], FactorCacheEntry],
    factor_errors: dict[tuple[str, int], str],
    derive_private: bool,
    factor_remaining: bool,
    verify_known: bool,
) -> KeyInventoryRecord:
    errors = list(scanned_record.errors)
    key_material = scanned_record.key_material
    private_exponent_hex: str | None = None
    private_exponent_source: str | None = None
    prime_factors_hex: list[str] = []
    factor_entry: FactorCacheEntry | None = None
    factored_private_exponent_match = None
    if key_material is not None:
        key = (key_material.modulus_hex.upper(), key_material.public_exponent)
        should_use_factored_private = derive_private and factor_remaining and scanned_record.historical_entry is None
        should_verify_factored_private = verify_known and scanned_record.historical_entry is not None
        if should_use_factored_private or should_verify_factored_private:
            factor_entry = factor_results.get(key)
        should_consult_factor_error = should_use_factored_private or should_verify_factored_private
        if should_consult_factor_error and key in factor_errors:
            errors.append(f"failed to derive private exponent: {factor_errors[key]}")
        if factor_entry is not None and scanned_record.historical_entry is not None:
            factored_private_exponent_match = hex_values_equal(
                factor_entry.private_exponent_hex,
                scanned_record.historical_entry.private_exponent_hex,
            )

    use_factored_override = factored_private_exponent_match is False
    if use_factored_override:
        errors.append("historical private exponent failed RSA verification; using factored replacement")

    if scanned_record.historical_entry is not None and not use_factored_override:
        private_exponent_hex = scanned_record.historical_entry.private_exponent_hex
        private_exponent_source = "historical_list"
    elif factor_entry is not None:
        private_exponent_hex = factor_entry.private_exponent_hex
        private_exponent_source = factor_entry.backend
        prime_factors_hex = factor_entry.prime_factors_hex

    list_modulus_hex = scanned_record.list_modulus_hex
    list_private_exponent_hex = scanned_record.list_private_exponent_hex
    modulus_hex = key_material.modulus_hex if key_material is not None else None
    list_modulus_match = None
    list_private_exponent_match = None
    if scanned_record.list_name is not None and modulus_hex is not None and list_modulus_hex is not None:
        list_modulus_match = hex_values_equal(modulus_hex, list_modulus_hex)
    if scanned_record.list_name is not None and private_exponent_hex is not None and list_private_exponent_hex is not None:
        list_private_exponent_match = hex_values_equal(private_exponent_hex, list_private_exponent_hex)

    return KeyInventoryRecord(
        game_name_guess=scanned_record.game_name_guess,
        dll_path=scanned_record.dll_path,
        app_id=scanned_record.app_id,
        app_id_hex=f"{scanned_record.app_id:08X}" if scanned_record.app_id is not None else None,
        key_revision=key_material.revision if key_material is not None else None,
        encoded_modulus=key_material.encoded_modulus if key_material is not None else None,
        encoded_public_exponent=key_material.encoded_public_exponent if key_material is not None else None,
        modulus_hex=modulus_hex,
        public_exponent=key_material.public_exponent if key_material is not None else None,
        public_exponent_hex=format_hex(key_material.public_exponent) if key_material is not None else None,
        private_exponent_hex=private_exponent_hex,
        private_exponent_source=private_exponent_source,
        prime_factors_hex=prime_factors_hex,
        factored_private_exponent_hex=factor_entry.private_exponent_hex if factor_entry is not None else None,
        factored_private_exponent_source=factor_entry.backend if factor_entry is not None else None,
        factored_prime_factors_hex=factor_entry.prime_factors_hex if factor_entry is not None else [],
        factored_elapsed_seconds=factor_entry.elapsed_seconds if factor_entry is not None else None,
        list_name=scanned_record.list_name,
        list_modulus_hex=list_modulus_hex,
        list_private_exponent_hex=list_private_exponent_hex,
        list_modulus_match=list_modulus_match,
        list_private_exponent_match=list_private_exponent_match,
        factored_private_exponent_match=factored_private_exponent_match,
        errors=errors,
    )


def summarize_records(records: list[KeyInventoryRecord]) -> dict[str, object]:
    revision_counts = Counter(record.key_revision for record in records if record.key_revision is not None)
    private_source_counts = Counter(record.private_exponent_source for record in records if record.private_exponent_source is not None)
    factored_source_counts = Counter(
        record.factored_private_exponent_source
        for record in records
        if record.factored_private_exponent_source is not None
    )
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
    verified_historical = [record for record in records if record.factored_private_exponent_match is not None]
    verified_historical_matches = [record for record in verified_historical if record.factored_private_exponent_match is True]
    verified_historical_mismatches = [record for record in verified_historical if record.factored_private_exponent_match is False]
    return {
        "dll_count": len(records),
        "app_id_count": sum(record.app_id is not None for record in records),
        "public_key_count": sum(record.modulus_hex is not None for record in records),
        "private_key_count": sum(record.private_exponent_hex is not None for record in records),
        "private_source_counts": dict(sorted(private_source_counts.items())),
        "factored_private_key_count": sum(record.factored_private_exponent_hex is not None for record in records),
        "factored_source_counts": dict(sorted(factored_source_counts.items())),
        "verified_historical_private_key_count": len(verified_historical),
        "verified_historical_private_key_match_count": len(verified_historical_matches),
        "verified_historical_private_key_mismatch_count": len(verified_historical_mismatches),
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
        f"- Private exponents available: {summary['private_key_count']}",
        f"- Factored private exponents: {summary['factored_private_key_count']}",
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

    private_source_counts = summary["private_source_counts"]
    if private_source_counts:
        lines.extend(
            [
                "",
                "## Private Exponent Sources",
                "",
                "| Source | Count |",
                "| --- | ---: |",
            ]
        )
        for source, count in private_source_counts.items():
            lines.append(f"| {source} | {count} |")

    factored_source_counts = summary["factored_source_counts"]
    if factored_source_counts:
        lines.extend(
            [
                "",
                "## Factoring Backends",
                "",
                "| Backend | Count |",
                "| --- | ---: |",
            ]
        )
        for source, count in factored_source_counts.items():
            lines.append(f"| {source} | {count} |")

    if summary["verified_historical_private_key_count"]:
        lines.extend(
            [
                "",
                "## Historical Verification",
                "",
                f"- Historical rows re-factored: {summary['verified_historical_private_key_count']}",
                f"- Matches: {summary['verified_historical_private_key_match_count']}",
                f"- Mismatches: {summary['verified_historical_private_key_mismatch_count']}",
            ]
        )
        verification_mismatches = [record for record in records if record.factored_private_exponent_match is False]
        if verification_mismatches:
            lines.extend(
                [
                    "",
                    "| Game | App ID | Historical D | Factored D |",
                    "| --- | ---: | --- | --- |",
                ]
            )
            for record in verification_mismatches[:20]:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            record.game_name_guess,
                            str(record.app_id),
                            record.list_private_exponent_hex or "",
                            record.factored_private_exponent_hex or "",
                        ]
                    )
                    + " |"
                )

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
                "| Game | App ID | Revision | Modulus | D | Source |",
                "| --- | ---: | --- | --- | --- | --- |",
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
                        record.private_exponent_source or "",
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
    parser.add_argument("--list-path", type=Path, default=HISTORICAL_LIST_PATH, help="path to list.txt for comparison")
    parser.add_argument(
        "--list-history-root",
        type=Path,
        default=default_list_history_root(),
        help="root containing historical listkg_* snapshots for exact private-exponent recovery",
    )
    parser.add_argument("--json-out", type=Path, help="write JSON inventory output")
    parser.add_argument("--markdown-out", type=Path, help="write Markdown report output")
    parser.add_argument("--limit", type=int, help="scan at most this many DLLs")
    parser.add_argument("--skip-factor", action="store_true", help="skip private-exponent derivation and only inventory embedded public keys")
    parser.add_argument(
        "--skip-factor-remaining",
        action="store_true",
        help="recover private exponents from exact historical list matches but do not factor unknown moduli",
    )
    parser.add_argument(
        "--verify-known",
        action="store_true",
        help="re-factor exact historical matches and verify the recovered private exponent",
    )
    parser.add_argument(
        "--factor-backend",
        choices=("auto", "internal", "msieve"),
        default="auto",
        help="factoring backend to use for unknown or verification work",
    )
    parser.add_argument(
        "--msieve-bin",
        type=Path,
        default=default_msieve_path(),
        help="path to the msieve binary for fast external factoring",
    )
    parser.add_argument(
        "--factor-cache",
        type=Path,
        help="append-only JSONL cache for resumable per-modulus factoring results",
    )
    parser.add_argument("--stdout-json", action="store_true", help="emit the JSON report to stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.skip_factor and args.verify_known:
        raise SystemExit("--verify-known cannot be used together with --skip-factor")

    extracted_root = args.extracted_root.resolve()
    source_id = infer_source_id_from_extracted_root(extracted_root)
    entries = load_entries(args.list_path.resolve())
    historical_entries = load_historical_private_entries(args.list_history_root.resolve())
    msieve_bin = args.msieve_bin.resolve()

    dll_paths = discover_support_dlls(extracted_root)
    if args.limit is not None:
        dll_paths = dll_paths[: args.limit]

    scanned_records = [scan_record(dll_path, entries, historical_entries) for dll_path in dll_paths]
    factor_cache = args.factor_cache
    if factor_cache is None and source_id is not None and (args.verify_known or not args.skip_factor):
        factor_cache = default_factor_cache_path(source_id)
    if factor_cache is not None:
        factor_cache = factor_cache.resolve()

    existing_factor_cache = load_factor_cache(factor_cache)
    pending_factor_work_items = collect_factor_work_items(
        scanned_records,
        derive_private=not args.skip_factor,
        factor_remaining=not args.skip_factor_remaining,
        verify_known=args.verify_known,
    )
    factor_results, factor_errors = factor_work_items(
        pending_factor_work_items,
        existing_cache=existing_factor_cache,
        factor_backend=args.factor_backend,
        msieve_bin=msieve_bin,
        factor_cache_path=factor_cache,
    )

    records = [
        build_record(
            scanned_record,
            factor_results=factor_results,
            factor_errors=factor_errors,
            derive_private=not args.skip_factor,
            factor_remaining=not args.skip_factor_remaining,
            verify_known=args.verify_known,
        )
        for scanned_record in scanned_records
    ]
    records.sort(key=lambda record: (record.app_id is None, record.app_id or -1, record.game_name_guess.casefold()))
    summary = summarize_records(records)

    report = {
        "source_id": source_id,
        "source_label": source_label(source_id) if source_id is not None else None,
        "extracted_root": display_path(extracted_root),
        "list_path": display_path(args.list_path.resolve()),
        "list_history_root": display_path(args.list_history_root.resolve()),
        "factor_backend": resolve_factor_backend(args.factor_backend, msieve_bin),
        "factor_cache_path": display_path(factor_cache) if factor_cache is not None else None,
        "verify_known": args.verify_known,
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
        if summary["private_source_counts"]:
            print(f"private_sources={json.dumps(summary['private_source_counts'], sort_keys=True)}")
        if summary["factored_source_counts"]:
            print(f"factored_sources={json.dumps(summary['factored_source_counts'], sort_keys=True)}")
        if summary["verified_historical_private_key_count"]:
            print(f"verified_historical_private_keys={summary['verified_historical_private_key_count']}")
            print(
                f"verified_historical_private_key_mismatches="
                f"{summary['verified_historical_private_key_mismatch_count']}"
            )
        print(f"public_list_matches={summary['public_list_matches']}")
        print(f"exact_list_matches={summary['exact_list_matches']}")
        print(f"errors={summary['failure_count']}")
        print(f"missing_list_entries={summary['missing_list_entry_count']}")
        print(f"list_mismatches={summary['list_mismatch_count']}")
        if factor_cache is not None:
            print(f"factor_cache={display_path(factor_cache)}")
        if json_out is not None:
            print(f"json_out={display_path(json_out.resolve())}")
        if markdown_out is not None:
            print(f"markdown_out={display_path(markdown_out.resolve())}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
