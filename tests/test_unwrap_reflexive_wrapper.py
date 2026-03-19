from pathlib import Path

import pytest

from reflexive import unwrap_reflexive_wrapper as MODULE


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


def test_native_region_skips_wrapper_stub_bytes() -> None:
    pe = FakePE(
        0x1100,
        [FakeSection(virtual_address=0x1000, virtual_size=0x2000, raw_size=0x1000, raw_offset=0x400)],
    )

    assert MODULE.native_encrypted_region(pe, False) == (0x505, 0xEFB)

def test_short_fixed_region_clamps_then_skips_stub() -> None:
    pe = FakePE(
        0x1100,
        [FakeSection(virtual_address=0x1000, virtual_size=0x2000, raw_size=0x1000, raw_offset=0x400)],
    )

    assert MODULE.native_encrypted_region(pe, True) == (0x505, 0x7B)

def test_native_region_requires_payload_after_entry_stub() -> None:
    pe = FakePE(
        0x100B,
        [FakeSection(virtual_address=0x1000, virtual_size=0x10, raw_size=0x10, raw_offset=0x400)],
    )

    with pytest.raises(RuntimeError, match="too short"):
        MODULE.native_encrypted_region(pe, False)

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
