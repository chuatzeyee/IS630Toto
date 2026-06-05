#!/usr/bin/env python3

import csv
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SUPP_DIR = DATA_DIR / "supplementary"
OUT_DIR = DATA_DIR / "analysis_ready"
OUT_DIR.mkdir(parents=True, exist_ok=True)

API_HEADERS = {"User-Agent": "SMU-IS630-Project/1.0"}

GEODATASETS = [
    {
        "name": "URA Master Plan 2019 Land Use",
        "dataset_id": "d_90d86daa5bfaa371668b84fa5f01424f",
        "filename": "master_plan_land_use.geojson",
    },
    {
        "name": "HDB Existing Building",
        "dataset_id": "d_16b157c52ed637edd6ba1232e026258d",
        "filename": "hdb_existing_building.geojson",
    },
]

RADII = [500, 1000, 1500]

LU_CATEGORY = {
    "RESIDENTIAL": "residential",
    "RESIDENTIAL / INSTITUTION": "residential",
    "RESIDENTIAL WITH COMMERCIAL AT 1ST STOREY": "residential",
    "COMMERCIAL & RESIDENTIAL": "mixed",
    "COMMERCIAL": "commercial",
    "COMMERCIAL / INSTITUTION": "commercial",
    "HOTEL": "commercial",
    "BUSINESS 1": "commercial",
    "BUSINESS 1 - WHITE": "commercial",
    "BUSINESS 2": "commercial",
    "BUSINESS 2 - WHITE": "commercial",
    "BUSINESS PARK": "commercial",
    "BUSINESS PARK - WHITE": "commercial",
    "CIVIC & COMMUNITY INSTITUTION": "institutional",
    "EDUCATIONAL INSTITUTION": "institutional",
    "PLACE OF WORSHIP": "institutional",
    "HEALTH & MEDICAL CARE": "institutional",
    "OPEN SPACE": "open",
    "PARK": "open",
    "SPORTS & RECREATION": "open",
    "BEACH AREA": "open",
    "ROAD": "infrastructure",
    "TRANSPORT FACILITIES": "infrastructure",
    "LIGHT RAPID TRANSIT": "infrastructure",
    "MASS RAPID TRANSIT": "infrastructure",
    "UTILITY": "infrastructure",
    "WATERBODY": "infrastructure",
    "PORT / AIRPORT": "infrastructure",
    "RESERVE SITE": "other",
    "SPECIAL USE": "other",
    "WHITE": "other",
    "AGRICULTURE": "other",
    "CEMETERY": "other",
}


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def polygon_centroid(geom):
    coords = geom["coordinates"]
    pts = []
    if geom["type"] == "Polygon":
        pts = coords[0]
    elif geom["type"] == "MultiPolygon":
        for poly in coords:
            pts.extend(poly[0])
    if not pts:
        return None, None
    return sum(p[1] for p in pts) / len(pts), sum(p[0] for p in pts) / len(pts)


def download_if_missing(dataset_id, output_path):
    if output_path.exists():
        print(f"  [SKIP] {output_path.name} ({output_path.stat().st_size:,} bytes)")
        return True
    print(f"  Downloading {output_path.name}...")
    poll_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/poll-download"
    try:
        req = Request(poll_url, headers=API_HEADERS)
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            dl_url = data.get("data", {}).get("url")
            if dl_url:
                with urlopen(Request(dl_url, headers=API_HEADERS), timeout=600) as dl:
                    content = dl.read()
                    with open(output_path, "wb") as f:
                        f.write(content)
                    print(f"  Saved ({len(content):,} bytes)")
                    return True
    except (HTTPError, URLError) as e:
        print(f"  Failed: {e}")
    print(f"  [MANUAL] https://data.gov.sg/datasets/{dataset_id}/view")
    return False


