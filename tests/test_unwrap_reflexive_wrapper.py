import struct
from pathlib import Path

import pytest

from reflexive import unwrap as MODULE
from reflexive.unwrap import Strategy


class FakeOptionalHeader:
    def __init__(self, entrypoint: int) -> None:
        self.AddressOfEntryPoint = entrypoint


class FakeSection:
    def __init__(self, *, virtual_address: int, virtual_size: int, raw_size: int, raw_offset: int) -> None:
        self.VirtualAddress = virtual_address
        self.Misc_VirtualSize = virtual_size
        self.SizeOfRawData = raw_size
        self.PointerToRawData = raw_offset


class FakePE:
    def __init__(self, entrypoint: int, sections: list[FakeSection]) -> None:
        self.OPTIONAL_HEADER = FakeOptionalHeader(entrypoint)
        self.sections = sections


IMAGE_BASE = 0x400000
TEXT_RVA = 0x1000
TEXT_OFFSET = 0x200
ENTRY_OFFSET = 0x60
CONFIG_TEXT = b"App Version String=Rev. 4876\r\nApplication Name=Test\r\nDemo Time Seconds=3600\r\n"


def align(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def x86_code(function_count: int) -> bytes:
    # push ebp; mov ebp, esp; sub esp, 0x10; push esi; mov eax, [ebp+8]; test eax, eax; je +5;
    # call next; pop esi; mov esp, ebp; pop ebp; ret
    function = bytes.fromhex("558bec83ec10568b450885c07405e8000000005e8be55dc3")
    return function * function_count


def build_pe(code: bytes, entry_offset: int) -> bytes:
    raw_size = align(len(code), 0x200)
    image_size = TEXT_RVA + align(len(code), 0x1000)
    coff_header = struct.pack("<4sHHIIIHH", b"PE\0\0", 0x14C, 1, 0, 0, 0, 0xE0, 0x102)
    optional_header = struct.pack(
        "<HBBIIIIIIIIIHHHHHHIIIIHHIIIIII",
        0x10B, 6, 0, raw_size, 0, 0, TEXT_RVA + entry_offset, TEXT_RVA, TEXT_RVA + raw_size,
        IMAGE_BASE, 0x1000, 0x200, 4, 0, 0, 0, 4, 0, 0, image_size, TEXT_OFFSET, 0, 2, 0,
        0x100000, 0x1000, 0x100000, 0x1000, 0, 16,
    ) + bytes(16 * 8)
    section_header = struct.pack(
        "<8sIIIIIIHHI", b".text", len(code), TEXT_RVA, raw_size, TEXT_OFFSET, 0, 0, 0, 0, 0x60000020
    )
    headers = b"MZ" + bytes(0x3A) + struct.pack("<I", 0x40) + coff_header + optional_header + section_header
    return headers.ljust(TEXT_OFFSET, b"\0") + code.ljust(raw_size, b"\0")


def encrypt_with_stream(data: bytes, seed: int) -> bytes:
    state, a, b = MODULE.initialize_stream(seed)
    output = bytearray(len(data))
    for index, value in enumerate(data):
        key, a, b = MODULE.stream_next_byte(state, a, b)
        output[index] = (value + key) & 0xFF
    return bytes(output)


def write_wrapped_game(tmp_path: Path, *, wrapper_skips_entry: bool, payload_skip: int) -> tuple[Path, Strategy, bytes]:
    wrapper_root = tmp_path / "Game"
    reflexive_dir = wrapper_root / "ReflexiveArcade"
    reflexive_dir.mkdir(parents=True)

    wrapper_binary = wrapper_root / "game.exe"
    wrapper_binary.write_bytes(b"MZ" + (MODULE.NATIVE_ENTRY_SKIP_MARKER if wrapper_skips_entry else b""))
    (reflexive_dir / "RAW_003.wdt").write_bytes(bytes(0x100))

    plain_child = build_pe(x86_code(64), ENTRY_OFFSET)
    config_path = reflexive_dir / "RAW_002.wdt"
    encrypted_config = encrypt_with_stream(CONFIG_TEXT, len(plain_child))
    config_path.write_bytes(encrypted_config)

    seed2 = MODULE.derive_seed2(encrypted_config, MODULE.parse_config(CONFIG_TEXT))
    region_start = TEXT_OFFSET + ENTRY_OFFSET + payload_skip
    region_end = TEXT_OFFSET + len(x86_code(64))
    child = bytearray(plain_child)
    child[region_start:region_end] = encrypt_with_stream(plain_child[region_start:region_end], seed2)
    child_payload = wrapper_root / "game.RWG"
    child_payload.write_bytes(child)

    strategy = Strategy(
        kind="static",
        reason="test",
        wrapper_binary=wrapper_binary,
        output_executable_name="game.exe",
        child_payload=child_payload,
        config_path=config_path,
    )
    return wrapper_root, strategy, plain_child


def test_native_region_starts_at_entrypoint_without_skip() -> None:
    pe = FakePE(
        0x1100,
        [FakeSection(virtual_address=0x1000, virtual_size=0x2000, raw_size=0x1000, raw_offset=0x400)],
    )

    assert MODULE.native_encrypted_region(pe, False, 0) == (0x500, 0xF00)


def test_native_region_skips_wrapper_stub_bytes() -> None:
    pe = FakePE(
        0x1100,
        [FakeSection(virtual_address=0x1000, virtual_size=0x2000, raw_size=0x1000, raw_offset=0x400)],
    )

    assert MODULE.native_encrypted_region(pe, False, MODULE.NATIVE_ENTRY_SKIP) == (0x505, 0xEFB)

def test_short_fixed_region_clamps_then_skips_stub() -> None:
    pe = FakePE(
        0x1100,
        [FakeSection(virtual_address=0x1000, virtual_size=0x2000, raw_size=0x1000, raw_offset=0x400)],
    )

    assert MODULE.native_encrypted_region(pe, True, MODULE.NATIVE_ENTRY_SKIP) == (0x505, 0x7B)

def test_native_region_requires_payload_after_entry_stub() -> None:
    pe = FakePE(
        0x100B,
        [FakeSection(virtual_address=0x1000, virtual_size=0x10, raw_size=0x10, raw_offset=0x400)],
    )

    with pytest.raises(RuntimeError, match="too short"):
        MODULE.native_encrypted_region(pe, False, MODULE.NATIVE_ENTRY_SKIP)

def test_parse_args_requires_extracted_root() -> None:
    with pytest.raises(SystemExit):
        MODULE.parse_args([])

def test_parse_args_accepts_explicit_extracted_root() -> None:
    args = MODULE.parse_args(["--extracted-root", "artifacts/extracted/rutracker", "--force"])

    assert args.extracted_root == Path("artifacts/extracted/rutracker")
    assert args.force is True

def test_default_output_root_requires_source_scoped_root() -> None:
    with pytest.raises(RuntimeError, match="unable to infer source id"):
        MODULE.default_output_root(Path("/tmp/reflexive-extracted"))


def test_materialize_record_can_skip_existing_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    extracted_root = tmp_path / "extracted"
    wrapper_root = extracted_root / "Game"
    wrapper_root.mkdir(parents=True)
    destination_root = tmp_path / "unwrapped" / "Game"
    destination_root.mkdir(parents=True)
    direct_exe = wrapper_root / "game.exe"
    direct_exe.write_bytes(b"MZ")

    monkeypatch.setattr(
        MODULE,
        "choose_strategy",
        lambda record, wrapper_root: Strategy(
            kind="direct",
            reason="test",
            direct_executable=direct_exe,
            output_executable_name=direct_exe.name,
        ),
    )
    monkeypatch.setattr(MODULE, "copy_support_tree", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not copy")))

    record = {
        "root": "Game",
        "binary_candidates": [],
    }

    summary = MODULE.materialize_record(
        record,
        extracted_root,
        tmp_path / "unwrapped",
        False,
        skip_existing=True,
    )

    assert summary["status"] == "skipped_existing"


def test_pre_skip_wrapper_decrypts_from_entrypoint(tmp_path: Path) -> None:
    # Wrappers built before the 2010 entry-skip feature (e.g. Crimsonland 2008-08 .. 2009-01) encrypt from the
    # entrypoint itself; skipping five bytes there used to shift the keystream and leave the span scrambled.
    wrapper_root, strategy, plain_child = write_wrapped_game(tmp_path, wrapper_skips_entry=False, payload_skip=0)

    child, summary = MODULE.decrypt_static_child(wrapper_root, strategy)

    assert child == plain_child
    assert summary["entry_skip"] == 0
    assert summary["region_start"] == TEXT_OFFSET + ENTRY_OFFSET
    assert summary["code_check_ratio"] == 0


def test_entry_skip_wrapper_leaves_entry_stub_plaintext(tmp_path: Path) -> None:
    wrapper_root, strategy, plain_child = write_wrapped_game(
        tmp_path, wrapper_skips_entry=True, payload_skip=MODULE.NATIVE_ENTRY_SKIP
    )

    child, summary = MODULE.decrypt_static_child(wrapper_root, strategy)

    assert child == plain_child
    assert summary["entry_skip"] == MODULE.NATIVE_ENTRY_SKIP


def test_mismatched_entry_skip_fails_instead_of_emitting_garbage(tmp_path: Path) -> None:
    wrapper_root, strategy, _ = write_wrapped_game(tmp_path, wrapper_skips_entry=True, payload_skip=0)

    with pytest.raises(RuntimeError, match="not plausible x86"):
        MODULE.decrypt_static_child(wrapper_root, strategy)


def test_failed_static_unwrap_does_not_create_destination(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    wrapper_root, strategy, _ = write_wrapped_game(tmp_path, wrapper_skips_entry=True, payload_skip=0)
    monkeypatch.setattr(MODULE, "choose_strategy", lambda record, wrapper_root: strategy)
    record = {"root": wrapper_root.name, "binary_candidates": []}
    output_root = tmp_path / "unwrapped"

    with pytest.raises(RuntimeError, match="not plausible x86"):
        MODULE.materialize_record(record, tmp_path, output_root, False)

    assert not (output_root / wrapper_root.name).exists()
