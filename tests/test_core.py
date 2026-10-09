"""Tests for binary_coded_decimal.core.

Every test name below corresponds to behaviour the implementation
actually claims to support. We test non-negative integers only,
because negative BCD encodings are intentionally rejected.
"""

import unittest

from binary_coded_decimal import (
    pack,
    unpack,
    encode_unpacked,
    decode_unpacked,
    InvalidBCDError,
)


class TestPack(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(pack(0), b"\x00")

    def test_single_digit(self):
        self.assertEqual(pack(7), b"\x07")

    def test_two_digits(self):
        self.assertEqual(pack(12), b"\x12")

    def test_three_digits_padded(self):
        self.assertEqual(pack(123), b"\x01\x23")

    def test_large_number(self):
        self.assertEqual(pack(12345678), b"\x12\x34\x56\x78")

    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            pack(-1)

    def test_rejects_bool(self):
        with self.assertRaises(TypeError):
            pack(True)

    def test_rejects_non_int(self):
        with self.assertRaises(TypeError):
            pack("12")  # type: ignore[arg-type]


class TestUnpack(unittest.TestCase):
    def test_zero_byte(self):
        self.assertEqual(unpack(b"\x00"), 0)

    def test_single_byte(self):
        self.assertEqual(unpack(b"\x12"), 12)

    def test_multiple_bytes(self):
        self.assertEqual(unpack(b"\x01\x23"), 123)

    def test_leading_zero_nibble_preserved_in_roundtrip(self):
        self.assertEqual(unpack(b"\x00\x12"), 12)

    def test_rejects_invalid_high_nibble(self):
        with self.assertRaises(InvalidBCDError):
            unpack(b"\xab")

    def test_rejects_invalid_low_nibble(self):
        with self.assertRaises(InvalidBCDError):
            unpack(b"\x0a")

    def test_rejects_non_bytes(self):
        with self.assertRaises(TypeError):
            unpack("12")  # type: ignore[arg-type]

    def test_accepts_bytearray(self):
        self.assertEqual(unpack(bytearray(b"\x12\x34")), 1234)


class TestEncodeUnpacked(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(encode_unpacked(0), b"\x00")

    def test_single_digit(self):
        self.assertEqual(encode_unpacked(7), b"\x07")

    def test_multiple_digits(self):
        self.assertEqual(encode_unpacked(123), b"\x01\x02\x03")

    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            encode_unpacked(-5)

    def test_rejects_bool(self):
        with self.assertRaises(TypeError):
            encode_unpacked(False)


class TestDecodeUnpacked(unittest.TestCase):
    def test_zero_byte(self):
        self.assertEqual(decode_unpacked(b"\x00"), 0)

    def test_single_digit(self):
        self.assertEqual(decode_unpacked(b"\x05"), 5)

    def test_multiple_digits(self):
        self.assertEqual(decode_unpacked(b"\x01\x02\x03"), 123)

    def test_rejects_byte_above_nine(self):
        with self.assertRaises(InvalidBCDError):
            decode_unpacked(b"\x0a")

    def test_rejects_non_bytes(self):
        with self.assertRaises(TypeError):
            decode_unpacked(12)  # type: ignore[arg-type]

    def test_accepts_bytearray(self):
        self.assertEqual(decode_unpacked(bytearray(b"\x01\x02")), 12)


class TestRoundTrip(unittest.TestCase):
    def test_packed_roundtrip(self):
        for value in [0, 1, 9, 10, 99, 100, 999, 12345, 10 ** 20]:
            with self.subTest(value=value):
                self.assertEqual(unpack(pack(value)), value)

    def test_unpacked_roundtrip(self):
        for value in [0, 1, 9, 10, 99, 100, 999, 12345, 10 ** 20]:
            with self.subTest(value=value):
                self.assertEqual(decode_unpacked(encode_unpacked(value)), value)


if __name__ == "__main__":
    unittest.main()
