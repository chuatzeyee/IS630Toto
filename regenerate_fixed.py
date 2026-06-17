import csv
from pathlib import Path
import project as P

BASE = Path(__file__).parent
RAW = BASE / "data" / "raw"
DATA = BASE / "data"

with open(RAW / "outlets_list.csv", newline="", encoding="utf-8") as f:
    outlet_list = list(csv.DictReader(f))
with open(RAW / "outlets_with_addresses.csv", newline="", encoding="utf-8") as f:
    scraped_outlets = list(csv.DictReader(f))
with open(RAW / "gra_outlets.csv", newline="", encoding="utf-8") as f:
    gra_outlets = list(csv.DictReader(f))

print("[5] Merge (fixed)")
merged = P.step5_merge(outlet_list, scraped_outlets, gra_outlets)

print("[6] Reuse existing geocodes (no network)")
old_geo = {}
with open(DATA / "outlets_geocoded.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        old_geo[r["outlet_name"]] = r
old_geo_by_postal = {}
for r in old_geo.values():
    pc = (r.get("postal_code") or "").strip()
    if pc and pc not in old_geo_by_postal:
        old_geo_by_postal[pc] = r

geocoded = []
reused, missed = 0, 0
for o in merged:
    name = o["outlet_name"]
    g = old_geo.get(name) or old_geo_by_postal.get((o.get("postal_code") or "").strip())
    if g and (g.get("latitude") or "").strip() and g.get("geocode_status") == "OK":
        geocoded.append({
            **o,
            "latitude": g["latitude"], "longitude": g["longitude"],
            "onemap_address": g.get("onemap_address", ""),
            "planning_area": g.get("planning_area", ""),
            "x_svy21": g.get("x_svy21", ""), "y_svy21": g.get("y_svy21", ""),
            "geocode_status": "OK",
        })
        reused += 1
    else:
        geocoded.append({**o, "latitude": "", "longitude": "", "onemap_address": "",
                         "planning_area": "", "x_svy21": "", "y_svy21": "", "geocode_status": "FAILED"})
        missed += 1
print(f"    reused {reused} geocodes, {missed} without a cached geocode")

with open(DATA / "outlets_geocoded.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(geocoded[0].keys()))
    w.writeheader()
    w.writerows(geocoded)

print("[7] Extract centroids")
lu_centroids, hdb_blocks = P.step7_extract_centroids()
print("[8] Build geospatial profiles (+ population)")
outlets = P.step8_build_geodata(geocoded, lu_centroids, hdb_blocks)
print("[9] Earliest win years + authoritative win counts")
earliest, hist_counts = P.step9_earliest_win_years()
print("[10] Operating hours (cached)")
hours = P.step10_scrape_hours()
print("[11] Save + quality check")
P.step11_save(outlets, hours, earliest, hist_counts)
print("DONE")
