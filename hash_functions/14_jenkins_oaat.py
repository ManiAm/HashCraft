"""Jenkins one-at-a-time hash — Bob Jenkins (1997).

Three operations per byte (add, shift-add, shift-XOR) plus a four-step
finalization.  Despite its simplicity it has excellent avalanche — each
input bit affects every output bit after just a few rounds.

The finalization is critical: without it the last few bytes would not
influence all output bits.

Reference: http://www.burtleburtle.net/bob/hash/doobs.html
"""

MASK32 = 0xFFFF_FFFF


def jenkins_oaat(data: bytes, seed: int = 0) -> int:
    """Jenkins one-at-a-time — 32-bit."""
    h = seed & MASK32
    for b in data:
        h = (h + b) & MASK32
        h = (h + (h << 10)) & MASK32
        h ^= (h >> 6)
    h = (h + (h << 3)) & MASK32
    h ^= (h >> 11)
    h = (h + (h << 15)) & MASK32
    return h
