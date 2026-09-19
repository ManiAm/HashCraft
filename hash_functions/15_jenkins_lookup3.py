"""Jenkins lookup3 — Bob Jenkins (2006).

Processes input in 12-byte blocks with three 32-bit accumulators (a, b, c)
that are mixed together.  Much faster than one-at-a-time on long inputs
because it processes 12 bytes per mixing round instead of 1.

Reference: http://www.burtleburtle.net/bob/hash/doobs.html
"""

MASK32 = 0xFFFF_FFFF


def jenkins_lookup3(data: bytes, seed: int = 0) -> int:
    """Jenkins lookup3 / hashlittle — 32-bit."""
    length = len(data)
    a = b = (0xDEAD_BEEF + length + seed) & MASK32
    c = seed & MASK32

    i = 0
    while i + 12 <= length:
        a = (a + int.from_bytes(data[i:i+4], "little")) & MASK32
        b = (b + int.from_bytes(data[i+4:i+8], "little")) & MASK32
        c = (c + int.from_bytes(data[i+8:i+12], "little")) & MASK32

        a = (a - c) & MASK32; a ^= ((c << 4) | (c >> 28)) & MASK32; c = (c + b) & MASK32
        b = (b - a) & MASK32; b ^= ((a << 6) | (a >> 26)) & MASK32; a = (a + c) & MASK32
        c = (c - b) & MASK32; c ^= ((b << 8) | (b >> 24)) & MASK32; b = (b + a) & MASK32
        a = (a - c) & MASK32; a ^= ((c << 16) | (c >> 16)) & MASK32; c = (c + b) & MASK32
        b = (b - a) & MASK32; b ^= ((a << 19) | (a >> 13)) & MASK32; a = (a + c) & MASK32
        c = (c - b) & MASK32; c ^= ((b << 4) | (b >> 28)) & MASK32; b = (b + a) & MASK32
        i += 12

    tail = data[i:]
    pad = tail + b"\x00" * (12 - len(tail))
    if len(tail) > 0:
        a = (a + int.from_bytes(pad[0:4], "little")) & MASK32
    if len(tail) > 4:
        b = (b + int.from_bytes(pad[4:8], "little")) & MASK32
    if len(tail) > 8:
        c = (c + int.from_bytes(pad[8:12], "little")) & MASK32

    if len(tail) > 0:
        c ^= b; c = (c - ((b << 14) | (b >> 18))) & MASK32
        a ^= c; a = (a - ((c << 11) | (c >> 21))) & MASK32
        b ^= a; b = (b - ((a << 25) | (a >> 7))) & MASK32
        c ^= b; c = (c - ((b << 16) | (b >> 16))) & MASK32
        a ^= c; a = (a - ((c << 4) | (c >> 28))) & MASK32
        b ^= a; b = (b - ((a << 14) | (a >> 18))) & MASK32
        c ^= b; c = (c - ((b << 24) | (b >> 8))) & MASK32

    return c
