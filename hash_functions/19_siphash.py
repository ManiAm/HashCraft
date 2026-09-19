"""SipHash-2-4 — Aumasson & Bernstein (2012).

A keyed hash function designed to defend hash tables against hash-flooding
DoS attacks (HashDoS).  Used as the default string hash in Python (3.4+),
Rust, and Ruby (2.4+).

Not a general-purpose crypto hash — it is a PRF (pseudorandom function)
requiring a 128-bit secret key.  An attacker who does not know the key
cannot craft inputs that all collide.

Reference: https://www.aumasson.jp/siphash/siphash.pdf
"""

MASK64 = 0xFFFF_FFFF_FFFF_FFFF
MASK32 = 0xFFFF_FFFF


def _rotl64(x: int, r: int) -> int:
    return ((x << r) | (x >> (64 - r))) & MASK64


def _sipround(v0, v1, v2, v3):
    v0 = (v0 + v1) & MASK64; v1 = _rotl64(v1, 13); v1 ^= v0; v0 = _rotl64(v0, 32)
    v2 = (v2 + v3) & MASK64; v3 = _rotl64(v3, 16); v3 ^= v2
    v0 = (v0 + v3) & MASK64; v3 = _rotl64(v3, 21); v3 ^= v0
    v2 = (v2 + v1) & MASK64; v1 = _rotl64(v1, 17); v1 ^= v2; v2 = _rotl64(v2, 32)
    return v0, v1, v2, v3


def siphash_2_4(data: bytes, seed: int = 0) -> int:
    """SipHash-2-4 — 64-bit internally, truncated to 32 bits."""
    k0 = k1 = seed & MASK64
    v0 = k0 ^ 0x736F_6D65_7073_6575
    v1 = k1 ^ 0x646F_7261_6E64_6F6D
    v2 = k0 ^ 0x6C79_6765_6E65_7261
    v3 = k1 ^ 0x7465_6462_7974_6573

    length = len(data)
    nblocks = length // 8
    for i in range(nblocks):
        m = int.from_bytes(data[i*8:(i+1)*8], "little")
        v3 ^= m
        for _ in range(2):
            v0, v1, v2, v3 = _sipround(v0, v1, v2, v3)
        v0 ^= m

    tail_start = nblocks * 8
    m = (length & 0xFF) << 56
    for i in range(length - tail_start):
        m |= data[tail_start + i] << (8 * i)
    v3 ^= m
    for _ in range(2):
        v0, v1, v2, v3 = _sipround(v0, v1, v2, v3)
    v0 ^= m

    v2 ^= 0xFF
    for _ in range(4):
        v0, v1, v2, v3 = _sipround(v0, v1, v2, v3)

    return (v0 ^ v1 ^ v2 ^ v3) & MASK32
