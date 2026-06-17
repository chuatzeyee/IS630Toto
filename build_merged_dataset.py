import csv
import math
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).parent
SRC = BASE / "data" / "analysis_ready" / "outlets_modeling.csv"
OUT = BASE / "data" / "analysis_ready" / "outlets_modeling_merged.csv"

rows = list(csv.DictReader(open(SRC, newline="", encoding="utf-8")))


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


global_last = max(to_int(r["first_draw"]) + to_int(r["draws_i"]) - 1 for r in rows)

replacement_groups = defaultdict(list)
for r in rows:
    if r["merge_group"] and r["merge_role"] == "replacement":
        replacement_groups[r["merge_group"]].append(r)
replacement_groups = {pc: g for pc, g in replacement_groups.items() if len(g) > 1}

merged = []
for r in rows:
    pc = r["merge_group"]
    if pc in replacement_groups and r["merge_role"] == "replacement":
        continue
    row = dict(r)
    if row["merge_role"] == "replacement":
        row["merge_role"] = "replacement_unmerged"
    merged.append(row)

LOCATION_COLS = [
    "postal_code", "outlet_type", "planning_area", "region", "neighborhood_type",
    "pa_population", "pa_area_sqkm", "pa_population_density", "n_outlets_at_postal",
    "shared_postal", "latitude", "longitude",
    "res_area_500m", "com_area_500m", "mixed_area_500m", "inst_area_500m", "open_area_500m", "hdb_blocks_500m", "rc_ratio_500m",
    "res_area_1000m", "com_area_1000m", "mixed_area_1000m", "inst_area_1000m", "open_area_1000m", "hdb_blocks_1000m", "rc_ratio_1000m",
    "res_area_1500m", "com_area_1500m", "mixed_area_1500m", "inst_area_1500m", "open_area_1500m", "hdb_blocks_1500m", "rc_ratio_1500m",
    "open_hours_daily", "hdb_proxy", "com_area_proxy",
]

for pc, grp in replacement_groups.items():
    grp_sorted = sorted(grp, key=lambda r: to_int(r["first_draw"]))
    latest = grp_sorted[-1]
    names = [r["outlet_name"] for r in grp_sorted]

    m = {c: latest.get(c, "") for c in LOCATION_COLS}
    m["outlet_name"] = latest["outlet_name"]
    m["merged_from"] = " | ".join(names)
    m["n_merged"] = len(grp_sorted)
    m["merge_group"] = pc
    m["merge_role"] = "replacement_merged"

    m["g1_wins_hist"] = sum(to_int(r["g1_wins_hist"]) for r in grp_sorted)
    m["g2_wins_hist"] = sum(to_int(r["g2_wins_hist"]) for r in grp_sorted)
    m["combined_wins_hist"] = sum(to_int(r["combined_wins_hist"]) for r in grp_sorted)
    m["first_draw"] = min(to_int(r["first_draw"]) for r in grp_sorted)
    m["last_draw"] = max(to_int(r["last_draw"]) for r in grp_sorted)
    m["draws_i"] = global_last - m["first_draw"] + 1
    m["is_closed"] = 1 if m["last_draw"] < global_last - 52 else 0
    merged.append(m)

for m in merged:
    m.setdefault("merged_from", m["outlet_name"])
    m.setdefault("n_merged", 1)
    for k in ("g1_wins_hist", "g2_wins_hist", "combined_wins_hist", "first_draw", "last_draw", "draws_i", "is_closed"):
        m[k] = to_int(m[k])
    m["hdb_proxy"] = to_float(m["hdb_proxy"])
    m["com_area_proxy"] = to_float(m["com_area_proxy"])

total_wins = sum(m["combined_wins_hist"] for m in merged)

sum_hdb = sum(m["hdb_proxy"] for m in merged) or 1.0
sum_com = sum(m["com_area_proxy"] for m in merged) or 1.0
com_scale = sum_com / sum_hdb
for m in merged:
    m["volume_proxy"] = m["hdb_proxy"] + (m["com_area_proxy"] / com_scale)

total_exp_hdb = sum(m["draws_i"] * m["hdb_proxy"] for m in merged if m["hdb_proxy"] > 0)
total_exp = sum(m["draws_i"] * m["volume_proxy"] for m in merged if m["volume_proxy"] > 0)

for m in merged:
    m["exposure_hdb"] = m["draws_i"] * m["hdb_proxy"]
    m["expected_wins_hdb"] = total_wins * (m["exposure_hdb"] / total_exp_hdb) if total_exp_hdb > 0 else 0.0

    m["exposure"] = m["draws_i"] * m["volume_proxy"]
    m["p_share"] = (m["exposure"] / total_exp) if total_exp > 0 else 0.0
    m["expected_wins"] = total_wins * m["p_share"]

    m["win_rate_per_draw"] = m["combined_wins_hist"] / m["draws_i"] if m["draws_i"] > 0 else 0.0
    m["win_share"] = m["combined_wins_hist"] / total_wins if total_wins > 0 else 0.0
    m["std_residual"] = (m["combined_wins_hist"] - m["expected_wins"]) / math.sqrt(m["expected_wins"]) if m["expected_wins"] > 0 else ""
    m["std_residual_hdb"] = (m["combined_wins_hist"] - m["expected_wins_hdb"]) / math.sqrt(m["expected_wins_hdb"]) if m["expected_wins_hdb"] > 0 else ""

fieldnames = [
    "outlet_name", "merged_from", "n_merged", "postal_code", "outlet_type", "planning_area", "region",
    "neighborhood_type", "pa_population", "pa_area_sqkm", "pa_population_density", "n_outlets_at_postal", "shared_postal", "merge_group", "merge_role", "latitude", "longitude",
    "res_area_500m", "com_area_500m", "mixed_area_500m", "inst_area_500m", "open_area_500m", "hdb_blocks_500m", "rc_ratio_500m",
    "res_area_1000m", "com_area_1000m", "mixed_area_1000m", "inst_area_1000m", "open_area_1000m", "hdb_blocks_1000m", "rc_ratio_1000m",
    "res_area_1500m", "com_area_1500m", "mixed_area_1500m", "inst_area_1500m", "open_area_1500m", "hdb_blocks_1500m", "rc_ratio_1500m",
    "open_hours_daily",
    "g1_wins_hist", "g2_wins_hist", "combined_wins_hist",
    "first_draw", "last_draw", "draws_i", "hdb_proxy", "com_area_proxy", "volume_proxy", "is_closed",
    "exposure", "p_share", "expected_wins", "win_rate_per_draw", "win_share", "std_residual",
    "exposure_hdb", "expected_wins_hdb", "std_residual_hdb",
]

merged.sort(key=lambda m: m["outlet_name"])
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for m in merged:
        w.writerow({k: m.get(k, "") for k in fieldnames})

n_merged_groups = len(replacement_groups)
n_collapsed = sum(len(g) for g in replacement_groups.values())
print(f"Wrote {OUT}")
print(f"  input outlets:  {len(rows)}")
print(f"  replacement groups merged: {n_merged_groups} ({n_collapsed} rows -> {n_merged_groups})")
print(f"  output outlets: {len(merged)}")
print(f"  total combined wins preserved: {total_wins} (source {sum(to_int(r['combined_wins_hist']) for r in rows)})")
