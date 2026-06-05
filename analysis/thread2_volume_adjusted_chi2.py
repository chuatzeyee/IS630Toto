#!/usr/bin/env python3
"""
Thread 2: Volume-Adjusted Chi-Squared Test
AQ2: After adjusting for estimated sales volume, are Group 1 wins
distributed proportionally across outlets?

Uses HDB dwelling units within planning areas as a proxy for foot
traffic / ticket sales volume.
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


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    geocoded_path = DATA_DIR / "outlets_geocoded.csv"
    if geocoded_path.exists():
        outlets = pd.read_csv(geocoded_path, dtype={"postal_code": str})
    else:
        outlets = pd.read_csv(DATA_DIR / "outlets_raw.csv", dtype={"postal_code": str})
    hdb = pd.read_csv(DATA_DIR / "supplementary" / "hdb_dwelling_units_by_town.csv")
    return outlets, hdb


def build_volume_proxy(outlets: pd.DataFrame, hdb: pd.DataFrame) -> pd.DataFrame:
    hdb.columns = [c.strip().lower().replace(" ", "_") for c in hdb.columns]

    town_col = next((c for c in hdb.columns if "town" in c), None)
    units_col = next((c for c in hdb.columns if "dwelling" in c or "units" in c), None)
    year_col = next((c for c in hdb.columns if "year" in c or "financial" in c), None)

    if town_col and units_col:
        hdb[units_col] = pd.to_numeric(hdb[units_col], errors="coerce").fillna(0)
        if year_col:
            latest = hdb[year_col].max()
            hdb_latest = hdb[hdb[year_col] == latest]
        else:
            hdb_latest = hdb
        hdb_summary = hdb_latest.groupby(town_col)[units_col].sum().reset_index()
        hdb_summary.columns = ["planning_area", "dwelling_units"]
    else:
        print("WARNING: Could not identify town/dwelling columns in HDB data")
        hdb_summary = pd.DataFrame(columns=["planning_area", "dwelling_units"])

    hdb_summary["planning_area"] = hdb_summary["planning_area"].str.upper().str.strip()

    if "planning_area" in outlets.columns:
        outlets["planning_area_upper"] = outlets["planning_area"].str.upper().str.strip()
        merged = outlets.merge(hdb_summary, left_on="planning_area_upper", right_on="planning_area",
                               how="left", suffixes=("", "_hdb"))
        merged["dwelling_units"] = merged["dwelling_units"].fillna(merged["dwelling_units"].median())
    else:
        merged = outlets.copy()
        median_units = hdb_summary["dwelling_units"].median() if len(hdb_summary) > 0 else 1000
        merged["dwelling_units"] = median_units

    merged["volume_proxy"] = merged["dwelling_units"].clip(lower=1)
    return merged


def chi2_volume_adjusted(df: pd.DataFrame) -> dict:
    df_valid = df[df["combined_wins"] > 0].copy()
    if len(df_valid) == 0:
        df_valid = df[df["combined_wins"] >= 0].copy()

    total_wins = df_valid["combined_wins"].sum()
    total_volume = df_valid["volume_proxy"].sum()

    df_valid["expected_wins"] = total_wins * (df_valid["volume_proxy"] / total_volume)

    print(f"Outlets analysed: {len(df_valid)}")
    print(f"Total wins: {total_wins}")
    print(f"Total volume proxy: {total_volume:.0f}")
    print()

    observed = df_valid["combined_wins"].values.astype(float)
    expected = df_valid["expected_wins"].values

    chi2 = np.sum((observed - expected) ** 2 / expected)
    dof = len(observed) - 1
    p_value = 1 - stats.chi2.cdf(chi2, dof)

    print(f"Chi-squared statistic: {chi2:.4f}")
    print(f"Degrees of freedom: {dof}")
    print(f"p-value: {p_value:.6f}")
    print(f"Conclusion: {'REJECT H0' if p_value < 0.05 else 'FAIL TO REJECT H0'} at alpha=0.05")

    n_sims = 10000
    print(f"\nMonte Carlo simulation ({n_sims:,} iterations)...")
    probs = expected / expected.sum()
    mc_chi2 = np.zeros(n_sims)
    rng = np.random.default_rng(42)
    for sim in range(n_sims):
        sim_counts = rng.multinomial(int(total_wins), probs).astype(float)
        mc_chi2[sim] = np.sum((sim_counts - expected) ** 2 / expected)

    mc_p_value = np.mean(mc_chi2 >= chi2)
    print(f"Monte Carlo p-value: {mc_p_value:.6f}")

    df_valid["standardized_residual"] = (observed - expected) / np.sqrt(expected)

    top_positive = df_valid.nlargest(10, "standardized_residual")[
        ["outlet_name", "combined_wins", "expected_wins", "standardized_residual"]
    ]
    top_negative = df_valid.nsmallest(5, "standardized_residual")[
        ["outlet_name", "combined_wins", "expected_wins", "standardized_residual"]
    ]

    print("\nTop 10 outlets with HIGHER wins than expected:")
    print(top_positive.to_string(index=False))
    print("\nTop 5 outlets with LOWER wins than expected:")
    print(top_negative.to_string(index=False))

    return {
        "chi2": chi2, "dof": dof, "p_value": p_value, "mc_p_value": mc_p_value,
        "df": df_valid, "mc_chi2": mc_chi2,
    }


def plot_results(results: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    df = results["df"]
    axes[0].scatter(df["expected_wins"], df["combined_wins"], alpha=0.5, s=20, color="#2196F3")
    max_val = max(df["combined_wins"].max(), df["expected_wins"].max())
    axes[0].plot([0, max_val], [0, max_val], "r--", alpha=0.7, label="Perfect fit")
    axes[0].set_xlabel("Expected Wins (volume-adjusted)")
    axes[0].set_ylabel("Observed Wins")
    axes[0].set_title("Observed vs Volume-Adjusted Expected Wins")
    axes[0].legend()

    residuals = df["standardized_residual"]
    axes[1].hist(residuals, bins=30, color="#4CAF50", alpha=0.7, edgecolor="black")
    axes[1].axvline(x=0, color="red", linestyle="--")
    axes[1].set_xlabel("Standardized Residual")
    axes[1].set_ylabel("Count")
    axes[1].set_title("Distribution of Standardized Residuals")

    axes[2].hist(results["mc_chi2"], bins=50, alpha=0.7, color="#9C27B0", density=True)
    axes[2].axvline(x=results["chi2"], color="red", linewidth=2, label=f"Observed χ²={results['chi2']:.1f}")
    axes[2].set_xlabel("Chi-squared Statistic")
    axes[2].set_ylabel("Density")
    axes[2].set_title(f"Monte Carlo Null Distribution\n(MC p={results['mc_p_value']:.4f})")
    axes[2].legend()

    plt.tight_layout()
    path = OUTPUT_DIR / "thread2_volume_adjusted.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\nPlot saved to {path}")


def main() -> None:
    print("=" * 60)
    print("THREAD 2: Volume-Adjusted Chi-Squared Test")
    print("=" * 60)

    outlets, hdb = load_data()
    merged = build_volume_proxy(outlets, hdb)
    results = chi2_volume_adjusted(merged)
    plot_results(results)


if __name__ == "__main__":
    main()
