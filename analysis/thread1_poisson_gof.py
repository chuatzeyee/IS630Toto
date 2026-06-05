#!/usr/bin/env python3
"""
Thread 1: Poisson Goodness-of-Fit Test
AQ1: Do wins follow a Poisson distribution across outlets?

If outlets have equal per-ticket probability, win counts should follow
Poisson(lambda) where lambda = total_wins / n_outlets.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data() -> pd.DataFrame:
    path = DATA_DIR / "outlets_raw.csv"
    df = pd.read_csv(path)
    df = df[df["combined_wins"] >= 0].copy()
    return df


def poisson_gof(df: pd.DataFrame) -> dict:
    wins = df["combined_wins"].values
    n = len(wins)
    total = wins.sum()
    lam = total / n

    print(f"Outlets: {n}")
    print(f"Total wins: {total}")
    print(f"Lambda (mean): {lam:.4f}")
    print(f"Variance: {np.var(wins, ddof=1):.4f}")
    print(f"Dispersion index (Var/Mean): {np.var(wins, ddof=1) / lam:.4f}")
    print()

    max_bin = max(int(np.percentile(wins, 95)) + 1, 5)
    bins = list(range(max_bin + 1)) + [wins.max() + 1]
    bin_labels = [str(i) for i in range(max_bin)] + [f"{max_bin}+"]

    observed = np.histogram(wins, bins=[b - 0.5 for b in range(max_bin + 1)] + [wins.max() + 0.5])[0]

    expected_probs = [stats.poisson.pmf(k, lam) for k in range(max_bin)]
    expected_probs.append(1 - stats.poisson.cdf(max_bin - 1, lam))
    expected = np.array(expected_probs) * n

    print(f"{'Wins':<8} {'Observed':<12} {'Expected':<12} {'(O-E)^2/E':<12}")
    print("-" * 44)
    for i, label in enumerate(bin_labels):
        residual = (observed[i] - expected[i]) ** 2 / expected[i] if expected[i] > 0 else 0
        print(f"{label:<8} {observed[i]:<12} {expected[i]:<12.2f} {residual:<12.4f}")

    mask = expected >= 5
    if not mask.all():
        combined_obs = np.concatenate([observed[mask], [observed[~mask].sum()]])
        combined_exp = np.concatenate([expected[mask], [expected[~mask].sum()]])
        print(f"\nBins with E<5 combined for chi-squared test")
    else:
        combined_obs = observed
        combined_exp = expected

    chi2, p_value = stats.chisquare(combined_obs, combined_exp)
    dof = len(combined_obs) - 1 - 1

    print(f"\nChi-squared statistic: {chi2:.4f}")
    print(f"Degrees of freedom: {dof}")
    print(f"p-value: {p_value:.6f}")
    print(f"Conclusion: {'REJECT H0' if p_value < 0.05 else 'FAIL TO REJECT H0'} at alpha=0.05")

    disp_stat = (n - 1) * np.var(wins, ddof=1) / lam
    disp_p = 1 - stats.chi2.cdf(disp_stat, n - 1)
    print(f"\nDispersion test statistic: {disp_stat:.2f}")
    print(f"Dispersion p-value: {disp_p:.6f}")
    if np.var(wins, ddof=1) / lam > 1:
        print("Overdispersion detected (Var/Mean > 1) — consistent with volume differences")
    else:
        print("No overdispersion — consistent with equal per-ticket probability")

    return {
        "n_outlets": n, "total_wins": total, "lambda": lam,
        "chi2": chi2, "p_value": p_value, "dof": dof,
        "dispersion_index": np.var(wins, ddof=1) / lam,
        "observed": observed, "expected": expected, "bin_labels": bin_labels,
    }


def plot_results(results: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    x = np.arange(len(results["bin_labels"]))
    width = 0.35
    axes[0].bar(x - width / 2, results["observed"], width, label="Observed", color="#2196F3", alpha=0.8)
    axes[0].bar(x + width / 2, results["expected"], width, label="Expected (Poisson)", color="#FF9800", alpha=0.8)
    axes[0].set_xlabel("Number of Wins")
    axes[0].set_ylabel("Number of Outlets")
    axes[0].set_title(f"Observed vs Expected Win Distribution\n(λ={results['lambda']:.2f}, χ²={results['chi2']:.2f}, p={results['p_value']:.4f})")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(results["bin_labels"])
    axes[0].legend()

    wins_range = np.arange(0, max(int(results["lambda"] * 3), 10) + 1)
    pmf = stats.poisson.pmf(wins_range, results["lambda"])
    axes[1].plot(wins_range, pmf, "o-", color="#FF9800", label=f"Poisson(λ={results['lambda']:.2f})", markersize=6)
    axes[1].set_xlabel("Number of Wins")
    axes[1].set_ylabel("Probability")
    axes[1].set_title("Theoretical Poisson PMF")
    axes[1].legend()

    plt.tight_layout()
    path = OUTPUT_DIR / "thread1_poisson_gof.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\nPlot saved to {path}")


def main() -> None:
    print("=" * 60)
    print("THREAD 1: Poisson Goodness-of-Fit Test")
    print("=" * 60)

    df = load_data()
    results = poisson_gof(df)
    plot_results(results)


if __name__ == "__main__":
    main()
