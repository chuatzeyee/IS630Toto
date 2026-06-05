import csv
import json
import math
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).parent # change for .py file
#BASE_DIR = Path.cwd() # change for ipynb
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
SUPP_DIR = DATA_DIR / "supplementary"
OUT_DIR = DATA_DIR / "analysis_ready"

RAW_DIR.mkdir(parents=True, exist_ok=True)
SUPP_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

ONEMAP_SEARCH_URL = "https://www.onemap.gov.sg/api/common/elastic/search"

API_HEADERS = {"User-Agent": "SMU-IS630-Project/1.0"}

SUPPLEMENTARY_DATASETS = [
    {
        "name": "URA Master Plan 2019 Planning Area Boundary (No Sea)",
        "dataset_id": "d_4765db0e87b9c86336792efe8a1f7a66",
        "filename": "planning_area_boundary.geojson",
    },
    {
        "name": "HDB Existing Building (Block-level GeoJSON)",
        "dataset_id": "d_16b157c52ed637edd6ba1232e026258d",
        "filename": "HDBExistingBuilding.geojson",
    },
]

HAVERSINE_RADII_M = [500, 750, 1000, 1500]

def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def step4_download_supplementary() -> int:
    success = 0
    for ds in SUPPLEMENTARY_DATASETS:
        output_path = SUPP_DIR / ds["filename"]
        if output_path.exists():
            print(f"{ds['filename']} already exists ({output_path.stat().st_size:,} bytes)")
            success += 1
            continue

        print(f"Downloading {ds['name']}")
        time.sleep(2)
        dataset_id = ds["dataset_id"]
        downloaded = False

        poll_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/poll-download"
        req = Request(poll_url, headers=API_HEADERS)
        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                download_url = data.get("data", {}).get("url")
                if download_url:
                    dl_req = Request(download_url, headers=API_HEADERS)
                    with urlopen(dl_req, timeout=60) as dl_resp:
                        content = dl_resp.read()
                        with open(output_path, "wb") as f:
                            f.write(content)
                        print(f"Saved {ds['filename']} ({len(content):,} bytes)")
                        downloaded = True
        except (HTTPError, URLError, json.JSONDecodeError):
            pass

        if not downloaded:
            initiate_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/initiate-download"
            req = Request(
                initiate_url,
                headers={**API_HEADERS, "Content-Type": "application/json"},
                data=b'{}',
                method="POST",
            )
            try:
                with urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                    download_url = data.get("data", {}).get("url")
                    if download_url:
                        dl_req = Request(download_url, headers=API_HEADERS)
                        with urlopen(dl_req, timeout=60) as dl_resp:
                            content = dl_resp.read()
                            with open(output_path, "wb") as f:
                                f.write(content)
                            print(f"    Saved {ds['filename']} ({len(content):,} bytes)")
                            downloaded = True
            except (HTTPError, URLError, json.JSONDecodeError):
                pass

        if downloaded:
            success += 1
        else:
            print(f"    [MANUAL] https://data.gov.sg/datasets/{dataset_id}/view -> save as {ds['filename']}")

    print(f"Downloaded: {success}/{len(SUPPLEMENTARY_DATASETS)}")
    return success


