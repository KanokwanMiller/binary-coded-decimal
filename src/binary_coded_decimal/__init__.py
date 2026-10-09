"""Binary Coded Decimal encoding and decoding.

Public API:
    pack           -- non-negative int -> bytes (packed BCD, two nibbles per byte)
    unpack         -- bytes            -> int (inverse of pack)
    encode_unpacked -- non-negative int -> bytes (one digit per byte, 0x00-0x09)
    decode_unpacked -- bytes            -> int (inverse of encode_unpacked)
"""

from .core import (
    pack,
    unpack,
    encode_unpacked,
    decode_unpacked,
    InvalidBCDError,
)

__all__ = [
    "pack",
    "unpack",
    "encode_unpacked",
    "decode_unpacked",
    "InvalidBCDError",
]
