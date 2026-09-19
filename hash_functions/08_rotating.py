"""Rotating hash — shift, rotate, and XOR.

A simple approach where bits are rotated (not just shifted) to preserve
information.  The 4-bit rotation ensures bits from early bytes are not
pushed off the top of the register and lost.
"""

MASK32 = 0xFFFF_FFFF


def rotating_hash(data: bytes, seed: int = 0) -> int:
    """Rotating hash:  h = rotate_left(h, 4) ^ byte."""
    h = seed & MASK32
    for b in data:
        h = ((h << 4) ^ (h >> 28) ^ b) & MASK32
    return h
