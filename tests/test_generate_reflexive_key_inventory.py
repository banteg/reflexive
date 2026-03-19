from __future__ import annotations

import importlib.util
import unittest

from reflexive.generate_reflexive_key_inventory import derive_private_exponent, extract_embedded_key_material


class GenerateReflexiveKeyInventoryTest(unittest.TestCase):
    def test_extract_embedded_key_material(self) -> None:
        material, errors = extract_embedded_key_material(
            b"prefix\x00Decryption Key Data=A/3KBCE4G5QWXAW39ZEHQ46VLQFFQTKN\x00/CAAB\x00suffix"
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(material)
        assert material is not None
        self.assertEqual(material.revision, "A")
        self.assertEqual(material.encoded_modulus, "3KBCE4G5QWXAW39ZEHQ46VLQFFQTKN")
        self.assertEqual(material.encoded_public_exponent, "CAAB")
        self.assertEqual(material.modulus_hex, "34A0889B37216B82DAFE48786FB55C0A584D4D")
        self.assertEqual(material.public_exponent, 65537)

    @unittest.skipUnless(importlib.util.find_spec("sympy") is not None, "sympy speeds up factorization for this fixture")
    def test_derive_private_exponent(self) -> None:
        result = derive_private_exponent(int("34A0889B37216B82DAFE48786FB55C0A584D4D", 16), 65537)
        self.assertEqual(result.prime_factors_hex, ["06CF9D0B9A4D6F389A31", "07BA0EDB3385D2B101DD"])
        self.assertEqual(result.private_exponent_hex, "1ABD872BF6F35041892550797506D085A75901")


if __name__ == "__main__":
    unittest.main()
