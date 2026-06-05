#!/usr/bin/env python3
"""
Exploratory Data Analysis: Summary statistics and descriptive plots
for the TOTO outlet winning data.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame | None]:
    outlets = pd.read_csv(DATA_DIR / "outlets_raw.csv", dtype={"postal_code": str})

    win_path = DATA_DIR / "raw" / "outlet_win_history.csv"
    win_history = pd.read_csv(win_path) if win_path.exists() else None
    return outlets, win_history


def outlet_summary(outlets: pd.DataFrame) -> None:
    print("=" * 60)
    print("OUTLET SUMMARY")
    print("=" * 60)
    print(f"Total physical outlets: {len(outlets)}")

    with_wins = outlets[outlets["combined_wins"] > 0]
    print(f"Outlets with at least 1 win: {len(with_wins)}")
    print(f"Outlets with zero wins: {len(outlets) - len(with_wins)}")

    valid_postal = outlets[outlets["postal_code"].fillna("").astype(str).str.strip().str.match(r'^\d{6}$')]
    print(f"Outlets with valid postal codes: {len(valid_postal)}")

    print(f"\nWin count statistics:")
    desc = outlets["combined_wins"].describe()
    for stat in ["mean", "std", "min", "25%", "50%", "75%", "max"]:
        print(f"  {stat}: {desc[stat]:.2f}")

    print(f"\nTotal Group 1 wins: {outlets['group1_wins'].sum()}")
    print(f"Total Group 2 wins: {outlets['group2_wins'].sum()}")
    print(f"Total combined wins: {outlets['combined_wins'].sum()}")

    print(f"\nTop 15 outlets by combined wins:")
    top15 = outlets.nlargest(15, "combined_wins")
    for _, r in top15.iterrows():
        print(f"  {r['outlet_name'][:50]:50s} G1={r['group1_wins']:3.0f} G2={r['group2_wins']:3.0f} Total={r['combined_wins']:3.0f}")

    if "outlet_type" in outlets.columns:
        print(f"\nWins by outlet type:")
        type_wins = outlets.groupby("outlet_type").agg(
            n=("outlet_name", "count"),
            total_wins=("combined_wins", "sum"),
            mean_wins=("combined_wins", "mean"),
        ).sort_values("total_wins", ascending=False)
        print(type_wins.to_string())

    print(f"\nSource distribution:")
    print(outlets["source"].value_counts().to_string())


def temporal_summary(win_history: pd.DataFrame) -> None:
    if win_history is None:
        print("\nNo win history data available for temporal analysis.")
        return

    print(f"\n{'=' * 60}")
    print("WIN HISTORY SUMMARY")
    print("=" * 60)
    print(f"Total win records: {len(win_history)}")

    win_history["draw_number"] = pd.to_numeric(win_history["draw_number"], errors="coerce")
    win_history["prize_amount"] = pd.to_numeric(win_history["prize_amount"], errors="coerce").fillna(0)
    win_history["prize_group"] = pd.to_numeric(win_history["prize_group"], errors="coerce").fillna(0).astype(int)

    g1 = win_history[win_history["prize_group"] == 1]
    g2 = win_history[win_history["prize_group"] == 2]
    print(f"Group 1 records: {len(g1)}")
    print(f"Group 2 records: {len(g2)}")
    print(f"Other/unknown: {len(win_history) - len(g1) - len(g2)}")

    unique_draws = win_history["draw_number"].nunique()
    print(f"Unique draws: {unique_draws}")
    print(f"Draw range: {win_history['draw_number'].min():.0f} to {win_history['draw_number'].max():.0f}")

    if g1["prize_amount"].sum() > 0:
        print(f"\nGroup 1 prize amounts:")
        print(f"  Mean: S${g1['prize_amount'].mean():,.0f}")
        print(f"  Median: S${g1['prize_amount'].median():,.0f}")
        print(f"  Max: S${g1['prize_amount'].max():,.0f}")


def plot_distributions(outlets: pd.DataFrame, win_history: pd.DataFrame | None) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))

    wins = outlets["combined_wins"]
    axes[0, 0].hist(wins, bins=50, color="#2196F3", alpha=0.7, edgecolor="black")
    axes[0, 0].set_xlabel("Combined Wins")
    axes[0, 0].set_ylabel("Number of Outlets")
    axes[0, 0].set_title(f"Distribution of Combined Wins\n(mean={wins.mean():.1f}, median={wins.median():.0f})")

    wins_nonzero = wins[wins > 0]
    axes[0, 1].hist(wins_nonzero, bins=40, color="#4CAF50", alpha=0.7, edgecolor="black")
    axes[0, 1].set_xlabel("Combined Wins (excl. zero)")
    axes[0, 1].set_ylabel("Number of Outlets")
    axes[0, 1].set_title(f"Wins Distribution (non-zero only, n={len(wins_nonzero)})")

    top20 = outlets.nlargest(20, "combined_wins")
    y = range(len(top20))
    axes[0, 2].barh(list(y), top20["group1_wins"], label="Group 1", color="#F44336", alpha=0.8)
    axes[0, 2].barh(list(y), top20["group2_wins"], left=top20["group1_wins"], label="Group 2", color="#2196F3", alpha=0.8)
    axes[0, 2].set_yticks(list(y))
    axes[0, 2].set_yticklabels([n[:35] for n in top20["outlet_name"]], fontsize=7)
    axes[0, 2].set_xlabel("Wins")
    axes[0, 2].set_title("Top 20 Outlets by Total Wins")
    axes[0, 2].legend()
    axes[0, 2].invert_yaxis()

    if "outlet_type" in outlets.columns:
        type_wins = outlets.groupby("outlet_type")["combined_wins"].sum().sort_values(ascending=False)
        if len(type_wins) > 0:
            axes[1, 0].bar(range(len(type_wins)), type_wins.values, color="#FF9800", alpha=0.8)
            axes[1, 0].set_xticks(range(len(type_wins)))
            axes[1, 0].set_xticklabels(type_wins.index, rotation=45, ha="right", fontsize=7)
            axes[1, 0].set_ylabel("Total Wins")
            axes[1, 0].set_title("Wins by Outlet Type")

    axes[1, 1].scatter(outlets["group1_wins"], outlets["group2_wins"], alpha=0.5, s=20, color="#9C27B0")
    axes[1, 1].set_xlabel("Group 1 Wins")
    axes[1, 1].set_ylabel("Group 2 Wins")
    axes[1, 1].set_title("Group 1 vs Group 2 Wins per Outlet")

    if win_history is not None:
        win_history["prize_amount"] = pd.to_numeric(win_history["prize_amount"], errors="coerce").fillna(0)
        nonzero_prizes = win_history[win_history["prize_amount"] > 0]["prize_amount"]
        if len(nonzero_prizes) > 0:
            axes[1, 2].hist(nonzero_prizes / 1000, bins=50, color="#009688", alpha=0.7, edgecolor="black")
            axes[1, 2].set_xlabel("Prize Amount (S$ thousands)")
            axes[1, 2].set_ylabel("Count")
            axes[1, 2].set_title(f"Prize Amount Distribution\n(n={len(nonzero_prizes)})")
        else:
            axes[1, 2].text(0.5, 0.5, "No prize amounts\navailable", ha="center", va="center", fontsize=12)
    else:
        axes[1, 2].text(0.5, 0.5, "No win history\ndata", ha="center", va="center", fontsize=12)

    plt.tight_layout()
    path = OUTPUT_DIR / "eda_summary.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\nPlot saved to {path}")


def main() -> None:
    outlets, win_history = load_data()
    outlet_summary(outlets)
    temporal_summary(win_history)
    plot_distributions(outlets, win_history)


if __name__ == "__main__":
    main()
