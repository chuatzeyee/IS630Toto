#!/usr/bin/env python3
"""
Thread 3: Bayesian Beta-Binomial Analysis
AQ3: Starting from a skeptical prior, do posterior win-rate distributions
differ meaningfully between "reputed lucky" and other outlets?
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

REPUTED_LUCKY = [
    "Tong Aik Huat",
    "Delisia Agency",
    "Ng Teo Guan",
    "Tan Wee Fong",
]


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "outlets_raw.csv", dtype={"postal_code": str})
    return df


def is_reputed_lucky(name: str) -> bool:
    name_lower = name.lower()
    return any(r.lower() in name_lower for r in REPUTED_LUCKY)


def bayesian_analysis(df: pd.DataFrame) -> dict:
    total_draws = 1200
    df["is_lucky_reputed"] = df["outlet_name"].apply(is_reputed_lucky)
    df["win_rate_raw"] = df["combined_wins"] / total_draws

    lucky = df[df["is_lucky_reputed"]]
    others = df[~df["is_lucky_reputed"]]

    print(f"'Reputed lucky' outlets: {len(lucky)}")
    print(f"Other outlets: {len(others)}")
    print()

    alpha_prior = 1.0
    beta_prior = 999.0

    print(f"Prior: Beta({alpha_prior}, {beta_prior})")
    print(f"Prior mean: {alpha_prior / (alpha_prior + beta_prior):.6f}")
    print(f"Prior 95% CI: [{stats.beta.ppf(0.025, alpha_prior, beta_prior):.6f}, "
          f"{stats.beta.ppf(0.975, alpha_prior, beta_prior):.6f}]")
    print()

    results_rows = []
    for _, row in df.iterrows():
        wins = row["combined_wins"]
        losses = total_draws - wins
        a_post = alpha_prior + wins
        b_post = beta_prior + losses
        post_mean = a_post / (a_post + b_post)
        ci_low = stats.beta.ppf(0.025, a_post, b_post)
        ci_high = stats.beta.ppf(0.975, a_post, b_post)
        results_rows.append({
            "outlet_name": row["outlet_name"],
            "wins": wins,
            "alpha_post": a_post,
            "beta_post": b_post,
            "posterior_mean": post_mean,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "is_lucky_reputed": row["is_lucky_reputed"],
        })

    results_df = pd.DataFrame(results_rows)

    print("Posterior summaries for 'reputed lucky' outlets:")
    lucky_results = results_df[results_df["is_lucky_reputed"]].sort_values("posterior_mean", ascending=False)
    for _, r in lucky_results.iterrows():
        print(f"  {r['outlet_name']}: wins={r['wins']:.0f}, "
              f"posterior mean={r['posterior_mean']:.6f}, "
              f"95% CI=[{r['ci_low']:.6f}, {r['ci_high']:.6f}]")

    print("\nTop 10 outlets by posterior mean (all):")
    top10 = results_df.nlargest(10, "posterior_mean")
    for _, r in top10.iterrows():
        marker = " ***" if r["is_lucky_reputed"] else ""
        print(f"  {r['outlet_name']}: posterior mean={r['posterior_mean']:.6f}, "
              f"95% CI=[{r['ci_low']:.6f}, {r['ci_high']:.6f}]{marker}")

    lucky_means = results_df[results_df["is_lucky_reputed"]]["posterior_mean"].values
    other_means = results_df[~results_df["is_lucky_reputed"]]["posterior_mean"].values

    if len(lucky_means) > 0 and len(other_means) > 0:
        n_sims = 100000
        rng = np.random.default_rng(42)
        prob_lucky_higher = 0
        for _, r in lucky_results.iterrows():
            lucky_samples = rng.beta(r["alpha_post"], r["beta_post"], n_sims)
            overall_mean_post = results_df["posterior_mean"].mean()
            prob_lucky_higher += np.mean(lucky_samples > overall_mean_post)
        prob_lucky_higher /= len(lucky_results)
        print(f"\nAvg P(lucky outlet rate > overall mean): {prob_lucky_higher:.4f}")

    overlap_count = 0
    for _, lr in lucky_results.iterrows():
        within_range = results_df[
            (results_df["ci_low"] <= lr["ci_high"]) &
            (results_df["ci_high"] >= lr["ci_low"]) &
            (~results_df["is_lucky_reputed"])
        ]
        overlap_count += len(within_range)
    avg_overlap = overlap_count / max(len(lucky_results), 1)
    print(f"Avg number of 'other' outlets with overlapping 95% CI: {avg_overlap:.0f}/{len(others)}")

    return {"results_df": results_df, "lucky_results": lucky_results, "alpha_prior": alpha_prior, "beta_prior": beta_prior}


def plot_results(results: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    df = results["results_df"]
    lucky_df = results["lucky_results"]

    x = np.linspace(0, df["posterior_mean"].max() * 2, 1000)
    for _, r in lucky_df.iterrows():
        y = stats.beta.pdf(x, r["alpha_post"], r["beta_post"])
        axes[0].plot(x, y, label=r["outlet_name"][:30], linewidth=2)

    top_others = df[~df["is_lucky_reputed"]].nlargest(3, "posterior_mean")
    for _, r in top_others.iterrows():
        y = stats.beta.pdf(x, r["alpha_post"], r["beta_post"])
        axes[0].plot(x, y, "--", label=r["outlet_name"][:30], alpha=0.6)

    axes[0].set_xlabel("Win Rate (per draw)")
    axes[0].set_ylabel("Density")
    axes[0].set_title("Posterior Distributions: Lucky vs Top Others")
    axes[0].legend(fontsize=7)

    sorted_df = df.sort_values("posterior_mean")
    y_pos = range(len(sorted_df))
    colors = ["red" if r else "steelblue" for r in sorted_df["is_lucky_reputed"]]
    axes[1].barh(list(y_pos), sorted_df["posterior_mean"], color=colors, alpha=0.7, height=1.0)
    axes[1].set_xlabel("Posterior Mean Win Rate")
    axes[1].set_title("All Outlets: Posterior Win Rates\n(red = reputed lucky)")
    axes[1].set_yticks([])

    a_prior = results["alpha_prior"]
    b_prior = results["beta_prior"]
    x_prior = np.linspace(0, 0.01, 1000)
    axes[2].plot(x_prior, stats.beta.pdf(x_prior, a_prior, b_prior), "k--",
                 label=f"Prior Beta({a_prior:.0f},{b_prior:.0f})", linewidth=2)

    if len(lucky_df) > 0:
        r = lucky_df.iloc[0]
        x_post = np.linspace(0, r["posterior_mean"] * 3, 1000)
        axes[2].plot(x_post, stats.beta.pdf(x_post, r["alpha_post"], r["beta_post"]),
                     "r-", label=f"Posterior: {r['outlet_name'][:20]}", linewidth=2)
    axes[2].set_xlabel("Win Rate")
    axes[2].set_ylabel("Density")
    axes[2].set_title("Prior vs Posterior Update")
    axes[2].legend(fontsize=8)

    plt.tight_layout()
    path = OUTPUT_DIR / "thread3_bayesian.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\nPlot saved to {path}")


def main() -> None:
    print("=" * 60)
    print("THREAD 3: Bayesian Beta-Binomial Analysis")
    print("=" * 60)

    df = load_data()
    results = bayesian_analysis(df)
    plot_results(results)


if __name__ == "__main__":
    main()
