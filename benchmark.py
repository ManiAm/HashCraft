#!/usr/bin/env python3
"""Benchmark runner — evaluate all 23 hash functions on five metrics.

Measures throughput, latency, chi-squared distribution, avalanche effect,
and collision rate.  Prints a scorecard table and optionally generates
matplotlib plots.

Run:
    python3 benchmark.py              # full benchmark
    python3 benchmark.py --quick      # reduced sample sizes (~14 s)
    python3 benchmark.py --no-plots   # skip plot generation
"""

import argparse
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hash_functions import REGISTRY


# ── Control ────────────────────────────────────────────────────────────────
#
# `identity` does no mixing whatsoever — it reinterprets the first four
# bytes of the key as an integer.  It is included in every table and plot
# as a calibration baseline.  Any metric on which `identity` scores as well
# as murmur3 is a metric with no discriminating power, and the random-key
# distribution test is exactly such a metric: random input is already
# uniform, so there is nothing left for a hash function to do.

def identity(data: bytes, seed: int = 0) -> int:
    """Control: no hashing at all — the first 4 bytes, little-endian."""
    return int.from_bytes(data[:4].ljust(4, b"\0"), "little")


CONTROLS = {
    "identity (control)": (identity, "control", 32),
}


def bench_targets():
    """Registry entries preceded by the control baseline."""
    return {**CONTROLS, **REGISTRY}


def chi_sq_z(chi_sq, num_buckets):
    """Two-sided deviation of a χ² statistic from its expected value.

    χ² has mean df and standard deviation sqrt(2·df) for df = buckets − 1.
    Returned as |z|, so 0 is ideal and anything past ~3 is suspect in
    *either* direction — χ² far below df means the hash is behaving like a
    counter rather than a random function, which is its own kind of broken.
    """
    df = num_buckets - 1
    return abs(chi_sq - df) / math.sqrt(2 * df)


# ── Configuration ──────────────────────────────────────────────────────────

FULL_CONFIG = {
    "throughput_bytes":  1 * 1024 * 1024,  # 1 MB buffer
    "throughput_iters":  3,
    "latency_key_len":   16,               # bytes per key
    "latency_iters":     10_000,
    "chi_sq_n":          50_000,
    "chi_sq_buckets":    100,
    "chi_sq_buckets_p2": 128,              # power of two — exposes weak low bits
    "avalanche_samples": 5_000,
    "collision_n":       10_000,
    "collision_buckets": 2 ** 20,          # ~1 M buckets
}

QUICK_CONFIG = {
    "throughput_bytes":  256 * 1024,       # 256 KB
    "throughput_iters":  2,
    "latency_key_len":   16,
    "latency_iters":     2_000,
    "chi_sq_n":          10_000,
    "chi_sq_buckets":    100,
    "chi_sq_buckets_p2": 128,
    "avalanche_samples": 1_000,
    "collision_n":       5_000,
    "collision_buckets": 2 ** 18,
}


# ── Workload generators ───────────────────────────────────────────────────

def gen_random_keys(n, length=16):
    """Uniformly random byte strings."""
    return [os.urandom(length) for _ in range(n)]


def gen_sequential(n):
    """Integers 0..n-1 encoded as 4-byte little-endian."""
    return [i.to_bytes(4, "little") for i in range(n)]


def gen_similar_strings(n):
    """Strings like 'key_0001', 'key_0002', … with a shared prefix."""
    width = len(str(n))
    return [f"key_{i:0{width}d}".encode() for i in range(n)]


def gen_repeated_prefixes(n):
    """Keys sharing a long common prefix, differing only at the end."""
    prefix = b"shared_prefix_" + b"x" * 40
    return [prefix + i.to_bytes(4, "little") for i in range(n)]


def gen_short_keys(n):
    """Very short keys: b'a', b'b', …, b'z', b'aa', b'ab', …"""
    import itertools
    import string
    keys = []
    for length in range(1, 5):
        for combo in itertools.product(string.ascii_lowercase, repeat=length):
            keys.append("".join(combo).encode())
            if len(keys) >= n:
                return keys
    return keys[:n]


