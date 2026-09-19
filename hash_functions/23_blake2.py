"""BLAKE2b — Aumasson, Neves, Wilcox-O'Hearn, Winnerlein (2012).  Via hashlib.

Faster than SHA-256 on most CPUs while providing equivalent security.
Variable-length digest (up to 512 bits).  The fastest standardized
cryptographic hash — useful as a "best of both worlds" benchmark.
"""

import hashlib

MASK32 = 0xFFFF_FFFF


def blake2b(data: bytes, seed: int = 0) -> int:
    """BLAKE2b — truncated to 32 bits for comparison."""
    h = hashlib.blake2b()
    if seed:
        h.update(seed.to_bytes(4, "little", signed=False))
    h.update(data)
    return int.from_bytes(h.digest()[:4], "big") & MASK32