def build_hdb_block_centroids(geojson_path):
    output_path = SUPP_DIR / "hdb_blocks.csv"
    if output_path.exists():
        print(f"hdb_blocks.csv already exists, skipping")
        return
    
    with open(geojson_path, encoding="utf-8") as f:
        gj = json.load(f)

    blocks = {}
    for feature in gj["features"]:
        postal = feature["properties"].get("POSTAL_COD", "").strip()
        if not postal or postal == "NIL":
            continue

        geom = feature["geometry"]
        if geom["type"] == "Polygon":
            coords = geom["coordinates"][0]
        elif geom["type"] == "MultiPolygon":
            coords = geom["coordinates"][0][0]  # first polygon, exterior ring
        else:
            continue
        avg_lon = sum(p[0] for p in coords) / len(coords)
        avg_lat = sum(p[1] for p in coords) / len(coords)

        blocks[postal] = {"postal_code": postal, "latitude": avg_lat, "longitude": avg_lon}

    result = list(blocks.values())
    print(f"Unique postal codes: {len(result)}")

    with open(SUPP_DIR / "hdb_blocks.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["postal_code", "latitude", "longitude"])
        writer.writeheader()
        writer.writerows(result)

    print(f"Saved {len(blocks)} blocks to hdb_blocks.csv")
    return result



def step5_merge() -> list[dict]:
    output_path = DATA_DIR / "outlets_raw.csv"

    def load_csv(path: Path) -> list[dict]:
        if not path.exists():
            return []
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    outlet_list     = load_csv(RAW_DIR / "outlets_list.csv")
    scraped_outlets = load_csv(RAW_DIR / "outlets_with_addresses.csv")
    gra_outlets     = load_csv(RAW_DIR / "gra_outlets.csv")

    print(f"Sources: aggregate={len(outlet_list)}, scraped={len(scraped_outlets)}, GRA={len(gra_outlets)}")

    scraped_by_name = {s["outlet_name"].strip(): s for s in scraped_outlets}
    gra_by_postal   = {g["postal_code"].strip(): g for g in gra_outlets if re.match(r'^\d{6}$', g.get("postal_code", "").strip())}

    merged           = {}
    used_gra_postals = set()

    #get outlet type from gra list based on postal code match
    for o in outlet_list:
        name   = o["outlet_name"].strip()
        postal = scraped_by_name.get(name, {}).get("postal_code", "").strip()
        gra    = gra_by_postal.get(postal, {})

        if gra:
            used_gra_postals.add(postal)

        merged[name] = {
            "outlet_name":   name,
            "postal_code":   postal,
            "outlet_type":   gra.get("outlet_type", ""),
            "group1_wins":   int(o.get("group1_wins", 0)),
            "group2_wins":   int(o.get("group2_wins", 0)),
            "combined_wins": int(o.get("group1_wins", 0)) + int(o.get("group2_wins", 0)),
            "source":        "matched" if gra else "scraped",
        }

    # add GRA outlets that never appeared in the wins list
    for g in gra_outlets:
        gp    = g.get("postal_code", "").strip()
        gname = g.get("outlet_name", "").strip()[:80]
        if gp in used_gra_postals or not gname:
            continue
        merged[gname] = {
            "outlet_name":   gname,
            "postal_code":   gp,
            "outlet_type":   g.get("outlet_type", ""),
            "group1_wins":   0,
            "group2_wins":   0,
            "combined_wins": 0,
            "source":        "gra_only",
        }

    physical = [
        o for o in merged.values()
        if "account betting" not in o["outlet_name"].lower()
        and "itoto"          not in o["outlet_name"].lower()
    ]

    fields = ["outlet_name", "postal_code", "outlet_type",
              "group1_wins", "group2_wins", "combined_wins", "source"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(physical)

    print(f"Merged {len(physical)} physical outlets to {output_path}")
    return physical

# 4 postal codes not found in OneMap APIs. Manually filled
MANUAL_GEOCODES = {
    "Singapore Pools Choa Chu Kang Branch": {"latitude": 1.3846968155873416, "longitude": 103.74378458764835, "planning_area": "CHOA CHU KANG"},
    "Singapore Pools Woodlands Centre":     {"latitude": 1.443578459984722, "longitude": 103.77085901032147, "planning_area": "WOODLANDS"},
    "Singapore Pools Rochor Centre Branch": {"latitude": 1.3052787317021182, "longitude": 103.85491101759817, "planning_area": "ROCHOR"},
    "Cheers Woodlands Centre":              {"latitude": 1.4416756560120672, "longitude": 103.77002767602397, "planning_area": "WOODLANDS"},
}


    
def step6_geocode() -> list[dict]:
    input_path  = DATA_DIR / "outlets_raw.csv"
    output_path = DATA_DIR / "outlets_geocoded.csv"

    if output_path.exists():
        print(f"outlets_geocoded.csv already exists, skipping")
        with open(output_path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    
    with open(input_path, newline="", encoding="utf-8") as f:
        outlets = list(csv.DictReader(f))

    print(f"Geocoding {len(outlets)} outlets...")
    geocoded = []

    for i, outlet in enumerate(outlets):
        name   = outlet.get("outlet_name", "").strip()
        postal = outlet.get("postal_code", "").strip()

        # manual override for outlets OneMap can't find
        if name in MANUAL_GEOCODES:
            m = MANUAL_GEOCODES[name]
            geocoded.append({
                **outlet,
                "latitude":       m["latitude"],
                "longitude":      m["longitude"],
                "onemap_address": "manual",
                "planning_area":  m["planning_area"],
                "x_svy21": "", "y_svy21": "",
                "geocode_status": "OK",
            })
            continue

        # postal code lookup
        result = None
        if postal and len(postal) == 6 and postal.isdigit():
            url = f"{ONEMAP_SEARCH_URL}?searchVal={postal}&returnGeom=Y&getAddrDetails=Y"
            req = Request(url, headers=API_HEADERS)
            for attempt in range(3):
                try:
                    with urlopen(req, timeout=30) as resp:
                        data = json.loads(resp.read().decode())
                        if data.get("found", 0) > 0:
                            r      = data["results"][0]
                        result = {
                            "latitude":       float(r["LATITUDE"]),
                            "longitude":      float(r["LONGITUDE"]),
                            "onemap_address": r.get("ADDRESS", ""),
                            "x_svy21":        float(r.get("X", 0)),
                            "y_svy21":        float(r.get("Y", 0)),
                        }
                    break
                except (URLError, TimeoutError):
                    time.sleep(2)

        # planning area lookup
        planning_area = ""

        if result:
            geocoded.append({
                **outlet,
                "latitude":       result["latitude"],
                "longitude":      result["longitude"],
                "onemap_address": result["onemap_address"],
                "planning_area":  planning_area,
                "x_svy21":        result["x_svy21"],
                "y_svy21":        result["y_svy21"],
                "geocode_status": "OK",
            })
        else:
            print(f"FAILED: {name} | postal: {postal}")
            geocoded.append({
                **outlet,
                "latitude": "", "longitude": "", "onemap_address": "",
                "planning_area": "", "x_svy21": "", "y_svy21": "",
                "geocode_status": "FAILED",
            })

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(outlets)}] geocoded...")

        time.sleep(1.0)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(geocoded[0].keys()))
        writer.writeheader()
        writer.writerows(geocoded)

    ok = sum(1 for r in geocoded if r["geocode_status"] == "OK")
    print(f"Geocoded: {ok} OK, {len(geocoded) - ok} failed out of {len(geocoded)}")
    return geocoded

