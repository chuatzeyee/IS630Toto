#!/usr/bin/env python3
"""
Thread 4: Geographic Clustering / Moran's I
AQ4: Are winning outlets spatially clustered beyond what population density predicts?

Aggregates wins by planning area, computes chi-squared test (observed vs
population-proportional expected), then Moran's I on standardised residuals.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data() -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    geocoded_path = DATA_DIR / "outlets_geocoded.csv"
    if geocoded_path.exists():
        outlets = pd.read_csv(geocoded_path, dtype={"postal_code": str})
    else:
        outlets = pd.read_csv(DATA_DIR / "outlets_raw.csv", dtype={"postal_code": str})

    boundary_path = DATA_DIR / "supplementary" / "planning_area_boundary.geojson"
    boundaries = gpd.read_file(boundary_path) if boundary_path.exists() else gpd.GeoDataFrame()
    return outlets, boundaries


def assign_planning_areas(outlets: pd.DataFrame, boundaries: gpd.GeoDataFrame) -> pd.DataFrame:
    if "planning_area" in outlets.columns and outlets["planning_area"].notna().sum() > 10:
        return outlets

    if len(boundaries) == 0 or "latitude" not in outlets.columns:
        return outlets

    valid = outlets[outlets["latitude"].notna() & (outlets["latitude"] != "")].copy()
    valid["latitude"] = pd.to_numeric(valid["latitude"], errors="coerce")
    valid["longitude"] = pd.to_numeric(valid["longitude"], errors="coerce")
    valid = valid.dropna(subset=["latitude", "longitude"])

    if len(valid) == 0:
        return outlets

    gdf = gpd.GeoDataFrame(
        valid,
        geometry=gpd.points_from_xy(valid["longitude"], valid["latitude"]),
        crs="EPSG:4326",
    )

    boundaries = boundaries.to_crs("EPSG:4326")
    name_col = next((c for c in boundaries.columns if "name" in c.lower() or "pln_area" in c.lower()), None)
    if name_col is None:
        name_col = boundaries.columns[0]

    joined = gpd.sjoin(gdf, boundaries[[name_col, "geometry"]], how="left", predicate="within")
    outlets.loc[valid.index, "planning_area"] = joined[name_col].values
    return outlets


def spatial_analysis(outlets: pd.DataFrame, boundaries: gpd.GeoDataFrame) -> dict:
    outlets = assign_planning_areas(outlets, boundaries)

    if "planning_area" not in outlets.columns or outlets["planning_area"].isna().all():
        print("WARNING: No planning area data available. Spatial analysis cannot proceed.")
        print("  Need geocoded outlets with planning_area column.")
        print("  Re-run after geocoding with OneMap auth credentials.")
        return {}

    pop_path = DATA_DIR / "supplementary" / "census2020_pop_by_dwelling.csv"
    if pop_path.exists():
        pop = pd.read_csv(pop_path)
        area_totals = pop[pop.iloc[:, 0].str.contains("- Total", na=False)].copy()
        area_totals["planning_area"] = area_totals.iloc[:, 0].str.replace(" - Total", "", regex=False).str.strip()
        area_totals["population"] = pd.to_numeric(area_totals.iloc[:, 1], errors="coerce").fillna(0)
        pop_by_area = area_totals[["planning_area", "population"]].copy()
        pop_by_area["planning_area"] = pop_by_area["planning_area"].str.upper().str.strip()
    else:
        pop_by_area = pd.DataFrame(columns=["planning_area", "population"])

    outlets["planning_area_upper"] = outlets["planning_area"].str.upper().str.strip()
    area_wins = outlets.groupby("planning_area_upper").agg(
        observed_wins=("combined_wins", "sum"),
        n_outlets=("outlet_name", "count"),
    ).reset_index()
    area_wins.columns = ["planning_area", "observed_wins", "n_outlets"]

    if len(pop_by_area) > 0:
        area_wins = area_wins.merge(pop_by_area, on="planning_area", how="left")
        area_wins["population"] = area_wins["population"].fillna(area_wins["population"].median())
    else:
        area_wins["population"] = area_wins["n_outlets"]

    total_wins = area_wins["observed_wins"].sum()
    total_pop = area_wins["population"].sum()
    area_wins["expected_wins"] = total_wins * (area_wins["population"] / total_pop)
    area_wins["residual"] = area_wins["observed_wins"] - area_wins["expected_wins"]
    area_wins["std_residual"] = area_wins["residual"] / np.sqrt(area_wins["expected_wins"].clip(lower=0.1))

    print(f"Planning areas with outlets: {len(area_wins)}")
    print(f"Total wins: {total_wins}")
    print()

    valid_areas = area_wins[area_wins["expected_wins"] >= 1]
    if len(valid_areas) > 1:
        chi2 = np.sum(valid_areas["residual"] ** 2 / valid_areas["expected_wins"])
        dof = len(valid_areas) - 1
        p_value = 1 - stats.chi2.cdf(chi2, dof)
        print(f"Chi-squared (area-level): {chi2:.4f}")
        print(f"Degrees of freedom: {dof}")
        print(f"p-value: {p_value:.6f}")
        print(f"Conclusion: {'REJECT H0' if p_value < 0.05 else 'FAIL TO REJECT H0'}")
    else:
        chi2, p_value = 0, 1
        print("Not enough valid areas for chi-squared test")

    print("\nTop 5 areas by standardized residual (over-winning):")
    top5 = area_wins.nlargest(5, "std_residual")
    print(top5[["planning_area", "observed_wins", "expected_wins", "std_residual"]].to_string(index=False))

    print("\nBottom 5 areas by standardized residual (under-winning):")
    bot5 = area_wins.nsmallest(5, "std_residual")
    print(bot5[["planning_area", "observed_wins", "expected_wins", "std_residual"]].to_string(index=False))

    morans_i = None
    morans_p = None
    try:
        from libpysal.weights import Queen
        from esda.moran import Moran

        if len(boundaries) > 0:
            name_col = next((c for c in boundaries.columns if "name" in c.lower() or "pln_area" in c.lower()), boundaries.columns[0])
            boundaries["pa_upper"] = boundaries[name_col].str.upper().str.strip()
            merged_geo = boundaries.merge(area_wins, left_on="pa_upper", right_on="planning_area", how="inner")

            if len(merged_geo) > 3:
                w = Queen.from_dataframe(merged_geo)
                w.transform = "r"
                mi = Moran(merged_geo["std_residual"].values, w)
                morans_i = mi.I
                morans_p = mi.p_sim

                print(f"\nMoran's I: {morans_i:.4f}")
                print(f"Expected I: {mi.EI:.4f}")
                print(f"p-value (permutation): {morans_p:.4f}")
                print(f"Conclusion: {'Spatial autocorrelation detected' if morans_p < 0.05 else 'No significant spatial autocorrelation'}")
            else:
                print("\nNot enough matched areas for Moran's I computation")
    except ImportError:
        print("\nWARNING: libpysal/esda not installed. Skipping Moran's I.")

    return {
        "area_wins": area_wins, "chi2": chi2, "p_value": p_value,
        "morans_i": morans_i, "morans_p": morans_p, "boundaries": boundaries,
    }


def plot_results(results: dict) -> None:
    if not results:
        return

    area_wins = results["area_wins"]
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    top_areas = area_wins.nlargest(20, "observed_wins")
    x = np.arange(len(top_areas))
    width = 0.35
    axes[0].barh(x - width / 2, top_areas["observed_wins"], width, label="Observed", color="#2196F3")
    axes[0].barh(x + width / 2, top_areas["expected_wins"], width, label="Expected", color="#FF9800")
    axes[0].set_yticks(x)
    axes[0].set_yticklabels(top_areas["planning_area"].str.title(), fontsize=7)
    axes[0].set_xlabel("Wins")
    axes[0].set_title("Top 20 Areas: Observed vs Expected Wins")
    axes[0].legend()
    axes[0].invert_yaxis()

    axes[1].scatter(area_wins["expected_wins"], area_wins["observed_wins"], s=40, alpha=0.7, color="#4CAF50")
    max_val = max(area_wins["observed_wins"].max(), area_wins["expected_wins"].max())
    axes[1].plot([0, max_val], [0, max_val], "r--", alpha=0.7)
    axes[1].set_xlabel("Expected Wins (population-proportional)")
    axes[1].set_ylabel("Observed Wins")
    axes[1].set_title(f"Area-Level: Observed vs Expected\n(χ²={results['chi2']:.1f}, p={results['p_value']:.4f})")

    axes[2].hist(area_wins["std_residual"], bins=20, color="#9C27B0", alpha=0.7, edgecolor="black")
    axes[2].axvline(x=0, color="red", linestyle="--")
    axes[2].set_xlabel("Standardized Residual")
    axes[2].set_ylabel("Count")
    mi_str = f", I={results['morans_i']:.3f}" if results.get("morans_i") is not None else ""
    axes[2].set_title(f"Distribution of Area Residuals{mi_str}")

    plt.tight_layout()
    path = OUTPUT_DIR / "thread4_spatial.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\nPlot saved to {path}")


def main() -> None:
    print("=" * 60)
    print("THREAD 4: Spatial Analysis / Moran's I")
    print("=" * 60)

    outlets, boundaries = load_data()
    results = spatial_analysis(outlets, boundaries)
    plot_results(results)


if __name__ == "__main__":
    main()
