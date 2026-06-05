#!/usr/bin/env python3
"""
Thread 5: Wald-Wolfowitz Runs Test (Hot Hand / Streak Analysis)
AQ5: Do outlets that produce a winner show higher-than-expected winning
rates in subsequent draws (hot hand effect)?

Creates a binary win/loss sequence per outlet across all draws,
then applies runs tests for randomness.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

TOP_N_OUTLETS = 30


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    win_history = pd.read_csv(DATA_DIR / "raw" / "outlet_win_history.csv")
    outlets = pd.read_csv(DATA_DIR / "outlets_raw.csv", dtype={"postal_code": str})
    return win_history, outlets


def wald_wolfowitz_runs_test(sequence: np.ndarray) -> tuple[float, float]:
    """Compute runs test z-statistic and p-value for a binary sequence."""
    n = len(sequence)
    if n < 10:
        return np.nan, np.nan

    n1 = int(sequence.sum())
    n0 = n - n1
    if n1 == 0 or n0 == 0:
        return np.nan, np.nan

    runs = 1 + np.sum(sequence[1:] != sequence[:-1])

    expected_runs = 1 + (2 * n0 * n1) / n
    var_runs = (2 * n0 * n1 * (2 * n0 * n1 - n)) / (n * n * (n - 1))
    if var_runs <= 0:
        return np.nan, np.nan

    z = (runs - expected_runs) / np.sqrt(var_runs)
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    return z, p_value


def build_binary_sequences(win_history: pd.DataFrame, outlets: pd.DataFrame) -> dict[str, np.ndarray]:
    win_history["draw_number"] = pd.to_numeric(win_history["draw_number"], errors="coerce")
    win_history = win_history.dropna(subset=["draw_number"])

    all_draws = sorted(win_history["draw_number"].unique())
    draw_index = {d: i for i, d in enumerate(all_draws)}
    n_draws = len(all_draws)

    top_outlets = outlets.nlargest(TOP_N_OUTLETS, "combined_wins")["outlet_name"].tolist()
    wins_by_outlet = win_history.groupby("outlet_name")["draw_number"].apply(set).to_dict()

    sequences = {}
    for name in top_outlets:
        winning_draws = wins_by_outlet.get(name, set())
        seq = np.zeros(n_draws, dtype=int)
        for d in winning_draws:
            if d in draw_index:
                seq[draw_index[d]] = 1
        sequences[name] = seq

    return sequences


def hot_hand_conditional(win_history: pd.DataFrame) -> dict:
    """Compare P(win in next k draws | recent win) vs P(win | no recent win)."""
    win_history["draw_number"] = pd.to_numeric(win_history["draw_number"], errors="coerce")
    all_draws = sorted(win_history["draw_number"].dropna().unique())
    draw_index = {d: i for i, d in enumerate(all_draws)}
    n_draws = len(all_draws)

    wins_by_outlet = win_history.groupby("outlet_name")["draw_number"].apply(set).to_dict()

    lookback_windows = [1, 3, 5, 10]
    results = {}

    for k in lookback_windows:
        after_win_hits = 0
        after_win_total = 0
        after_no_win_hits = 0
        after_no_win_total = 0

        for name, winning_draws in wins_by_outlet.items():
            if len(winning_draws) < 3:
                continue
            seq = np.zeros(n_draws, dtype=int)
            for d in winning_draws:
                if d in draw_index:
                    seq[draw_index[d]] = 1

            for i in range(k, n_draws):
                recent_wins = seq[i - k:i].sum()
                if recent_wins > 0:
                    after_win_total += 1
                    after_win_hits += seq[i]
                else:
                    after_no_win_total += 1
                    after_no_win_hits += seq[i]

        p_after_win = after_win_hits / max(after_win_total, 1)
        p_after_no_win = after_no_win_hits / max(after_no_win_total, 1)

        if after_win_total > 0 and after_no_win_total > 0:
            z_stat, z_p = proportions_ztest(
                [after_win_hits, after_no_win_hits],
                [after_win_total, after_no_win_total],
            )
        else:
            z_stat, z_p = np.nan, np.nan

        results[k] = {
            "p_after_win": p_after_win, "p_after_no_win": p_after_no_win,
            "n_after_win": after_win_total, "n_after_no_win": after_no_win_total,
            "z_stat": z_stat, "z_p": z_p,
        }

    return results


def runs_analysis(win_history: pd.DataFrame, outlets: pd.DataFrame) -> dict:
    sequences = build_binary_sequences(win_history, outlets)

    print(f"Outlets analysed: {len(sequences)}")
    print(f"Draw range: checking per-outlet binary sequences\n")

    results_rows = []
    for name, seq in sequences.items():
        z, p = wald_wolfowitz_runs_test(seq)
        n_wins = seq.sum()
        results_rows.append({
            "outlet_name": name, "total_wins": n_wins,
            "n_draws": len(seq), "z_statistic": z, "p_value": p,
        })

    results_df = pd.DataFrame(results_rows).dropna(subset=["z_statistic"])

    significant = results_df[results_df["p_value"] < 0.05]
    print(f"Outlets with significant non-random patterns: {len(significant)}/{len(results_df)}")
    if len(significant) > 0:
        print(significant[["outlet_name", "total_wins", "z_statistic", "p_value"]].to_string(index=False))
    else:
        print("  None — all outlets show random win patterns")

    expected_false_positives = len(results_df) * 0.05
    print(f"\nExpected false positives at alpha=0.05: {expected_false_positives:.1f}")
    print(f"Actual significant results: {len(significant)}")
    if len(significant) <= expected_false_positives * 1.5:
        print("Consistent with Type I error rate — no real hot hand effect")

    print("\n--- Hot Hand Conditional Analysis ---")
    hot_hand = hot_hand_conditional(win_history)
    for k, r in hot_hand.items():
        print(f"\nLookback window: {k} draws")
        print(f"  P(win | recent win):    {r['p_after_win']:.6f} (n={r['n_after_win']})")
        print(f"  P(win | no recent win): {r['p_after_no_win']:.6f} (n={r['n_after_no_win']})")
        print(f"  z-test: z={r['z_stat']:.4f}, p={r['z_p']:.4f}" if not np.isnan(r['z_stat']) else "  z-test: N/A")

    return {"results_df": results_df, "hot_hand": hot_hand, "sequences": sequences}


def plot_results(results: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    df = results["results_df"]
    axes[0].scatter(df["total_wins"], df["z_statistic"], alpha=0.6, s=40, color="#2196F3")
    axes[0].axhline(y=1.96, color="red", linestyle="--", alpha=0.5, label="z=1.96")
    axes[0].axhline(y=-1.96, color="red", linestyle="--", alpha=0.5, label="z=-1.96")
    axes[0].axhline(y=0, color="gray", linestyle="-", alpha=0.3)
    axes[0].set_xlabel("Total Wins")
    axes[0].set_ylabel("Runs Test Z-statistic")
    axes[0].set_title("Wald-Wolfowitz Runs Test\n(outside red lines = non-random)")
    axes[0].legend()

    hh = results["hot_hand"]
    windows = sorted(hh.keys())
    p_after = [hh[k]["p_after_win"] for k in windows]
    p_none = [hh[k]["p_after_no_win"] for k in windows]
    x = np.arange(len(windows))
    width = 0.3
    axes[1].bar(x - width / 2, p_after, width, label="After win", color="#FF9800")
    axes[1].bar(x + width / 2, p_none, width, label="After no win", color="#4CAF50")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([str(w) for w in windows])
    axes[1].set_xlabel("Lookback Window (draws)")
    axes[1].set_ylabel("P(win in next draw)")
    axes[1].set_title("Hot Hand Test: Conditional Win Probability")
    axes[1].legend()

    axes[2].hist(df["p_value"], bins=20, color="#9C27B0", alpha=0.7, edgecolor="black")
    axes[2].axhline(y=len(df) / 20, color="red", linestyle="--", label="Expected under H0")
    axes[2].set_xlabel("p-value")
    axes[2].set_ylabel("Count")
    axes[2].set_title("Distribution of Runs Test p-values\n(should be ~uniform under H0)")
    axes[2].legend()

    plt.tight_layout()
    path = OUTPUT_DIR / "thread5_runs_test.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\nPlot saved to {path}")


def main() -> None:
    print("=" * 60)
    print("THREAD 5: Wald-Wolfowitz Runs Test (Hot Hand)")
    print("=" * 60)

    win_history, outlets = load_data()
    results = runs_analysis(win_history, outlets)
    plot_results(results)


if __name__ == "__main__":
    main()
