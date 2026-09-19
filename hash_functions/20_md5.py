"""MD5 — Ron Rivest (1991).  Cryptographic hash, via hashlib.

128-bit digest.  Broken for collision resistance since 2004 (Wang et al.),
but still widely used for non-security checksums.  Included here to
show the speed-vs-security tradeoff — MD5 is much slower than generic
hashes but faster than modern crypto hashes like SHA-256.
"""

import hashlib

MASK32 = 0xFFFF_FFFF


def md5(data: bytes, seed: int = 0) -> int:
    """MD5 — truncated to 32 bits for comparison."""
    h = hashlib.md5()
    if seed:
        h.update(seed.to_bytes(4, "little", signed=False))
    h.update(data)
    return int.from_bytes(h.digest()[:4], "big") & MASK32
