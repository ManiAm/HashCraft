"""XOR hash — fold all bytes together with exclusive-or.

XOR is commutative and self-canceling, so:
  - anagrams collide ("abc" == "cba")
  - repeated bytes cancel out ("aa" == "")
  - only 256 possible outputs regardless of input length

This demonstrates why a hash must spread bits across the full output
width, not just fold them into a single byte.
"""

MASK32 = 0xFFFF_FFFF


def xor_hash(data: bytes, seed: int = 0) -> int:
    """XOR all bytes together (0–255), zero-extended to 32 bits."""
    h = seed & 0xFF
    for b in data:
        h ^= b
    return h & MASK32
