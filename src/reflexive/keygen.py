from __future__ import annotations

import argparse
import json
import math
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_LIST_PATH = Path(__file__).parent / "data" / "list.txt"

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ345679"
ALPHABET_INDEX = {ch: index for index, ch in enumerate(ALPHABET)}

MIX_TABLE_LONG = bytes.fromhex(
    "28ae77fb12d531608742ce004a700667fe3daa58e88edcc3bb257f2a2907240f"
    "96b9ff56b74ecf828f102d34e614a339d0f63b2173abbc94bdd44511e7e4a67b"
    "e2ccd2f32f4bb05e6f71f030890d1946685123a598eb26af918ab54c5cf4c8a8"
    "64f876ea7c69ba50050a619e1890dbaccb664fd1f1369f1e4815f50c160963bf"
    "7922e51aee3332525a0e850ba9781fb8b255838092ed031d47a1dda4e9546e9a"
    "9335f757846b95c59c38cd7dda088cc69dc23aa7dfd343fddec1048159971bb1"
    "d66d9bc7f2206acad97ec499e13e2b3fd8a2445fa0d7135d40378bbe725b744d"
    "ec62e08defb3c053656c2c4986c97a3c17b40127fc41f975e31cfa0288ad2eb6"
)
MIX_TABLE_SHORT = bytes.fromhex(
    "330692f73d71d07afe6ed99f09287cbf5d1ae18575d730204eabed8b5e73a247"
    "9c9023292cf2cbba42f58e9ad54816d180041c1b452f4464e5b80e6241b4173e"
    "acdbe4e611af797dbdc8a868f36aa515b063c6de2649ee5357ae5a6c13fa82cd"
    "c0d352aabc4ca00b95122a219dcf025cc96bda03b23c81729be9313887a3f64b"
    "32b6ff61c314944d74a934896de34346fbea4a83bb0c7656dfb7b5fdd4548cca"
    "a65f96fc6724a1f84f3af9e0b97e8aa79786be2e37ddc4910d1e987f84000f2b"
    "403678c507eb3969efe27b27592dad1019c23ff170d26f505501355866b16077"
    "e7d80acef0b393d63b8dec9e5be88822991d0518c78f6525c1dc08a4ccf4511f"
)
KEY_MATERIAL = bytes.fromhex(
    "d0c9bf0400000000006c6973742e747874002e2f6c6973742e2a2e74787400"
    "00000000000000000000000000000000000000000000000000000000000000"
)

BASE9_DIGITS = "123456789"

REGISTRY_ROOTS = (
    r"HKEY_CURRENT_USER\SOFTWARE\ReflexiveArcade",
    r"HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\ReflexiveArcade",
    r"HKEY_LOCAL_MACHINE\SOFTWARE\ReflexiveArcade",
)


@dataclass
class ListkgEntry:
    name: str
    game_id: int
    modulus_hex: str
    exponent_hex: str

    @property
    def modulus(self) -> int:
        return int(self.modulus_hex, 16)

    @property
    def exponent(self) -> int:
        return int(self.exponent_hex, 16)


@dataclass
class ProductCodeData:
    raw_code: str
    normalized_code: str
    payload: str
    decoded_integer: int
    decoded_decimal: str
    game_id: int
    group_values: list[int]


@dataclass
class GeneratedKey:
    game_id: int
    game_name: str
    group_values: list[int]
    registration_body: str
    registration_code: str
    unlock_code: str


def load_entries(path: Path) -> dict[int, ListkgEntry]:
    entries: dict[int, ListkgEntry] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip().strip("|")
        if not line:
            continue
        parts = line.split("|")
        if len(parts) < 4:
            continue
        entry = ListkgEntry(
            name=parts[0],
            game_id=int(parts[1]),
            modulus_hex=parts[2],
            exponent_hex=parts[3],
        )
        entries[entry.game_id] = entry
    return entries


def normalize_product_code(code: str) -> str:
    stripped = code
    for ch in " ,.'\"-/":
        stripped = stripped.replace(ch, "")
    return stripped.upper()


def normalize_payload_char(ch: str) -> str:
    if ch == "0":
        return "O"
    if ch == "1":
        return "I"
    if ch == "2":
        return "Z"
    if ch == "8":
        return "B"
    return ch


def decode_payload_integer(payload: str) -> int:
    value = 0
    for raw_ch in payload:
        ch = normalize_payload_char(raw_ch)
        if ch not in ALPHABET_INDEX:
            raise ValueError(f"unsupported payload character: {raw_ch!r}")
        value = (value << 5) | ALPHABET_INDEX[ch]
    return value


def encode_payload_integer(value: int) -> str:
    if value < 0:
        raise ValueError("payload integer must be non-negative")
    if value == 0:
        return ALPHABET[0]
    chars: list[str] = []
    current = value
    while current:
        chars.append(ALPHABET[current & 0x1F])
        current >>= 5
    return "".join(reversed(chars))


