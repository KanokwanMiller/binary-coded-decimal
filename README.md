# Binary Coded Decimal

Encodes and decodes non-negative integers to and from packed and unpacked BCD byte representations.

```python
from binary_coded_decimal import pack, unpack, encode_unpacked, decode_unpacked

pack(123)            # b'\x01\x23'
unpack(b'\x12\x34')  # 1234
encode_unpacked(12)  # b'\x01\x02'
decode_unpacked(b'\x01\x02')  # 12
```

## Why this exists

Some legacy systems, financial protocols, and hardware interfaces exchange numbers in BCD rather than plain binary. Doing this by hand is a source of off-by-one nibble errors. This library provides two functions for each direction: `pack`/`unpack` for packed BCD (two digits per byte), and `encode_unpacked`/`decode_unpacked` for unpacked BCD (one digit per byte, values 0x00-0x09).

The trade-off: only non-negative integers are supported. Negative BCD encodings exist (ten's complement, sign nibbles in 0x0A-0x0F), but there is no single universal convention. Rather than implement one of several conflicting schemes and call it standard, the library refuses negative input.

## Edge cases

Packed BCD with an odd number of digits is left-padded with a zero nibble (`pack(1)` returns `b'\x01'`, not a single-nibble value). This is lossless: `unpack(pack(1))` returns `1`. Unpacked BCD always produces at least one byte, so `encode_unpacked(0)` returns `b'\x00'`, not `b''`.

Decoding rejects any nibble or byte outside 0-9 by raising `InvalidBCDError` (a subclass of `ValueError`).
