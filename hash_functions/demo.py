#!/usr/bin/env python3
"""Demo — hash the same input with every registered function.

Each hash function takes bytes in and returns an integer out.
No hash tables, no collision resolution — just the raw hash.

Run:
    python3 -m hash_functions.demo
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hash_functions import REGISTRY


def main():
    test_input = b"Hello, hash world!"

    print(f"Input: {test_input!r}  ({len(test_input)} bytes)")
    print()
    print(f"  {'#':>3s}  {'Name':20s} {'Category':12s} {'Hash (hex)':>12s}")
    print(f"  {'─' * 52}")

    for i, (name, (fn, cat, bits)) in enumerate(REGISTRY.items(), 1):
        h = fn(test_input)
        print(f"  {i:3d}  {name:20s} {cat:12s} {h:>12x}")

    print()
    print(f"  {len(REGISTRY)} hash functions registered")
    print()


if __name__ == "__main__":
    main()
