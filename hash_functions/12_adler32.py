"""Adler-32 — Mark Adler (1995), used in zlib.

A checksum designed for **error detection**, not hash tables.  It maintains
two 16-bit running sums (A and B) and combines them into a 32-bit output.

Faster than CRC32 but catches fewer error patterns.  Including it in
benchmarks shows why "fast checksum" ≠ "good hash table distribution".
"""

MASK32 = 0xFFFF_FFFF


def adler32(data: bytes, seed: int = 1) -> int:
    """Adler-32:  A = 1 + sum(bytes) mod 65521,  B = sum(A) mod 65521."""
    MOD = 65521
    a = seed & 0xFFFF
    b = (seed >> 16) & 0xFFFF
    for byte in data:
        a = (a + byte) % MOD
        b = (b + a) % MOD
    return ((b << 16) | a) & MASK32
