"""DJB2 — Dan Bernstein's hash (1991).

Algorithm:  h = h * 33 + byte

One of the most widely cited string hash functions.  The constant 33
works surprisingly well in practice, though the reason is partly
empirical.  Used in many older hash table implementations and still
found in glibc's ELF symbol hashing.
"""

MASK32 = 0xFFFF_FFFF


def djb2(data: bytes, seed: int = 5381) -> int:
    """DJB2:  h = h * 33 + byte."""
    h = seed & MASK32
    for b in data:
        h = ((h * 33) + b) & MASK32
    return h
