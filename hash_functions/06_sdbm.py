"""SDBM hash — from the SDBM database library.

Algorithm:  h = byte + (h << 6) + (h << 16) - h

This is equivalent to  h = byte + h * 65599.  It was chosen empirically
for the SDBM database and has good distribution for short ASCII strings.
The large multiplier spreads bits better than DJB2's 33.
"""

MASK32 = 0xFFFF_FFFF


def sdbm(data: bytes, seed: int = 0) -> int:
    """SDBM:  h = byte + h * 65599."""
    h = seed & MASK32
    for b in data:
        h = (b + (h << 6) + (h << 16) - h) & MASK32
    return h
