"""Hash Functions Library — one algorithm per file, ordered naive → best.

Every function follows the same interface:

    def hash_func(data: bytes, seed: int = 0) -> int

Files are numbered 01–23 from worst to most sophisticated.

Usage
-----
    from hash_functions import REGISTRY, get_hash

    fnv = get_hash("fnv1a")
    print(fnv(b"hello world"))

    for name, fn in get_all():
        print(f"{name:20s} -> {fn(b'test'):08x}")
"""

import importlib

_m01 = importlib.import_module("hash_functions.01_sum")
_m02 = importlib.import_module("hash_functions.02_xor")
_m03 = importlib.import_module("hash_functions.03_lose_lose")
_m04 = importlib.import_module("hash_functions.04_simple")
_m05 = importlib.import_module("hash_functions.05_djb2")
_m06 = importlib.import_module("hash_functions.06_sdbm")
_m07 = importlib.import_module("hash_functions.07_elf")
_m08 = importlib.import_module("hash_functions.08_rotating")
_m09 = importlib.import_module("hash_functions.09_fnv1")
_m10 = importlib.import_module("hash_functions.10_fnv1a")
_m11 = importlib.import_module("hash_functions.11_pearson")
_m12 = importlib.import_module("hash_functions.12_adler32")
_m13 = importlib.import_module("hash_functions.13_crc32")
_m14 = importlib.import_module("hash_functions.14_jenkins_oaat")
_m15 = importlib.import_module("hash_functions.15_jenkins_lookup3")
_m16 = importlib.import_module("hash_functions.16_superfasthash")
_m17 = importlib.import_module("hash_functions.17_murmur3")
_m18 = importlib.import_module("hash_functions.18_xxhash")
_m19 = importlib.import_module("hash_functions.19_siphash")
_m20 = importlib.import_module("hash_functions.20_md5")
_m21 = importlib.import_module("hash_functions.21_sha256")
_m22 = importlib.import_module("hash_functions.22_sha3")
_m23 = importlib.import_module("hash_functions.23_blake2")

sum_hash         = _m01.sum_hash
xor_hash         = _m02.xor_hash
lose_lose        = _m03.lose_lose
simple_hash      = _m04.simple_hash
djb2             = _m05.djb2
sdbm             = _m06.sdbm
elf_hash         = _m07.elf_hash
rotating_hash    = _m08.rotating_hash
fnv1_32          = _m09.fnv1_32
fnv1a_32         = _m10.fnv1a_32
pearson          = _m11.pearson
adler32          = _m12.adler32
crc32            = _m13.crc32
jenkins_oaat     = _m14.jenkins_oaat
jenkins_lookup3  = _m15.jenkins_lookup3
super_fast_hash  = _m16.super_fast_hash
murmur3_32       = _m17.murmur3_32
xxhash32         = _m18.xxhash32
siphash_2_4      = _m19.siphash_2_4
md5              = _m20.md5
sha256           = _m21.sha256
sha3_256         = _m22.sha3_256
blake2b          = _m23.blake2b

# ---------------------------------------------------------------------------
# Registry — one entry per file, ordered 01 → 23  (naive → best)
# ---------------------------------------------------------------------------

REGISTRY: dict[str, tuple[callable, str, int]] = {
    # Naive (01–03)
    "sum":              (sum_hash,         "naive",      32),
    "xor":              (xor_hash,         "naive",      32),
    "lose_lose":        (lose_lose,        "naive",      32),

    # First real hash (04)
    "simple":           (simple_hash,      "naive",      32),

    # Classic (05–08)
    "djb2":             (djb2,             "classic",    32),
    "sdbm":             (sdbm,             "classic",    32),
    "elf":              (elf_hash,          "classic",    32),
    "rotating":         (rotating_hash,    "classic",    32),

    # FNV (09–10)
    "fnv1":             (fnv1_32,          "fnv",        32),
    "fnv1a":            (fnv1a_32,         "fnv",        32),

    # Pearson (11)
    "pearson":          (pearson,          "pearson",    32),

    # Checksums (12–13)
    "adler32":          (adler32,          "checksum",   32),
    "crc32":            (crc32,            "checksum",   32),

    # Jenkins (14–15)
    "jenkins_oaat":     (jenkins_oaat,     "jenkins",    32),
    "jenkins_lookup3":  (jenkins_lookup3,  "jenkins",    32),

    # Modern (16–18)
    "super_fast_hash":  (super_fast_hash,  "modern",     32),
    "murmur3":          (murmur3_32,       "modern",     32),
    "xxhash32":         (xxhash32,         "modern",     32),

    # Keyed (19)
    "siphash":          (siphash_2_4,      "keyed",      32),

    # Cryptographic (20–23)
    "md5":              (md5,              "crypto",     32),
    "sha256":           (sha256,           "crypto",     32),
    "sha3_256":         (sha3_256,         "crypto",     32),
    "blake2b":          (blake2b,          "crypto",     32),
}


def get_hash(name: str) -> callable:
    """Return a hash function by name.  Raises KeyError if not found."""
    fn, _, _ = REGISTRY[name]
    return fn


def get_category(category: str) -> list[tuple[str, callable]]:
    """Return all (name, function) pairs in a category."""
    return [(n, fn) for n, (fn, cat, _) in REGISTRY.items() if cat == category]


def get_all() -> list[tuple[str, callable]]:
    """Return all (name, function) pairs."""
    return [(n, fn) for n, (fn, _, _) in REGISTRY.items()]


def list_names() -> list[str]:
    """Return all registered hash function names."""
    return list(REGISTRY.keys())


def describe() -> str:
    """Return a formatted table of all registered hash functions."""
    lines = [f"{'#':>3s}  {'Name':20s} {'Category':12s}", "─" * 40]
    for i, (name, (_, cat, _)) in enumerate(REGISTRY.items(), 1):
        lines.append(f"{i:3d}  {name:20s} {cat:12s}")
    return "\n".join(lines)
