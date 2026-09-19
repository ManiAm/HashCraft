"""Pearson hashing — Peter K. Pearson (1990).

A byte-oriented hash that uses a 256-entry permutation table to map each
input byte to a pseudo-random output.  The original algorithm produces
only an 8-bit hash (256 possible values), making collisions very frequent
— but that is the point: it teaches why hash width matters.

The 32-bit variant runs 4 independent passes with different starting
values and concatenates the results.

Reference: "Fast Hashing of Variable-Length Text Strings",
           Communications of the ACM, June 1990.
"""

MASK32 = 0xFFFF_FFFF

# PERMUTATION must be a true permutation of 0..255.  A table with
# duplicates or gaps silently destroys uniformity in the low output byte,
# which is exactly the byte a `hash % bucket_count` table depends on.
PERMUTATION = [
     98,   6,  85, 150,  36,  23, 112, 164, 135, 207, 169,   5,  26,  64,
    165, 219,  61,  20,  68,  89, 130,  63,  52, 102,  24, 229, 132, 245,
     80, 216, 195, 115,  90, 168, 156, 203, 177, 120,   2, 190, 188,   7,
    100, 185, 174, 243, 162,  10, 237,  18, 253, 225,   8, 208, 172, 244,
    255, 126, 101,  79, 145, 235, 228, 121, 123, 251,  67, 250, 161,   0,
    107,  97, 241, 111, 181,  82, 249,  33,  69,  55,  59, 153,  29,   9,
    213, 167,  84,  93,  30,  46,  94,  75, 151, 114,  73, 222, 197,  96,
    210,  45,  16, 227, 248, 202,  51, 152, 252, 125,  81, 206, 215, 186,
     39, 158, 178, 187, 131, 136,   1,  49,  50,  17, 141,  91,  47, 129,
     60,  99, 154,  35,  86, 171, 105,  34,  38, 200, 147,  58,  77, 118,
    173, 246,  76, 254, 133, 232, 196, 144, 198, 124,  53,   4, 108,  74,
    223, 234, 134, 230, 157, 139, 189, 205, 199, 128, 176,  19, 211, 236,
    127, 192, 231,  70, 233,  88, 146,  44, 183, 201,  22,  83,  13, 214,
    116, 109, 159,  32,  95, 226, 140, 220,  57,  12, 221,  31, 209, 182,
    143,  92, 149, 184, 148,  62, 113,  65,  37,  27, 106, 166,   3,  14,
    204,  72,  21,  41,  56,  66,  28, 193,  40, 217,  25,  54, 179, 117,
    238,  87, 240, 155, 180, 170, 242, 212, 191, 163,  78, 218, 137, 194,
    175, 110,  43, 119, 224,  71, 122, 142,  42, 160, 104,  48, 247, 103,
     15,  11, 138, 239,
]

assert sorted(PERMUTATION) == list(range(256)), \
    "PERMUTATION is not a permutation of 0..255"


def pearson(data: bytes, seed: int = 0) -> int:
    """Pearson hash — 32-bit (4 independent 8-bit passes combined)."""
    result = 0
    for i in range(4):
        h = (seed + i) & 0xFF
        for b in data:
            h = PERMUTATION[(h ^ b) % 256]
        result = (result << 8) | h
    return result & MASK32
