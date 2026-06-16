import csv
import math
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).parent
RAW = BASE / "data" / "raw" / "outlet_win_history.csv"
GEO = BASE / "data" / "analysis_ready" / "outlets_geodata.csv"
OUT = BASE / "data" / "analysis_ready" / "outlets_modeling.csv"
OUT_ENRICHED = BASE / "data" / "analysis_ready" / "win_history_enriched.csv"

EXCLUDE_SUBSTRINGS = ["account betting", "itoto"]


def is_real_outlet(name):
    low = name.lower()
    return not any(s in low for s in EXCLUDE_SUBSTRINGS)


wins = list(csv.DictReader(open(RAW, newline="", encoding="utf-8")))

g1 = defaultdict(int)
g2 = defaultdict(int)
first_draw = {}
last_draw = {}
global_last = 0

for r in wins:
    name = r["outlet_name"]
    if not is_real_outlet(name):
        continue
    if not r["draw_number"].isdigit():
        continue
    dn = int(r["draw_number"])
    global_last = max(global_last, dn)
    if r["prize_group"] == "1":
        g1[name] += 1
    elif r["prize_group"] == "2":
        g2[name] += 1
    if name not in first_draw or dn < first_draw[name]:
        first_draw[name] = dn
    if name not in last_draw or dn > last_draw[name]:
        last_draw[name] = dn

geo_rows = list(csv.DictReader(open(GEO, newline="", encoding="utf-8")))
geo_by_name = {r["outlet_name"]: r for r in geo_rows}

rows = []
for name in sorted(set(list(g1) + list(g2))):
    geo = geo_by_name.get(name, {})
    w1 = g1[name]
    w2 = g2[name]
    combined = w1 + w2

    draws_i = global_last - first_draw[name] + 1
    is_closed = 1 if last_draw[name] < global_last - 52 else 0

    try:
        hdb = float(geo.get("hdb_blocks_1000m", "") or 0)
    except ValueError:
        hdb = 0.0

    rows.append({
        "outlet_name": name,
        "postal_code": geo.get("postal_code", ""),
        "outlet_type": geo.get("outlet_type", ""),
        "planning_area": geo.get("planning_area", ""),
        "region": geo.get("region", ""),
        "neighborhood_type": geo.get("neighborhood_type", ""),
        "pa_population": geo.get("pa_population", ""),
        "n_outlets_at_postal": geo.get("n_outlets_at_postal", ""),
        "shared_postal": geo.get("shared_postal", ""),
        "latitude": geo.get("latitude", ""),
        "longitude": geo.get("longitude", ""),
        "res_area_500m": geo.get("res_area_500m", ""),
        "com_area_500m": geo.get("com_area_500m", ""),
        "mixed_area_500m": geo.get("mixed_area_500m", ""),
        "inst_area_500m": geo.get("inst_area_500m", ""),
        "open_area_500m": geo.get("open_area_500m", ""),
        "hdb_blocks_500m": geo.get("hdb_blocks_500m", ""),
        "rc_ratio_500m": geo.get("rc_ratio_500m", ""),
        "res_area_1000m": geo.get("res_area_1000m", ""),
        "com_area_1000m": geo.get("com_area_1000m", ""),
        "mixed_area_1000m": geo.get("mixed_area_1000m", ""),
        "inst_area_1000m": geo.get("inst_area_1000m", ""),
        "open_area_1000m": geo.get("open_area_1000m", ""),
        "hdb_blocks_1000m": geo.get("hdb_blocks_1000m", ""),
        "rc_ratio_1000m": geo.get("rc_ratio_1000m", ""),
        "res_area_1500m": geo.get("res_area_1500m", ""),
        "com_area_1500m": geo.get("com_area_1500m", ""),
        "mixed_area_1500m": geo.get("mixed_area_1500m", ""),
        "inst_area_1500m": geo.get("inst_area_1500m", ""),
        "open_area_1500m": geo.get("open_area_1500m", ""),
        "hdb_blocks_1500m": geo.get("hdb_blocks_1500m", ""),
        "rc_ratio_1500m": geo.get("rc_ratio_1500m", ""),
        "open_hours_daily": geo.get("open_hours_daily", ""),
        "g1_wins_hist": w1,
        "g2_wins_hist": w2,
        "combined_wins_hist": combined,
        "first_draw": first_draw[name],
        "last_draw": last_draw[name],
        "draws_i": draws_i,
        "hdb_proxy": hdb,
        "is_closed": is_closed,
    })

