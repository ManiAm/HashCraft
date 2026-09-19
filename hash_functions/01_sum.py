"""Sum hash — add all bytes together.

The simplest thing you might try: just add up every byte.  It looks at
all the input (unlike first-byte or length), but anagrams always collide
("abc" == "bca") and the output clusters in a narrow range.
"""

MASK32 = 0xFFFF_FFFF


def sum_hash(data: bytes, seed: int = 0) -> int:
    """Sum of all bytes mod 2^32."""
    h = seed & MASK32
    for b in data:
        h = (h + b) & MASK32
    return h
