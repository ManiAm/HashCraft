"""Lose-lose hash — from K&R "The C Programming Language" (1978).

The simplest hash function ever published in a textbook.  It is identical
to sum_hash (h += byte) but is historically significant as the first hash
function many C programmers ever saw.  Distribution is poor.
"""

MASK32 = 0xFFFF_FFFF


def lose_lose(data: bytes, seed: int = 0) -> int:
    """K&R lose-lose:  h += byte  (identical to sum, kept for history)."""
    h = seed & MASK32
    for b in data:
        h = (h + b) & MASK32
    return h
