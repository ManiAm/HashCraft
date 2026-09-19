"""MurmurHash3 — Austin Appleby (2011).

The modern standard for non-cryptographic hashing.  Excellent distribution
and avalanche.  Used by Cassandra, Redis Cluster, Elasticsearch, and many
Bloom filter libraries.

Pipeline: process 4-byte chunks → mix with constants c1/c2 → rotate →
XOR into running hash → finalize with fmix32.

Reference: https://github.com/aappleby/smhasher/blob/master/src/MurmurHash3.cpp
"""

MASK32 = 0xFFFF_FFFF
C1 = 0xCC9E_2D51
C2 = 0x1B87_3593


def _rotl32(x: int, r: int) -> int:
    return ((x << r) | (x >> (32 - r))) & MASK32


def _fmix32(h: int) -> int:
    h ^= h >> 16
    h = (h * 0x85EB_CA6B) & MASK32
    h ^= h >> 13
    h = (h * 0xC2B2_AE35) & MASK32
    h ^= h >> 16
    return h


def murmur3_32(data: bytes, seed: int = 0) -> int:
    """MurmurHash3 — 32-bit.  Matches the reference C implementation."""
    h = seed & MASK32
    length = len(data)
    nblocks = length // 4

    for i in range(nblocks):
        k = int.from_bytes(data[i*4:(i+1)*4], "little", signed=False)
        k = (k * C1) & MASK32
        k = _rotl32(k, 15)
        k = (k * C2) & MASK32
        h ^= k
        h = _rotl32(h, 13)
        h = (h * 5 + 0xE654_6B64) & MASK32

    tail_start = nblocks * 4
    k1 = 0
    tail_len = length & 3
    if tail_len >= 3:
        k1 ^= data[tail_start + 2] << 16
    if tail_len >= 2:
        k1 ^= data[tail_start + 1] << 8
    if tail_len >= 1:
        k1 ^= data[tail_start]
        k1 = (k1 * C1) & MASK32
        k1 = _rotl32(k1, 15)
        k1 = (k1 * C2) & MASK32
        h ^= k1

    h ^= length
    h = _fmix32(h)
    return h