COMMERCIAL_PLANNING_AREAS = {
    "DOWNTOWN CORE", "MARINA SOUTH", "MUSEUM", "OUTRAM", "RIVER VALLEY",
    "ROCHOR", "ORCHARD", "NEWTON", "SINGAPORE RIVER", "MARINA EAST",
    "STRAITS VIEW", "SOUTHERN ISLANDS",
}

def classify_area_type(planning_area: str) -> str:
    if planning_area.upper() in COMMERCIAL_PLANNING_AREAS:
        return "commercial"
    return "residential"



def step7_build_final(geocoded_outlets: list[dict]) -> None:
    output_path    = OUT_DIR / "outlets_final.csv"
    geojson_path   = SUPP_DIR / "planning_area_boundary.geojson"
    hdb_blocks_path = SUPP_DIR / "hdb_blocks.csv"

    if not geojson_path.exists():
        print(f"{geojson_path} not found.")
        return

    # --- Load planning area boundaries ---
    with open(geojson_path, encoding="utf-8") as f:
        geojson = json.load(f)

    pa_centroids: dict[str, tuple[float, float]] = {}
    pa_regions:   dict[str, str]                 = {}

    for feature in geojson["features"]:
        props   = feature["properties"]
        pa_name = props["PLN_AREA_N"]
        region  = props["REGION_N"]
        pa_regions[pa_name] = region

        geom       = feature["geometry"]
        all_points = []
        if geom["type"] == "Polygon":
            all_points = geom["coordinates"][0]
        elif geom["type"] == "MultiPolygon":
            for polygon in geom["coordinates"]:
                all_points.extend(polygon[0])

        if all_points:
            avg_lon = sum(p[0] for p in all_points) / len(all_points)
            avg_lat = sum(p[1] for p in all_points) / len(all_points)
            pa_centroids[pa_name] = (avg_lat, avg_lon)

    print(f"Loaded {len(pa_centroids)} planning area centroids")

    # --- Load HDB block centroids ---
    def load_hdb_blocks(path: Path) -> list[tuple[float, float]]:
        blocks = []
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                blocks.append((float(row["latitude"]), float(row["longitude"])))
        print(f"Loaded {len(blocks)} HDB blocks from {path.name}")
        return blocks

    hdb_blocks = load_hdb_blocks(hdb_blocks_path)

    # --- Filter to valid geocoded outlets ---
    valid_outlets = []
    for o in geocoded_outlets:
        if o.get("geocode_status") != "OK":
            continue
        lat = float(o["latitude"])
        lon = float(o["longitude"])
        valid_outlets.append({
            "outlet_name":    o["outlet_name"],
            "postal_code":    o.get("postal_code", ""),
            "outlet_type":    o.get("outlet_type", ""),
            "group1_wins":    int(o.get("group1_wins", 0)),
            "group2_wins":    int(o.get("group2_wins", 0)),
            "combined_wins":  int(o.get("combined_wins", 0)),
            "source":         o.get("source", ""),
            "latitude":       lat,
            "longitude":      lon,
            "onemap_address": o.get("onemap_address", ""),
            "planning_area":  o.get("planning_area", ""),
            "x_svy21":        o.get("x_svy21", ""),
            "y_svy21":        o.get("y_svy21", ""),
            "geocode_status": "OK",
        })

    # --- Assign planning area via nearest centroid where missing ---
    pa_assign_count = 0
    for outlet in valid_outlets:
        pa = outlet["planning_area"].strip().upper()
        if not pa:
            best_pa, best_dist = "", float("inf")
            for pa_name, (clat, clon) in pa_centroids.items():
                d = haversine_m(outlet["latitude"], outlet["longitude"], clat, clon)
                if d < best_dist:
                    best_dist = d
                    best_pa   = pa_name
            if best_pa and best_dist < 5000:
                outlet["planning_area"] = best_pa
                pa_assign_count += 1

    print(f"Assigned planning area via nearest centroid for {pa_assign_count} outlets")

    # --- Assign region ---
    for outlet in valid_outlets:
        outlet["region"] = pa_regions.get(outlet["planning_area"].upper(), "")

    # --- Classify area type based on planning area ---
    print("Classifying area types...")
    for outlet in valid_outlets:
        outlet["area_type"] = classify_area_type(outlet["planning_area"])

    # --- Compute HDB block count proxy at multiple radii ---
    print(f"Computing HDB block proxy at radii: {HAVERSINE_RADII_M}m")
    for idx, outlet in enumerate(valid_outlets):
        olat = outlet["latitude"]
        olon = outlet["longitude"]
        for radius in HAVERSINE_RADII_M:
            outlet[f"proxy_{radius}m"] = sum(
                1 for (blat, blon) in hdb_blocks
                if haversine_m(olat, olon, blat, blon) <= radius
            )
        if (idx + 1) % 50 == 0:
            print(f"  [{idx+1}/{len(valid_outlets)}] proxy computed...")

    # --- Win rate ---
    for outlet in valid_outlets:
        proxy_1000 = outlet.get("proxy_1000m", 0)
        combined   = outlet["combined_wins"]
        outlet["win_rate_1000m"] = round(combined / proxy_1000, 8) if proxy_1000 > 0 and combined > 0 else 0.0

    # --- Write output ---
    fieldnames = [
        "outlet_name", "postal_code", "outlet_type",
        "group1_wins", "group2_wins", "combined_wins", "source",
        "latitude", "longitude", "onemap_address", "planning_area",
        "x_svy21", "y_svy21", "geocode_status",
        "proxy_500m", "proxy_750m", "proxy_1000m", "proxy_1500m",
        "area_type", "region", "win_rate_1000m",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(valid_outlets)

    # --- Summary ---
    residential_count = sum(1 for o in valid_outlets if o["area_type"] == "residential")
    commercial_count  = sum(1 for o in valid_outlets if o["area_type"] == "commercial")
    with_proxy        = sum(1 for o in valid_outlets if o["proxy_1000m"] > 0)
    regions           = defaultdict(int)
    for o in valid_outlets:
        if o["region"]:
            regions[o["region"]] += 1

    print(f"\nSummary")
    print(f"Total outlets    : {len(valid_outlets)}")
    print(f"Residential      : {residential_count}")
    print(f"Commercial       : {commercial_count}")
    print(f"With proxy_1000m : {with_proxy}")
    print(f"Regions          : {dict(regions)}")
    print(f"Planning areas   : {len(set(o['planning_area'] for o in valid_outlets if o['planning_area']))}")
    print(f"Saved to         : {output_path}")

    top_10 = sorted(valid_outlets, key=lambda x: x["combined_wins"], reverse=True)[:10]
    print(f"\nTop 10 by combined wins:")
    for i, o in enumerate(top_10, 1):
        print(f"  {i:2d}. {o['outlet_name'][:35]:<35s}  wins={o['combined_wins']:>5d}  proxy1k={o['proxy_1000m']:>4d}  {o['area_type']}")



def main() -> None:
    print("Build Dataset")
    start_time = time.time()

    print("Download data.gov.sg datasets")
    step4_download_supplementary()

    print("[Step 4b] Build HDB block centroids")
    build_hdb_block_centroids(SUPP_DIR / "HDBExistingBuilding.geojson")
    
    print("Merge Data Sources into outlets_raw.csv")
    step5_merge()

    print("Geocode Outlets via OneMap API")
    geocoded_outlets = step6_geocode()
    if not geocoded_outlets:
        print("Geocoding failed.")
        sys.exit(1)
    ok_count = sum(1 for o in geocoded_outlets if o.get("geocode_status") == "OK")
    print(f"Result: {ok_count} geocoded outlets")

    print("Compute Proxy Volumes & Build Final Dataset")
    step7_build_final(geocoded_outlets)

    elapsed = time.time() - start_time
    print(f"{elapsed:.0f}s")
    print(f"Final dataset: {OUT_DIR / 'outlets_final.csv'}")

if __name__ == "__main__":
    main()
