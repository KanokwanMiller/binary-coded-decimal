"""Core BCD encode/decode logic.

Two flavours of Binary Coded Decimal are supported:

    * Packed BCD: two decimal digits per byte, high nibble first.
      The integer 12 becomes b'\\x12'. An odd digit count is padded
      with a leading zero, so 1 -> b'\\x01'. This zero-padding is
      lossless, which is why round-tripping works regardless of
      digit-count parity.

    * Unpacked BCD: one digit per byte, each byte holding 0x00-0x09.
      The integer 12 becomes b'\\x01\\x02'. This wastes a byte per
      digit but is the form some legacy hardware expects.

Only non-negative integers are supported. Negative BCD encodings
exist in the wild (ten's complement, sign nibbles, etc.) but there
is no single standard, so we refuse rather than guess.
"""


class InvalidBCDError(ValueError):
    """Raised when input is not a valid BCD-encoded byte string.

    Subclassing ValueError keeps it catchable alongside ordinary
    value validation errors, while still allowing callers to
    distinguish BCD-specific failures if they need to.
    """


def _validate_non_negative(value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("value must be a non-negative int, not bool")
    if value < 0:
        raise ValueError("value must be non-negative")


def pack(value: int) -> bytes:
    """Encode a non-negative integer as packed BCD.

    Returns a bytes object with two digits per byte, most-significant
    digit in the high nibble. An odd digit count is left-padded with
    a single zero nibble, making the operation reversible for any
    non-negative int.

    pack(0)   -> b'\\x00'
    pack(1)   -> b'\\x01'
    pack(12)  -> b'\\x12'
    pack(123) -> b'\\x01\\x23'
    """
    _validate_non_negative(value)

    if value == 0:
        return b"\x00"

    digits: list[int] = []
    remaining = value
    while remaining > 0:
        digits.append(remaining % 10)
        remaining //= 10
    digits.reverse()

    if len(digits) % 2 != 0:
        digits.insert(0, 0)

    return bytes((digits[i] << 4) | digits[i + 1] for i in range(0, len(digits), 2))


def unpack(data: bytes) -> int:
    """Decode packed BCD bytes back into a non-negative integer.

    Each byte must contain two valid decimal digits (0-9) in its
    nibbles. Leading zero nibbles are preserved in the byte string
    but naturally collapse to leading zeros in the returned integer,
    which is the identity-preserving behaviour for round-trips.

    Raises InvalidBCDError if any nibble is outside 0-9.
    Raises TypeError if data is not bytes or bytearray.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes or bytearray")

    result = 0
    for byte in data:
        high = (byte >> 4) & 0x0F
        low = byte & 0x0F
        if high > 9 or low > 9:
            raise InvalidBCDError(
                f"byte 0x{byte:02x} is not valid packed BCD "
                f"(nibbles {high}, {low})"
            )
        result = result * 100 + high * 10 + low

    return result


def encode_unpacked(value: int) -> bytes:
    """Encode a non-negative integer as unpacked BCD.

    Returns a bytes object with one decimal digit per byte, each
    byte in the range 0x00-0x09. The integer 0 produces b'\\x00'
    (one byte), not an empty bytestring, so decoding is unambiguous.

    encode_unpacked(0)   -> b'\\x00'
    encode_unpacked(12)  -> b'\\x01\\x02'
    encode_unpacked(123) -> b'\\x01\\x02\\x03'
    """
    _validate_non_negative(value)

    if value == 0:
        return b"\x00"

    digits: list[int] = []
    remaining = value
    while remaining > 0:
        digits.append(remaining % 10)
        remaining //= 10
    digits.reverse()

    return bytes(digits)


def decode_unpacked(data: bytes) -> int:
    """Decode unpacked BCD bytes back into a non-negative integer.

    Each byte must hold a single decimal digit (0x00-0x09). Leading
    zero bytes collapse naturally in the integer result.

    Raises InvalidBCDError if any byte is outside 0x00-0x09.
    Raises TypeError if data is not bytes or bytearray.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes or bytearray")

    result = 0
    for byte in data:
        if byte > 9:
            raise InvalidBCDError(
                f"byte 0x{byte:02x} is not valid unpacked BCD "
                f"(must be 0x00-0x09)"
            )
        result = result * 10 + byte

    return result