def decode_game_id(prefix: str) -> int:
    total = 0
    for ch in prefix[:6]:
        digit = ord(ch) - ord("1")
        if digit < 0 or digit > 8:
            raise ValueError(f"invalid base-9 digit in game id: {ch!r}")
        total = total * 9 + digit
    return total


def encode_base9(value: int, width: int | None = None) -> str:
    if value < 0:
        raise ValueError("base-9 values must be non-negative")
    if value == 0:
        digits = ["1"]
    else:
        digits: list[str] = []
        current = value
        while current:
            current, remainder = divmod(current, 9)
            digits.append(BASE9_DIGITS[remainder])
        digits.reverse()
    encoded = "".join(digits)
    if width is not None:
        encoded = encoded.rjust(width, "1")
    return encoded


def extract_group_values(suffix: str) -> list[int]:
    groups: list[int] = []
    index = 0
    while index + 4 <= len(suffix) and len(groups) < 6:
        if suffix[index] == "0":
            break
        chunk = suffix[index : index + 4]
        if len(chunk) < 4:
            break
        value = 0
        for ch in chunk:
            digit = ord(ch) - ord("1")
            if digit < 0 or digit > 8:
                raise ValueError(f"invalid base-9 digit in group value: {ch!r}")
            value = value * 9 + digit
        groups.append(value)
        index += 4
    return groups


def encode_group_value(value: int) -> str:
    if value < 0 or value >= 9**4:
        raise ValueError("group values must fit in four base-9 digits")
    return encode_base9(value, width=4)


def parse_product_code(raw_code: str) -> ProductCodeData:
    normalized = normalize_product_code(raw_code)
    if len(normalized) < 6 or not normalized.startswith("E"):
        raise ValueError("expected an E-type Reflexive product code")

    payload = normalized[2:-2]
    if not payload:
        raise ValueError("product code payload is empty")

    decoded_integer = decode_payload_integer(payload)
    decoded_decimal = str(decoded_integer)

    first_zero = decoded_decimal.find("0")
    if first_zero <= 0:
        raise ValueError("product code is missing the first separator")

    second_zero = decoded_decimal.find("0", first_zero + 1)
    if second_zero == -1:
        raise ValueError("product code is missing the second separator")

    game_id = decode_game_id(decoded_decimal[:first_zero])
    group_values = extract_group_values(decoded_decimal[second_zero + 1 :])
    if not group_values:
        raise ValueError("product code does not contain any registration groups")

    return ProductCodeData(
        raw_code=raw_code,
        normalized_code=normalized,
        payload=payload,
        decoded_integer=decoded_integer,
        decoded_decimal=decoded_decimal,
        game_id=game_id,
        group_values=group_values,
    )


def normalize_revision_char(revision: str) -> str:
    if len(revision) != 1:
        raise ValueError("revision must be a single character")
    normalized = normalize_payload_char(revision.upper())
    if normalized not in ALPHABET_INDEX:
        raise ValueError(f"unsupported revision character: {revision!r}")
    return normalized


def synthesize_product_code(
    game_id: int,
    group_values: Iterable[int],
    middle: str = "1",
    revision: str = "A",
) -> str:
    group_digits = "".join(encode_group_value(value) for value in group_values)
    decimal_string = f"{encode_base9(game_id)}0{middle}0{group_digits}0"
    payload = encode_payload_integer(int(decimal_string))
    return f"E{normalize_revision_char(revision)}{payload}AA"


def crc32_text(text: str) -> int:
    return zlib.crc32(text.encode("ascii")) & 0xFFFFFFFF


def build_registration_body(game_id: int, group_values: list[int]) -> str:
    return "4" + "".join(f"{crc32_text(f'{game_id}{value}') % 10000:04d}" for value in group_values[:5])


def build_registration_code(game_id: int, group_values: list[int]) -> tuple[str, str]:
    body = build_registration_body(game_id, group_values)
    return body, f"{body}{crc32_text(body) % 100:02d}"


def mix_bytes(source: bytes, output_length: int) -> bytes:
    table = MIX_TABLE_LONG if len(source) >= output_length else MIX_TABLE_SHORT
    mixed = bytearray(output_length)
    for index in range(output_length):
        value = table[index & 0xFF]
        for byte in source:
            value = table[byte ^ value]
        mixed[index] = value
    return bytes(mixed)


