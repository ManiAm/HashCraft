"""SHA-256 — NIST (2001), part of the SHA-2 family.  Via hashlib.

The gold standard for integrity verification.  256-bit digest.
Still considered secure.  Much slower than generic hashes, but produces
near-perfect distribution and avalanche — the benchmark against which
all other hash functions are measured.
"""

import hashlib

MASK32 = 0xFFFF_FFFF


def sha256(data: bytes, seed: int = 0) -> int:
    """SHA-256 — truncated to 32 bits for comparison."""
    h = hashlib.sha256()
    if seed:
        h.update(seed.to_bytes(4, "little", signed=False))
    h.update(data)
    return int.from_bytes(h.digest()[:4], "big") & MASK32
