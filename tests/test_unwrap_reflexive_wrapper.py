import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

SPEC = importlib.util.spec_from_file_location(
    "unwrap_reflexive_wrapper",
    SCRIPTS_DIR / "unwrap_reflexive_wrapper.py",
)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


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


class NativeEncryptedRegionTests(unittest.TestCase):
    def test_native_region_skips_wrapper_stub_bytes(self) -> None:
        pe = FakePE(
            0x1100,
            [FakeSection(virtual_address=0x1000, virtual_size=0x2000, raw_size=0x1000, raw_offset=0x400)],
        )

        self.assertEqual(MODULE.native_encrypted_region(pe, False), (0x505, 0xEFB))

    def test_short_fixed_region_clamps_then_skips_stub(self) -> None:
        pe = FakePE(
            0x1100,
            [FakeSection(virtual_address=0x1000, virtual_size=0x2000, raw_size=0x1000, raw_offset=0x400)],
        )

        self.assertEqual(MODULE.native_encrypted_region(pe, True), (0x505, 0x7B))

    def test_native_region_requires_payload_after_entry_stub(self) -> None:
        pe = FakePE(
            0x100B,
            [FakeSection(virtual_address=0x1000, virtual_size=0x10, raw_size=0x10, raw_offset=0x400)],
        )

        with self.assertRaisesRegex(RuntimeError, "too short"):
            MODULE.native_encrypted_region(pe, False)


class CliBehaviorTests(unittest.TestCase):
    def test_parse_args_requires_extracted_root(self) -> None:
        with self.assertRaises(SystemExit):
            MODULE.parse_args([])

    def test_parse_args_accepts_explicit_extracted_root(self) -> None:
        args = MODULE.parse_args(["--extracted-root", "artifacts/extracted/rutracker", "--force"])

        self.assertEqual(args.extracted_root, Path("artifacts/extracted/rutracker"))
        self.assertTrue(args.force)

    def test_default_output_root_requires_source_scoped_root(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "unable to infer source id"):
            MODULE.default_output_root(Path("/tmp/reflexive-extracted"))


if __name__ == "__main__":
    unittest.main()
