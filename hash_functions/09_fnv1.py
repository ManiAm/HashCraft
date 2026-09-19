"""FNV-1 — Fowler–Noll–Vo hash, original variant (1991).

Algorithm:  h = (h * prime) ^ byte   (multiply first, then XOR)

Extremely simple — one multiply and one XOR per byte.  Good distribution
for hash tables and short keys.  Compare with FNV-1a (10_fnv1a.py) which
swaps the order of operations for better avalanche.

Reference: http://www.isthe.com/chongo/tech/comp/fnv/
"""

FNV1_32_OFFSET = 0x811C_9DC5
FNV1_32_PRIME  = 0x0100_0193
MASK32 = 0xFFFF_FFFF


def fnv1_32(data: bytes, seed: int = FNV1_32_OFFSET) -> int:
    """FNV-1 hash — 32-bit.  Multiply first, then XOR."""
    h = seed & MASK32
    for b in data:
        h = ((h * FNV1_32_PRIME) ^ b) & MASK32
    return h