def extract_land_use_centroids():
    cache = SUPP_DIR / "land_use_centroids.csv"
    if cache.exists():
        centroids = []
        with open(cache, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                centroids.append((
                    row["lu_category"],
                    float(row["latitude"]),
                    float(row["longitude"]),
                    float(row["area_sqm"]),
                ))
        print(f"  Loaded {len(centroids)} cached land use centroids")
        return centroids

    src = SUPP_DIR / "master_plan_land_use.geojson"
    print(f"  Parsing {src.name} (~166MB)...")
    with open(src, encoding="utf-8") as f:
        gj = json.load(f)

    centroids = []
    for feature in gj["features"]:
        props = feature["properties"]
        lu_desc = (props.get("LU_DESC") or "").strip()
        area = float(props.get("SHAPE.AREA", 0) or 0)
        cat = LU_CATEGORY.get(lu_desc, "other")
        geom = feature.get("geometry")
        if geom is None:
            continue
        lat, lon = polygon_centroid(geom)
        if lat is None:
            continue
        centroids.append((cat, lat, lon, area))

    with open(cache, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["lu_category", "latitude", "longitude", "area_sqm"])
        for cat, lat, lon, area in centroids:
            w.writerow([cat, lat, lon, area])

    print(f"  Extracted {len(centroids)} centroids -> {cache.name}")
    del gj
    return centroids


def extract_hdb_block_centroids():
    cache = SUPP_DIR / "hdb_block_centroids.csv"
    if cache.exists():
        blocks = []
        with open(cache, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                blocks.append((float(row["latitude"]), float(row["longitude"])))
        print(f"  Loaded {len(blocks)} cached HDB block centroids")
        return blocks

    src = SUPP_DIR / "hdb_existing_building.geojson"
    print(f"  Parsing {src.name} (~54MB)...")
    with open(src, encoding="utf-8") as f:
        gj = json.load(f)

    blocks = []
    for feature in gj["features"]:
        geom = feature.get("geometry")
        if geom is None:
            continue
        lat, lon = polygon_centroid(geom)
        if lat is None:
            continue
        blocks.append((lat, lon))

    with open(cache, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["latitude", "longitude"])
        for lat, lon in blocks:
            w.writerow([lat, lon])

    print(f"  Extracted {len(blocks)} block centroids -> {cache.name}")
    del gj
    return blocks


def load_pa_regions():
    path = SUPP_DIR / "planning_area_boundary.geojson"
    if not path.exists():
        return {}, {}
    with open(path, encoding="utf-8") as f:
        gj = json.load(f)
    centroids = {}
    regions = {}
    for feature in gj["features"]:
        props = feature["properties"]
        name = props["PLN_AREA_N"]
        regions[name] = props["REGION_N"]
        geom = feature.get("geometry")
        if geom:
            lat, lon = polygon_centroid(geom)
            if lat is not None:
                centroids[name] = (lat, lon)
    return centroids, regions


def compute_profiles(outlets, lu_centroids, hdb_blocks):
    max_r = max(RADII)
    deg_box = max_r / 111320.0 * 1.15

    for idx, outlet in enumerate(outlets):
        olat = outlet["latitude"]
        olon = outlet["longitude"]

        nearby_lu = [
            (cat, clat, clon, area)
            for cat, clat, clon, area in lu_centroids
            if abs(clat - olat) <= deg_box and abs(clon - olon) <= deg_box
        ]
        lu_dists = [
            (cat, area, haversine_m(olat, olon, clat, clon))
            for cat, clat, clon, area in nearby_lu
        ]

        nearby_hdb = [
            haversine_m(olat, olon, blat, blon)
            for blat, blon in hdb_blocks
            if abs(blat - olat) <= deg_box and abs(blon - olon) <= deg_box
        ]

        for radius in RADII:
            area_by_cat = defaultdict(float)
            for cat, area, dist in lu_dists:
                if dist <= radius:
                    area_by_cat[cat] += area

            outlet[f"res_area_{radius}m"] = round(area_by_cat.get("residential", 0))
            outlet[f"com_area_{radius}m"] = round(area_by_cat.get("commercial", 0))
            outlet[f"mixed_area_{radius}m"] = round(area_by_cat.get("mixed", 0))
            outlet[f"inst_area_{radius}m"] = round(area_by_cat.get("institutional", 0))
            outlet[f"open_area_{radius}m"] = round(area_by_cat.get("open", 0))
            outlet[f"hdb_blocks_{radius}m"] = sum(1 for d in nearby_hdb if d <= radius)

            res_total = area_by_cat.get("residential", 0) + area_by_cat.get("mixed", 0) * 0.5
            com_total = area_by_cat.get("commercial", 0) + area_by_cat.get("mixed", 0) * 0.5
            denom = res_total + com_total
            outlet[f"rc_ratio_{radius}m"] = round(res_total / denom, 4) if denom > 0 else 0.5

        rc = outlet["rc_ratio_1000m"]
        hdb = outlet["hdb_blocks_1000m"]
        if rc >= 0.65 and hdb >= 5:
            outlet["neighborhood_type"] = "residential"
        elif rc <= 0.35:
            outlet["neighborhood_type"] = "commercial"
        else:
            outlet["neighborhood_type"] = "mixed"

        areas_1000 = {
            "residential": outlet["res_area_1000m"],
            "commercial": outlet["com_area_1000m"],
            "mixed": outlet["mixed_area_1000m"],
            "institutional": outlet["inst_area_1000m"],
            "open": outlet["open_area_1000m"],
        }
        outlet["dominant_landuse_1000m"] = max(areas_1000, key=areas_1000.get) if any(areas_1000.values()) else "unknown"

        outlet["landuse_diversity_1000m"] = sum(1 for v in areas_1000.values() if v > 0)

        if (idx + 1) % 50 == 0 or idx == 0:
            print(f"  [{idx+1}/{len(outlets)}] computed...")


def main():
    print("=" * 70)
    print("  Geospatial Analysis -- Land Use Profiling for TOTO Outlets")
    print("=" * 70)
    start = time.time()

    print("\n[Step 1] Download geospatial datasets")
    for ds in GEODATASETS:
        download_if_missing(ds["dataset_id"], SUPP_DIR / ds["filename"])

    print("\n[Step 2a] Extract land use centroids")
    lu_centroids = extract_land_use_centroids()

    print("\n[Step 2b] Extract HDB block centroids")
    hdb_blocks = extract_hdb_block_centroids()

    print("\n[Step 2c] Load planning area boundaries")
    pa_centroids, pa_regions = load_pa_regions()
    print(f"  {len(pa_centroids)} planning areas, {len(set(pa_regions.values()))} regions")

    print("\n[Step 3] Load geocoded outlets")
    input_path = DATA_DIR / "outlets_geocoded.csv"
    if not input_path.exists():
        print(f"  [ERROR] {input_path} not found. Run build_dataset.py first.")
        sys.exit(1)

    with open(input_path, newline="", encoding="utf-8") as f:
        raw = list(csv.DictReader(f))

    outlets = []
    for o in raw:
        if o.get("geocode_status") != "OK":
            continue
        try:
            lat = float(o["latitude"])
            lon = float(o["longitude"])
        except (ValueError, KeyError):
            continue

        pa = (o.get("planning_area") or "").strip().upper()
        if not pa:
            best_pa, best_d = "", float("inf")
            for name, (clat, clon) in pa_centroids.items():
                d = haversine_m(lat, lon, clat, clon)
                if d < best_d:
                    best_d = d
                    best_pa = name
            if best_pa and best_d < 5000:
                pa = best_pa

        outlets.append({
            "outlet_name": o["outlet_name"],
            "postal_code": o.get("postal_code", ""),
            "outlet_type": o.get("outlet_type", ""),
            "group1_wins": int(o.get("group1_wins", 0)),
            "group2_wins": int(o.get("group2_wins", 0)),
            "combined_wins": int(o.get("combined_wins", 0)),
            "source": o.get("source", ""),
            "latitude": lat,
            "longitude": lon,
            "onemap_address": o.get("onemap_address", ""),
            "planning_area": pa,
            "region": pa_regions.get(pa, ""),
            "geocode_status": "OK",
        })

    print(f"  {len(outlets)} geocoded outlets loaded")

    print(f"\n[Step 4] Compute land use profiles at {RADII}m radii")
    print(f"  {len(lu_centroids)} land use polygons + {len(hdb_blocks)} HDB blocks")
    compute_profiles(outlets, lu_centroids, hdb_blocks)

    print("\n[Step 5] Compute win rates")
    for outlet in outlets:
        hdb = outlet["hdb_blocks_1000m"]
        wins = outlet["combined_wins"]
        outlet["win_rate_hdb_1000m"] = round(wins / hdb, 6) if hdb > 0 and wins > 0 else 0.0

    output_path = OUT_DIR / "outlets_geodata.csv"
    fieldnames = [
        "outlet_name", "postal_code", "outlet_type",
        "group1_wins", "group2_wins", "combined_wins", "source",
        "latitude", "longitude", "onemap_address", "planning_area", "region",
        "geocode_status",
        "res_area_500m", "com_area_500m", "mixed_area_500m",
        "inst_area_500m", "open_area_500m", "hdb_blocks_500m", "rc_ratio_500m",
        "res_area_1000m", "com_area_1000m", "mixed_area_1000m",
        "inst_area_1000m", "open_area_1000m", "hdb_blocks_1000m", "rc_ratio_1000m",
        "res_area_1500m", "com_area_1500m", "mixed_area_1500m",
        "inst_area_1500m", "open_area_1500m", "hdb_blocks_1500m", "rc_ratio_1500m",
        "neighborhood_type", "dominant_landuse_1000m", "landuse_diversity_1000m",
        "win_rate_hdb_1000m",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(outlets)

    res_ct = sum(1 for o in outlets if o["neighborhood_type"] == "residential")
    com_ct = sum(1 for o in outlets if o["neighborhood_type"] == "commercial")
    mix_ct = sum(1 for o in outlets if o["neighborhood_type"] == "mixed")

    def avg_wins(lst):
        return sum(o["combined_wins"] for o in lst) / len(lst) if lst else 0

    def med_wins(lst):
        if not lst:
            return 0
        vals = sorted(o["combined_wins"] for o in lst)
        n = len(vals)
        return vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2

    res_out = [o for o in outlets if o["neighborhood_type"] == "residential"]
    com_out = [o for o in outlets if o["neighborhood_type"] == "commercial"]
    mix_out = [o for o in outlets if o["neighborhood_type"] == "mixed"]

    dom_counts = defaultdict(int)
    for o in outlets:
        dom_counts[o["dominant_landuse_1000m"]] += 1

    print(f"\n{'='*70}")
    print(f"  RESULTS")
    print(f"{'='*70}")
    print(f"  Total outlets:  {len(outlets)}")
    print(f"  Residential:    {res_ct}")
    print(f"  Commercial:     {com_ct}")
    print(f"  Mixed:          {mix_ct}")
    print(f"  Dominant LU:    {dict(dom_counts)}")
    print(f"\n  Average combined wins by neighborhood:")
    print(f"    Residential:  {avg_wins(res_out):.1f} (median {med_wins(res_out):.0f}, n={len(res_out)})")
    print(f"    Commercial:   {avg_wins(com_out):.1f} (median {med_wins(com_out):.0f}, n={len(com_out)})")
    print(f"    Mixed:        {avg_wins(mix_out):.1f} (median {med_wins(mix_out):.0f}, n={len(mix_out)})")

    print(f"\n  Top 10 by combined wins:")
    top10 = sorted(outlets, key=lambda x: x["combined_wins"], reverse=True)[:10]
    for i, o in enumerate(top10, 1):
        print(f"    {i:2d}. {o['outlet_name'][:30]:<30s}  wins={o['combined_wins']:>4d}  "
              f"rc={o['rc_ratio_1000m']:.2f}  hdb={o['hdb_blocks_1000m']:>3d}  {o['neighborhood_type']}")

    print(f"\n  Correlation hints (Pearson r):")
    n = len(outlets)
    wins = [o["combined_wins"] for o in outlets]
    mean_w = sum(wins) / n
    for col in ["hdb_blocks_1000m", "res_area_1000m", "com_area_1000m", "rc_ratio_1000m"]:
        vals = [o[col] for o in outlets]
        mean_v = sum(vals) / n
        cov = sum((w - mean_w) * (v - mean_v) for w, v in zip(wins, vals)) / n
        std_w = (sum((w - mean_w) ** 2 for w in wins) / n) ** 0.5
        std_v = (sum((v - mean_v) ** 2 for v in vals) / n) ** 0.5
        r = cov / (std_w * std_v) if std_w > 0 and std_v > 0 else 0
        print(f"    combined_wins vs {col}: r = {r:.4f}")

    elapsed = time.time() - start
    print(f"\n  Saved to: {output_path}")
    print(f"  Completed in {elapsed:.0f}s")


if __name__ == "__main__":
    main()
