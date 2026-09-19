"""Simple hash — the guide's hash function (docs/01_hash_functions.md).

Algorithm:  h = (h * 31 + byte) % 2^32

This is the same multiply-and-add pattern used by Java's
String.hashCode().  The constant 31 is a small prime that the compiler
can optimize to a shift-and-subtract (31 * h == (h << 5) - h).

It is a reasonable first real hash — it looks at every byte and has
some bit mixing from the multiply — but the single multiply provides
weak avalanche, and patterned inputs (sequential integers, similar
strings) will cluster.
"""

MASK32 = 0xFFFF_FFFF


def simple_hash(data: bytes, seed: int = 0) -> int:
    """h = h * 31 + byte — the guide's simple_hash."""
    h = seed & MASK32
    for b in data:
        h = (h * 31 + b) & MASK32
    return h