WORKLOADS = {
    "random":     gen_random_keys,
    "sequential": gen_sequential,
    "similar":    gen_similar_strings,
    "prefixes":   gen_repeated_prefixes,
    "short":      gen_short_keys,
}


# ── Metric implementations ────────────────────────────────────────────────

def measure_throughput(fn, buf_size, iters):
    """MB/s on a large buffer."""
    buf = os.urandom(buf_size)
    fn(buf)                                    # warm-up
    start = time.perf_counter()
    for _ in range(iters):
        fn(buf)
    elapsed = time.perf_counter() - start
    total_mb = buf_size * iters / (1024 * 1024)
    return total_mb / elapsed if elapsed > 0 else float("inf")


def measure_latency(fn, key_len, iters):
    """Average nanoseconds per call on short keys."""
    pool = [os.urandom(key_len) for _ in range(min(iters, 1000))]
    pool_len = len(pool)
    for k in pool[:10]:
        fn(k)                                  # warm-up
    start = time.perf_counter_ns()
    for i in range(iters):
        fn(pool[i % pool_len])
    elapsed_ns = time.perf_counter_ns() - start
    return elapsed_ns / iters


def measure_chi_squared(fn, keys, num_buckets):
    """Return (chi_sq_statistic, bucket_counts)."""
    counts = [0] * num_buckets
    for k in keys:
        counts[fn(k) % num_buckets] += 1
    expected = len(keys) / num_buckets
    chi_sq = sum((obs - expected) ** 2 / expected for obs in counts)
    return chi_sq, counts


