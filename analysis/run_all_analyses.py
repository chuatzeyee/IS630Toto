#!/usr/bin/env python3
"""
Master runner: executes all 6 statistical analysis threads sequentially.
Each thread produces console output and saves plots to analysis/output/.
"""

import importlib
import traceback
from pathlib import Path

THREADS = [
    ("thread1_poisson_gof", "Thread 1: Poisson GOF"),
    ("thread2_volume_adjusted_chi2", "Thread 2: Volume-Adjusted Chi²"),
    ("thread3_bayesian_beta_binomial", "Thread 3: Bayesian Beta-Binomial"),
    ("thread4_spatial_morans_i", "Thread 4: Spatial / Moran's I"),
    ("thread5_runs_test", "Thread 5: Runs Test (Hot Hand)"),
    ("thread6_mann_whitney", "Thread 6: Mann-Whitney U"),
]


def main() -> None:
    print("=" * 70)
    print("  TOTO Lucky Outlet Analysis: Running All 6 Threads")
    print("=" * 70)

    results = []
    for module_name, label in THREADS:
        print(f"\n{'#' * 70}")
        print(f"  {label}")
        print(f"{'#' * 70}\n")
        try:
            mod = importlib.import_module(module_name)
            mod.main()
            results.append((label, "OK"))
        except Exception as e:
            print(f"\n[ERROR] {label} failed: {e}")
            traceback.print_exc()
            results.append((label, f"FAILED: {e}"))

    print(f"\n{'=' * 70}")
    print("  Summary")
    print(f"{'=' * 70}")
    for label, status in results:
        print(f"  {label}: {status}")

    output_dir = Path(__file__).parent / "output"
    plots = list(output_dir.glob("*.png"))
    print(f"\nPlots generated: {len(plots)}")
    for p in sorted(plots):
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
