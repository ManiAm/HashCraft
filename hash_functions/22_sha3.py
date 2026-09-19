"""SHA3-256 — NIST (2015), based on the Keccak sponge construction.  Via hashlib.

Completely different internal design from SHA-2 (sponge vs. Merkle-Damgård),
providing algorithm diversity.  If SHA-2 is ever broken, SHA-3 is the
fallback.  256-bit digest.
"""

import hashlib

MASK32 = 0xFFFF_FFFF


def sha3_256(data: bytes, seed: int = 0) -> int:
    """SHA3-256 — truncated to 32 bits for comparison."""
    h = hashlib.sha3_256()
    if seed:
        h.update(seed.to_bytes(4, "little", signed=False))
    h.update(data)
    return int.from_bytes(h.digest()[:4], "big") & MASK32
