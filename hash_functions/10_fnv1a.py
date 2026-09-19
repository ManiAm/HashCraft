"""FNV-1a — Fowler–Noll–Vo hash, improved variant (1991).

Algorithm:  h = (h ^ byte) * prime   (XOR first, then multiply)

The only difference from FNV-1 is the order: XOR before multiply.  This
gives the multiplication a chance to cascade changes across more bits,
resulting in better avalanche properties.  FNV-1a is the recommended
variant for new code.

Reference: http://www.isthe.com/chongo/tech/comp/fnv/
"""

FNV1_32_OFFSET = 0x811C_9DC5
FNV1_32_PRIME  = 0x0100_0193
MASK32 = 0xFFFF_FFFF


def fnv1a_32(data: bytes, seed: int = FNV1_32_OFFSET) -> int:
    """FNV-1a hash — 32-bit.  XOR first, then multiply."""
    h = seed & MASK32
    for b in data:
        h = ((h ^ b) * FNV1_32_PRIME) & MASK32
    return h
