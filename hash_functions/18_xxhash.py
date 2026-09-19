"""xxHash — Yann Collet (2012).

One of the fastest non-cryptographic hash functions while maintaining
excellent distribution.  Uses four parallel accumulators for high
throughput.  Found in LZ4 compression, FreeBSD, and the Linux kernel.

Reference: https://github.com/Cyan4973/xxHash/blob/dev/doc/xxhash_spec.md
"""

MASK32 = 0xFFFF_FFFF
PRIME1 = 0x9E37_79B1
PRIME2 = 0x85EB_CA77
PRIME3 = 0xC2B2_AE3D
PRIME4 = 0x27D4_EB2F
PRIME5 = 0x1656_67B1


def _rotl32(x: int, r: int) -> int:
    return ((x << r) | (x >> (32 - r))) & MASK32


def _round(acc: int, lane: int) -> int:
    acc = (acc + lane * PRIME2) & MASK32
    acc = _rotl32(acc, 13)
    acc = (acc * PRIME1) & MASK32
    return acc


def xxhash32(data: bytes, seed: int = 0) -> int:
    """XXH32 — xxHash 32-bit."""
    length = len(data)
    idx = 0

    if length >= 16:
        v1 = (seed + PRIME1 + PRIME2) & MASK32
        v2 = (seed + PRIME2) & MASK32
        v3 = seed & MASK32
        v4 = (seed - PRIME1) & MASK32
        while idx + 16 <= length:
            v1 = _round(v1, int.from_bytes(data[idx:idx+4], "little"))
            v2 = _round(v2, int.from_bytes(data[idx+4:idx+8], "little"))
            v3 = _round(v3, int.from_bytes(data[idx+8:idx+12], "little"))
            v4 = _round(v4, int.from_bytes(data[idx+12:idx+16], "little"))
            idx += 16
        h = (_rotl32(v1, 1) + _rotl32(v2, 7) +
             _rotl32(v3, 12) + _rotl32(v4, 18)) & MASK32
    else:
        h = (seed + PRIME5) & MASK32

    h = (h + length) & MASK32
    while idx + 4 <= length:
        k = int.from_bytes(data[idx:idx+4], "little")
        h = (h + k * PRIME3) & MASK32
        h = (_rotl32(h, 17) * PRIME4) & MASK32
        idx += 4
    while idx < length:
        h = (h + data[idx] * PRIME5) & MASK32
        h = (_rotl32(h, 11) * PRIME1) & MASK32
        idx += 1

    h ^= h >> 15
    h = (h * PRIME2) & MASK32
    h ^= h >> 13
    h = (h * PRIME3) & MASK32
    h ^= h >> 16
    return h
