"""CRC32 — Cyclic Redundancy Check (IEEE 802.3).

A polynomial-based checksum designed for **error detection** in network
frames (Ethernet), archives (ZIP, PNG), and storage.  Excellent at
catching burst errors.  CRC32's polynomial mixing actually provides good
distribution and near-perfect avalanche (~49%), but its linearity over
GF(2) lets an attacker compute exactly how any input change affects the
output and craft collisions at will — making it unsuitable for hash
tables facing untrusted input.

Uses a pre-computed 256-entry lookup table to turn 8 bit-level operations
per byte into a single table lookup.
"""

MASK32 = 0xFFFF_FFFF
CRC32_POLY = 0xEDB8_8320  # bit-reversed IEEE polynomial

_CRC32_TABLE = []
for _byte in range(256):
    _crc = _byte
    for _ in range(8):
        if _crc & 1:
            _crc = (_crc >> 1) ^ CRC32_POLY
        else:
            _crc >>= 1
    _CRC32_TABLE.append(_crc & MASK32)


def crc32(data: bytes, seed: int = 0) -> int:
    """CRC32 (IEEE 802.3) — matches zlib.crc32() output."""
    crc = (seed ^ MASK32) & MASK32
    for b in data:
        crc = _CRC32_TABLE[(crc ^ b) & 0xFF] ^ (crc >> 8)
        crc &= MASK32
    return crc ^ MASK32