total_wins = sum(r["combined_wins_hist"] for r in rows)

eligible = [r for r in rows if r["hdb_proxy"] > 0]
total_exposure = sum(r["draws_i"] * r["hdb_proxy"] for r in eligible)

for r in rows:
    r["exposure"] = r["draws_i"] * r["hdb_proxy"]
    r["p_share"] = (r["exposure"] / total_exposure) if total_exposure > 0 else 0.0
    r["expected_wins"] = total_wins * r["p_share"]
    r["win_rate_per_draw"] = r["combined_wins_hist"] / r["draws_i"] if r["draws_i"] > 0 else 0.0
    r["win_share"] = r["combined_wins_hist"] / total_wins if total_wins > 0 else 0.0
    if r["expected_wins"] > 0:
        r["std_residual"] = (r["combined_wins_hist"] - r["expected_wins"]) / math.sqrt(r["expected_wins"])
    else:
        r["std_residual"] = ""

fieldnames = [
    "outlet_name", "postal_code", "outlet_type", "planning_area", "region",
    "neighborhood_type", "pa_population", "n_outlets_at_postal", "shared_postal", "latitude", "longitude",
    "res_area_500m", "com_area_500m", "mixed_area_500m", "inst_area_500m", "open_area_500m", "hdb_blocks_500m", "rc_ratio_500m",
    "res_area_1000m", "com_area_1000m", "mixed_area_1000m", "inst_area_1000m", "open_area_1000m", "hdb_blocks_1000m", "rc_ratio_1000m",
    "res_area_1500m", "com_area_1500m", "mixed_area_1500m", "inst_area_1500m", "open_area_1500m", "hdb_blocks_1500m", "rc_ratio_1500m",
    "open_hours_daily",
    "g1_wins_hist", "g2_wins_hist", "combined_wins_hist",
    "first_draw", "last_draw", "draws_i", "hdb_proxy", "is_closed",
    "exposure", "p_share", "expected_wins", "win_rate_per_draw", "win_share", "std_residual",
]

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in fieldnames})

# --- Enriched per-win-record file: each winning record joined to its outlet's modeling columns ---
model_by_name = {r["outlet_name"]: r for r in rows}
win_fields = ["draw_date", "draw_number", "prize_amount", "bet_type", "prize_group"]
attach_fields = [c for c in fieldnames if c != "outlet_name"]
enriched_fields = ["outlet_name"] + win_fields + attach_fields

enriched_count = 0
with open(OUT_ENRICHED, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=enriched_fields)
    w.writeheader()
    for rec in wins:
        name = rec["outlet_name"]
        if not is_real_outlet(name) or name not in model_by_name:
            continue
        m = model_by_name[name]
        out_row = {"outlet_name": name}
        for k in win_fields:
            out_row[k] = rec.get(k, "")
        for k in attach_fields:
            out_row[k] = m.get(k, "")
        w.writerow(out_row)
        enriched_count += 1

print(f"Wrote {OUT} with {len(rows)} outlets, {len(fieldnames)} columns")
print(f"Wrote {OUT_ENRICHED} with {enriched_count} win records, {len(enriched_fields)} columns")
print(f"Total combined wins (from win history): {total_wins}")
print(f"Global last draw number: {global_last}")
print(f"Outlets with HDB proxy = 0 (excluded from exposure): {sum(1 for r in rows if r['hdb_proxy'] == 0)}")
print(f"Outlets flagged closed (no win in last ~year): {sum(1 for r in rows if r['is_closed'] == 1)}")