def build_message_bytes(registration_code: str) -> bytes:
    raw_value = int(registration_code)
    raw_bytes = raw_value.to_bytes(32, "little")
    significant = raw_bytes.rstrip(b"\x00")
    if not significant:
        significant = b"\x00"

    buffer = bytearray(0x20)
    buffer[0:2] = (10).to_bytes(2, "little")
    data = buffer[2:22]

    size = len(significant)
    data[0x11] = size
    data[0x12] = 0x1F

    pad = 0x11 - size
    data[pad : pad + size] = significant

    quotient = (pad * 2) // 3
    left_span = pad - quotient
    right_span = size + quotient

    first_mix = mix_bytes(KEY_MATERIAL[:left_span], right_span)
    for index, byte in enumerate(first_mix):
        data[left_span + index] ^= byte

    second_mix = mix_bytes(bytes(data[left_span : left_span + right_span]), left_span)
    data[:left_span] = second_mix

    for index in range(left_span):
        data[index] ^= KEY_MATERIAL[index]

    return bytes(data)


def encode_unlock_value(value: int) -> str:
    if value < 0:
        raise ValueError("unlock values must be non-negative")

    byte_length = max(1, (value.bit_length() + 7) // 8)
    word_count = max(1, (byte_length + 1) // 2)
    char_count = math.ceil(word_count * 16 / 5)
    chars = [ALPHABET[(value >> (5 * index)) & 0x1F] for index in range(char_count)]
    return "F" + "".join(reversed(chars))


def build_unlock_code(entry: ListkgEntry, registration_code: str) -> str:
    message_int = int.from_bytes(build_message_bytes(registration_code), "little")
    unlock_int = pow(message_int, entry.exponent, entry.modulus)
    return encode_unlock_value(unlock_int)


def generate_for_entry(entry: ListkgEntry, group_values: list[int]) -> GeneratedKey:
    registration_body, registration_code = build_registration_code(entry.game_id, group_values)
    unlock_code = build_unlock_code(entry, registration_code)
    return GeneratedKey(
        game_id=entry.game_id,
        game_name=entry.name,
        group_values=group_values[:5],
        registration_body=registration_body,
        registration_code=registration_code,
        unlock_code=unlock_code,
    )


def render_reg(entries: Iterable[GeneratedKey]) -> str:
    lines = ["Windows Registry Editor Version 5.00", ""]
    for item in entries:
        for registry_root in REGISTRY_ROOTS:
            lines.append(f"[{registry_root}\\{item.game_id}]")
            lines.append(f"\"RegistrationCode\"=\"{item.registration_code}\"")
            lines.append(f"\"UnlockCode\"=\"{item.unlock_code}\"")
            lines.append("")
    return "\r\n".join(lines) + "\r\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pure-Python fallback for russiankid's Reflexive Arcade keygen.")
    parser.add_argument("product_code", nargs="?", help="E-type Reflexive product code")
    parser.add_argument("--list-path", type=Path, default=DEFAULT_LIST_PATH, help="path to list.txt")
    parser.add_argument("--all", action="store_true", help="generate keys for every game in list.txt using the product code's registration groups")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--reg-out", type=Path, help="write registry file output")
    parser.add_argument("--synthesize", action="store_true", help="build a synthetic product code for testing instead of decoding one")
    parser.add_argument("--game-id", type=int, help="game id for --synthesize")
    parser.add_argument("--groups", help="comma-separated base-10 group values for --synthesize")
    parser.add_argument(
        "--revision",
        default="A",
        help="synthetic product-code revision character for --synthesize (typically A or B)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    entries = load_entries(args.list_path.resolve())

    if args.synthesize:
        if args.game_id is None or not args.groups:
            raise SystemExit("--synthesize requires --game-id and --groups")
        group_values = [int(part) for part in args.groups.split(",") if part]
        print(synthesize_product_code(args.game_id, group_values, revision=args.revision))
        return 0

    if not args.product_code:
        raise SystemExit("product_code is required unless --synthesize is used")

    product = parse_product_code(args.product_code)

    if args.all:
        generated = [generate_for_entry(entry, product.group_values) for entry in entries.values()]
        if args.reg_out:
            args.reg_out.write_text(render_reg(generated), encoding="utf-8", newline="")
        if args.json:
            print(json.dumps([asdict(item) for item in generated], indent=2))
        else:
            print(f"product_code={product.normalized_code}")
            print(f"group_values={','.join(str(value) for value in product.group_values[:5])}")
            print(f"games={len(generated)}")
        return 0

    entry = entries.get(product.game_id)
    if entry is None:
        raise SystemExit(f"unknown game id: {product.game_id}")

    generated = generate_for_entry(entry, product.group_values)
    if args.reg_out:
        args.reg_out.write_text(render_reg([generated]), encoding="utf-8", newline="")

    if args.json:
        print(json.dumps({"product": asdict(product), "generated": asdict(generated)}, indent=2))
    else:
        print(f"product_code={product.normalized_code}")
        print(f"decoded_decimal={product.decoded_decimal}")
        print(f"game_id={generated.game_id}")
        print(f"game_name={generated.game_name}")
        print(f"group_values={','.join(str(value) for value in generated.group_values)}")
        print(f"registration_code={generated.registration_code}")
        print(f"unlock_code={generated.unlock_code}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