def measure_avalanche(fn, num_samples):
    """Return (mean_percent, per_sample_percents)."""
    pcts = []
    for _ in range(num_samples):
        data = bytearray(os.urandom(16))
        h1 = fn(bytes(data))
        bit_pos = random.randint(0, len(data) * 8 - 1)
        data[bit_pos // 8] ^= 1 << (bit_pos % 8)
        h2 = fn(bytes(data))
        flipped = bin(h1 ^ h2).count("1")
        pcts.append(flipped / 32 * 100)
    return sum(pcts) / len(pcts), pcts


def measure_collisions(fn, keys, num_buckets):
    """Return (total_collisions, collision_curve).

    collision_curve is a list of (n_inserted, cumulative_collisions) pairs
    sampled at ~100 evenly spaced checkpoints.
    """
    seen = set()
    collisions = 0
    curve = []
    step = max(1, len(keys) // 100)
    for i, k in enumerate(keys, 1):
        bucket = fn(k) % num_buckets
        if bucket in seen:
            collisions += 1
        else:
            seen.add(bucket)
        if i % step == 0 or i == len(keys):
            curve.append((i, collisions))
    return collisions, curve


# ── Scorecard formatting ──────────────────────────────────────────────────

def _fmt_tp(mbps):
    if mbps >= 1000:
        return f"{mbps / 1000:.1f} GB/s"
    if mbps >= 1:
        return f"{mbps:.1f} MB/s"
    return f"{mbps * 1024:.0f} KB/s"


def _fmt_lat(ns):
    if ns >= 1_000_000:
        return f"{ns / 1_000_000:.1f} ms"
    if ns >= 1000:
        return f"{ns / 1000:.1f} µs"
    return f"{ns:.0f} ns"


def print_scorecard(results, cfg):
    col_n = cfg["collision_n"]
    hdr = (f"  {'Hash Function':20s}  {'Category':10s}  {'Throughput':>12s}"
           f"  {'Latency':>10s}  {'χ²':>10s}  {'|z|':>6s}  {'Avalanche':>10s}"
           f"  {'Collis/' + str(col_n // 1000) + 'K':>10s}")
    print()
    print(hdr)
    print("  " + "─" * (len(hdr) - 2))
    for name, r in results.items():
        print(
            f"  {name:20s}  {r['category']:10s}"
            f"  {_fmt_tp(r['throughput_mbps']):>12s}"
            f"  {_fmt_lat(r['latency_ns']):>10s}"
            f"  {r['chi_squared']:>10.0f}"
            f"  {chi_sq_z(r['chi_squared'], cfg['chi_sq_buckets']):>6.1f}"
            f"  {r['avalanche_pct']:>9.1f}%"
            f"  {r['collisions']:>10,d}"
        )
    print()
    print(f"  χ² expected (uniform):  ~{cfg['chi_sq_buckets'] - 1}"
          f"    ({cfg['chi_sq_n']:,} keys → {cfg['chi_sq_buckets']} buckets)")
    print(f"  This column is on RANDOM keys, where the input is already "
          f"uniform and there is nothing for a")
    print(f"  hash to do — note that the `identity` control scores as well "
          f"as murmur3.  The per-workload")
    print(f"  tables below are what actually separates these functions.")
    print()


def print_workload_table(wl_results, cfg):
    """Print per-workload χ² and collision tables."""
    wl_names = list(WORKLOADS.keys())
    hdr = f"  {'Hash Function':20s}" + "".join(f"  {w:>12s}" for w in wl_names)

    for key, buckets in (("chi_sq",    cfg["chi_sq_buckets"]),
                         ("chi_sq_p2", cfg["chi_sq_buckets_p2"])):
        note = "" if buckets & (buckets - 1) else "   ← power of two, uses low bits only"
        print(f"  Per-Workload χ²  ({buckets} buckets, ideal ≈ {buckets - 1}){note}")
        print(hdr)
        print("  " + "─" * (len(hdr) - 2))
        for name, wl_data in wl_results.items():
            vals = "".join(f"  {wl_data[w][key]:>12.0f}" for w in wl_names)
            print(f"  {name:20s}{vals}")
        print()

    print(f"  Per-Workload χ² deviation |z|  (0 is ideal, >3 is broken either way)")
    print(hdr)
    print("  " + "─" * (len(hdr) - 2))
    for name, wl_data in wl_results.items():
        vals = "".join(f"  {wl_data[w]['z']:>12.1f}" for w in wl_names)
        print(f"  {name:20s}{vals}")
    print()

    print(f"  Per-Workload Collisions")
    print(hdr)
    print("  " + "─" * (len(hdr) - 2))
    for name, wl_data in wl_results.items():
        vals = "".join(f"  {wl_data[w]['collisions']:>12,d}" for w in wl_names)
        print(f"  {name:20s}{vals}")
    print()


# ── Plot generation ───────────────────────────────────────────────────────

CAT_COLORS = {
    "control":  "#2c3e50",
    "naive":    "#e74c3c",
    "classic":  "#e67e22",
    "fnv":      "#f1c40f",
    "pearson":  "#2ecc71",
    "checksum": "#1abc9c",
    "jenkins":  "#3498db",
    "modern":   "#2980b9",
    "keyed":    "#9b59b6",
    "crypto":   "#8e44ad",
}

REPRESENTATIVE_HASHES = [
    "identity (control)", "sum", "xor", "djb2", "fnv1a",
    "murmur3", "xxhash32", "sha256",
]


def generate_plots(results, cfg, output_dir, wl_results=None):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import LogNorm
    except ImportError:
        print("  matplotlib not installed — skipping plots.")
        print("  Install with: pip install matplotlib")
        return

    os.makedirs(output_dir, exist_ok=True)
    names = list(results.keys())
    reps = [n for n in REPRESENTATIVE_HASHES if n in results]

    def _color(name):
        return CAT_COLORS.get(results[name]["category"], "#95a5a6")

    # ── 1. Collision curve ────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 7))
    for name in names:
        xs, ys = zip(*results[name]["collision_curve"])
        ax.plot(xs, ys, label=name, color=_color(name), linewidth=1.2)
    ax.set_xlabel("Keys inserted")
    ax.set_ylabel("Cumulative collisions")
    ax.set_title("Collisions vs. Number of Inserted Keys")
    ax.legend(fontsize=7, ncol=3, loc="upper left")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(output_dir, "collision_curve.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  saved {path}")

    # ── 2. Avalanche histogram ────────────────────────────────────────
    #
    # Hashes with near-zero avalanche (identity, xor) spike to extreme
    # density at the left edge, crushing the Y-axis scale and making the
    # good hashes at ~50% invisible.  Cap Y at 1.0 so both ends are
    # readable — the clipped spikes still show as tall bars at the left.
    fig, ax = plt.subplots(figsize=(12, 7))
    for name in reps:
        ax.hist(results[name]["avalanche_samples"], bins=50,
                alpha=0.5, label=name, color=_color(name), density=True)
    ax.axvline(50, color="black", linestyle="--", linewidth=1, label="Ideal (50%)")
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("Bit-flip percentage")
    ax.set_ylabel("Density (capped at 1.0 — low-avalanche spikes are clipped)")
    ax.set_title(
        "Avalanche Effect Distribution\n"
        "Each curve: hash 1,000 random 16-byte inputs, flip one bit, "
        "measure % of output bits that change. Ideal = 50%.",
        fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(output_dir, "avalanche_histogram.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  saved {path}")

    # ── 3. Bucket distribution heatmap ────────────────────────────────
    #
    # A "noise floor" row drawn straight from random.randrange is appended
    # so the reader can see that the mottling in the good rows is Poisson
    # sampling noise, not structure.  Expected count is n/buckets with
    # standard deviation sqrt(n/buckets), so at 50,000 keys over 100
    # buckets a flawless hash still varies by ±4.5%.
    n_keys, n_buckets = cfg["chi_sq_n"], cfg["chi_sq_buckets"]
    expected = n_keys / n_buckets
    sigma = math.sqrt(expected)

    noise_row = [0] * n_buckets
    for _ in range(n_keys):
        noise_row[random.randrange(n_buckets)] += 1

    rows = names + ["— noise floor (pure RNG) —"]
    data_matrix = [results[n]["bucket_counts"] for n in names] + [noise_row]

    fig, ax = plt.subplots(figsize=(14, 8))
    im = ax.imshow(data_matrix, aspect="auto", cmap="YlOrRd",
                   interpolation="nearest")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=7)
    ax.get_yticklabels()[-1].set_style("italic")
    ax.set_xlabel("Bucket index")
    ax.set_title(
        f"Bucket Distribution on Random Keys — {n_keys:,} keys → "
        f"{n_buckets} buckets (brighter = more keys)\n"
        f"Expected {expected:.0f} per bucket, Poisson σ = {sigma:.0f}: a "
        f"flawless hash still mottles by ±{3 * sigma / expected:.0%}. "
        f"Compare every row against the noise floor at the bottom.",
        fontsize=10)
    fig.colorbar(im, ax=ax, label="Keys per bucket")
    fig.tight_layout()
    path = os.path.join(output_dir, "bucket_heatmap.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  saved {path}")

    # ── 4. Per-workload χ² heatmap ────────────────────────────────────
    #
    # Colour encodes |z| — how far χ² sits from its expected value in
    # either direction — not χ² itself.  Colouring by raw χ² would paint
    # the degenerate cases greenest: a hash that maps sequential keys
    # straight onto sequential buckets scores χ² ≈ 0, which is as wrong as
    # χ² ≈ 20,000 and means the hash is acting as a counter, not a
    # pseudo-random function.  The cell text stays the raw χ².
    if wl_results:
        wl_names = list(WORKLOADS.keys())
        hash_names = list(wl_results.keys())
        bucket_sets = (("chi_sq",    cfg["chi_sq_buckets"]),
                       ("chi_sq_p2", cfg["chi_sq_buckets_p2"]))

        columns = [(w, key, buckets)
                   for key, buckets in bucket_sets for w in wl_names]
        z_matrix = [[chi_sq_z(wl_results[h][w][key], buckets)
                     for w, key, buckets in columns] for h in hash_names]
        chi_matrix = [[wl_results[h][w][key] for w, key, _ in columns]
                      for h in hash_names]

        # |z| below 2 is consistent with a uniform distribution, so the
        # whole passing range saturates to one green rather than grading
        # noise against noise.
        flat = [v for row in z_matrix for v in row]
        norm = LogNorm(vmin=2.0, vmax=max(flat))

        fig, ax = plt.subplots(figsize=(14, 9))
        im = ax.imshow(z_matrix, aspect="auto", cmap="RdYlGn_r",
                       norm=norm, interpolation="nearest")
        ax.set_xticks(range(len(columns)))
        ax.set_xticklabels([f"{w}\n{b} buckets" for w, _, b in columns],
                           fontsize=8)
        ax.axvline(len(wl_names) - 0.5, color="black", linewidth=2)
        ax.set_yticks(range(len(hash_names)))
        ax.set_yticklabels(hash_names, fontsize=7)
        ax.set_title(
            "Per-Workload Distribution Quality\n"
            "Colour = |z|, the two-sided deviation of χ² from its expected "
            "value (green = on target, red = off target in either "
            "direction).\nCell text is the raw χ². A χ² far BELOW the ideal "
            "is a failure too — it means the hash is counting, not mixing.",
            fontsize=10)
        for i in range(len(hash_names)):
            for j in range(len(columns)):
                val = chi_matrix[i][j]
                txt = f"{val:.0f}" if val < 10_000 else f"{val:.0e}"
                ax.text(j, i, txt, ha="center", va="center", fontsize=5)
        fig.colorbar(im, ax=ax, extend="min",
                     label="|z| = |χ² − df| / √(2·df)   "
                           "(log scale; |z| ≤ 2 = passes)")
        fig.tight_layout()
        path = os.path.join(output_dir, "workload_chi_squared.png")
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"  saved {path}")

        # ── 5. Per-workload bucket heatmaps ───────────────────────────
        #
        # One heatmap per input class so the reader can see how each
        # hash function distributes structured keys across buckets.
        n_buckets_wl = cfg["chi_sq_buckets"]
        wl_n = len(next(iter(next(iter(wl_results.values())).values()))["bucket_counts"])
        expected_wl = wl_n  # infer from bucket_counts length? No — use key count
        # wl_n is actually n_buckets; the key count is cfg["collision_n"]
        wl_key_count = cfg["collision_n"]
        expected_wl = wl_key_count / n_buckets_wl
        sigma_wl = math.sqrt(expected_wl)

        for wl_name in wl_names:
            wl_hash_names = list(wl_results.keys())
            data_matrix_wl = [wl_results[h][wl_name]["bucket_counts"]
                              for h in wl_hash_names]

            fig, ax = plt.subplots(figsize=(14, 8))
            im = ax.imshow(data_matrix_wl, aspect="auto", cmap="YlOrRd",
                           interpolation="nearest")
            ax.set_yticks(range(len(wl_hash_names)))
            ax.set_yticklabels(wl_hash_names, fontsize=7)
            ax.set_xlabel("Bucket index")
            ax.set_title(
                f"Bucket Distribution — {wl_name} keys "
                f"({wl_key_count:,} keys → {n_buckets_wl} buckets)\n"
                f"Expected {expected_wl:.0f} per bucket",
                fontsize=10)
            fig.colorbar(im, ax=ax, label="Keys per bucket")
            fig.tight_layout()
            path = os.path.join(output_dir,
                                f"bucket_heatmap_{wl_name}.png")
            fig.savefig(path, dpi=150)
            plt.close(fig)
            print(f"  saved {path}")


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Benchmark all 23 hash functions")
    ap.add_argument("--quick", action="store_true",
                    help="Reduced sample sizes for a faster run (~1 min)")
    ap.add_argument("--no-plots", action="store_true",
                    help="Skip matplotlib plot generation")
    ap.add_argument("--plot-dir", default="plots",
                    help="Output directory for plots (default: plots/)")
    args = ap.parse_args()

    cfg = QUICK_CONFIG if args.quick else FULL_CONFIG

    targets = bench_targets()

    print("HashCraft Benchmark")
    print("─" * 40)
    print(f"  Hash functions:    {len(REGISTRY)}"
          f" (+{len(CONTROLS)} control)")
    print(f"  Mode:              {'quick' if args.quick else 'full'}")
    print(f"  Throughput buffer: {cfg['throughput_bytes'] // 1024} KB"
          f" × {cfg['throughput_iters']} iters")
    print(f"  Latency calls:     {cfg['latency_iters']:,}")
    print(f"  χ² keys:           {cfg['chi_sq_n']:,}"
          f" → {cfg['chi_sq_buckets']} and"
          f" {cfg['chi_sq_buckets_p2']} buckets")
    print(f"  Avalanche samples: {cfg['avalanche_samples']:,}")
    print(f"  Collision keys:    {cfg['collision_n']:,}"
          f" → {cfg['collision_buckets']:,} buckets")
    print()

    # Pre-generate workloads so every hash function sees identical keys
    print("Generating workloads …")
    keys_chi = gen_random_keys(cfg["chi_sq_n"])
    keys_col = gen_random_keys(cfg["collision_n"])
    print(f"  {len(keys_chi):,} random keys for χ² distribution")
    print(f"  {len(keys_col):,} random keys for collision rate")
    print()

    results = {}
    total = len(targets)

    for idx, (name, (fn, cat, bits)) in enumerate(targets.items(), 1):
        tag = f"[{idx:2d}/{total}]"
        print(f"{tag} {name:20s} ", end="", flush=True)

        tp = measure_throughput(fn, cfg["throughput_bytes"],
                                cfg["throughput_iters"])
        print("T", end="", flush=True)

        lat = measure_latency(fn, cfg["latency_key_len"],
                              cfg["latency_iters"])
        print("L", end="", flush=True)

        chi, bucket_counts = measure_chi_squared(fn, keys_chi,
                                                 cfg["chi_sq_buckets"])
        print("D", end="", flush=True)

        aval, aval_samples = measure_avalanche(fn, cfg["avalanche_samples"])
        print("A", end="", flush=True)

        col, col_curve = measure_collisions(fn, keys_col,
                                            cfg["collision_buckets"])
        print("C", end="", flush=True)

        results[name] = {
            "category":          cat,
            "throughput_mbps":   tp,
            "latency_ns":        lat,
            "chi_squared":       chi,
            "avalanche_pct":     aval,
            "collisions":        col,
            "collision_curve":   col_curve,
            "avalanche_samples": aval_samples,
            "bucket_counts":     bucket_counts,
        }

        print(f"  ✓  {_fmt_tp(tp):>10s}  {_fmt_lat(lat):>8s}"
              f"  χ²={chi:>8.0f}  aval={aval:>5.1f}%"
              f"  col={col:>5d}")

    print_scorecard(results, cfg)

    # ── Per-workload analysis (χ² and collisions on all input classes) ─
    print(f"Per-workload analysis"
          f" ({len(WORKLOADS)} input classes × {total} functions) …")
    wl_n = cfg["collision_n"]
    workload_keys = {}
    for wl_name, gen_fn in WORKLOADS.items():
        workload_keys[wl_name] = gen_fn(wl_n)
    print(f"  Generated {len(workload_keys)} workloads"
          f" × {wl_n:,} keys each")

    b1, b2 = cfg["chi_sq_buckets"], cfg["chi_sq_buckets_p2"]
    wl_results = {}
    for idx, (name, (fn, cat, bits)) in enumerate(targets.items(), 1):
        wl_results[name] = {}
        print(f"  [{idx:2d}/{total}] {name:20s} ", end="", flush=True)
        for wl_name, keys in workload_keys.items():
            chi, counts = measure_chi_squared(fn, keys, b1)
            chi_p2, _ = measure_chi_squared(fn, keys, b2)
            col, _ = measure_collisions(fn, keys, cfg["collision_buckets"])
            wl_results[name][wl_name] = {
                "chi_sq":        chi,
                "chi_sq_p2":     chi_p2,
                "z":             max(chi_sq_z(chi, b1), chi_sq_z(chi_p2, b2)),
                "collisions":    col,
                "bucket_counts": counts,
            }
            print(".", end="", flush=True)
        print(" ✓")
    print()

    print_workload_table(wl_results, cfg)

    if not args.no_plots:
        print("Generating plots …")
        generate_plots(results, cfg, args.plot_dir, wl_results)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
