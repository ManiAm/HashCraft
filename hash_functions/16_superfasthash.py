"""SuperFastHash — Paul Hsieh (2004).

Optimized for speed on x86 hardware.  Processes input in 4-byte chunks
using 16-bit half-word operations.  One of the first hashes specifically
designed for hash table performance rather than error detection.

Weakness: higher collision rates than MurmurHash on certain patterns,
which is why MurmurHash largely replaced it.

Reference: http://www.azillionmonkeys.com/qed/hash.html
"""

MASK32 = 0xFFFF_FFFF
MASK16 = 0xFFFF


def super_fast_hash(data: bytes, seed: int = 0) -> int:
    """SuperFastHash (Paul Hsieh) — 32-bit."""
    length = len(data)
    if length == 0:
        return 0

    h = (seed + length) & MASK32
    remaining = length & 3
    n_blocks = length >> 2
    idx = 0

    for _ in range(n_blocks):
        lo = int.from_bytes(data[idx:idx+2], "little") & MASK16
        hi = int.from_bytes(data[idx+2:idx+4], "little") & MASK16
        h = (h + lo) & MASK32
        tmp = ((hi << 11) ^ h) & MASK32
        h = ((h << 16) ^ tmp) & MASK32
        h = (h + (h >> 11)) & MASK32
        idx += 4

    if remaining == 3:
        lo = int.from_bytes(data[idx:idx+2], "little") & MASK16
        h = (h + lo) & MASK32
        h ^= ((data[idx + 2] << 16) ^ (h << 16)) & MASK32
        h = (h + (h >> 11)) & MASK32
    elif remaining == 2:
        lo = int.from_bytes(data[idx:idx+2], "little") & MASK16
        h = (h + lo) & MASK32
        h ^= (h << 11) & MASK32
        h = (h + (h >> 17)) & MASK32
    elif remaining == 1:
        h = (h + data[idx]) & MASK32
        h ^= (h << 10) & MASK32
        h = (h + (h >> 1)) & MASK32

    h ^= (h << 3) & MASK32
    h = (h + (h >> 5)) & MASK32
    h ^= (h << 4) & MASK32
    h = (h + (h >> 17)) & MASK32
    h ^= (h << 25) & MASK32
    h = (h + (h >> 6)) & MASK32
    return h
