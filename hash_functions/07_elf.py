"""ELF hash — used in Unix ELF (Executable and Linkable Format) files.

The high bits are mixed back in after each byte to prevent them from
being lost.  Historically used for symbol table lookups in linkers and
loaders.
"""

MASK32 = 0xFFFF_FFFF


def elf_hash(data: bytes, seed: int = 0) -> int:
    """ELF hash — shift left 4, mix high nibble back in."""
    h = seed & MASK32
    for b in data:
        h = ((h << 4) + b) & MASK32
        high = h & 0xF000_0000
        if high:
            h ^= high >> 24
        h &= ~high & MASK32
    return h
