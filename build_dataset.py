import csv
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
SUPP_DIR = DATA_DIR / "supplementary"
OUT_DIR = DATA_DIR / "analysis_ready"

SUPP_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

ONEMAP_SEARCH_URL = "https://www.onemap.gov.sg/api/common/elastic/search"
ONEMAP_TOKEN_URL = "https://www.onemap.gov.sg/api/auth/post/getToken"
ONEMAP_PA_URL = "https://www.onemap.gov.sg/api/public/popapi/getPlanningArea"

API_HEADERS = {"User-Agent": "SMU-IS630-Project/1.0"}

SUPPLEMENTARY_DATASETS = [
    {
        "name": "HDB Dwelling Units by Town and Flat Type",
        "dataset_id": "d_07b1eeeb22efdf7faf5bd6a13667359d",
        "filename": "hdb_dwelling_units_by_town.csv",
    },
    {
        "name": "Census 2020 Population by Planning Area (Dwelling Type)",
        "dataset_id": "d_7f243956483d5901f237e6f87b096636",
        "filename": "census2020_pop_by_dwelling.csv",
    },
    {
        "name": "Census 2020 Population by Planning Area (Age & Sex)",
        "dataset_id": "d_d95ae740c0f8961a0b10435836660ce0",
        "filename": "census2020_pop_by_age_sex.csv",
    },
    {
        "name": "URA Master Plan 2019 Planning Area Boundary (No Sea)",
        "dataset_id": "d_4765db0e87b9c86336792efe8a1f7a66",
        "filename": "planning_area_boundary.geojson",
    },
    {
        "name": "URA Master Plan 2019 Subzone Boundary (No Sea)",
        "dataset_id": "d_8594ae9ff96d0c708bc2af633048edfb",
        "filename": "subzone_boundary.geojson",
    },
]

HDB_TOWN_TO_PA = {
    "Ang Mo Kio": ["ANG MO KIO"],
    "Bedok": ["BEDOK"],
    "Bishan": ["BISHAN"],
    "Bukit Batok": ["BUKIT BATOK"],
    "Bukit Merah": ["BUKIT MERAH"],
    "Bukit Panjang": ["BUKIT PANJANG"],
    "Bukit Timah": ["BUKIT TIMAH"],
    "Central Area": ["DOWNTOWN CORE", "MARINA SOUTH", "MUSEUM", "OUTRAM", "RIVER VALLEY", "ROCHOR"],
    "Choa Chu Kang": ["CHOA CHU KANG"],
    "Clementi": ["CLEMENTI"],
    "Geylang": ["GEYLANG"],
    "Hougang": ["HOUGANG"],
    "Jurong East": ["JURONG EAST"],
    "Jurong West": ["JURONG WEST"],
    "Kallang/Whampoa": ["KALLANG"],
    "Marine Parade": ["MARINE PARADE"],
    "Pasir Ris": ["PASIR RIS"],
    "Punggol": ["PUNGGOL"],
    "Queenstown": ["QUEENSTOWN"],
    "Sembawang": ["SEMBAWANG"],
    "Sengkang": ["SENGKANG"],
    "Serangoon": ["SERANGOON"],
    "Tampines": ["TAMPINES"],
    "Tengah": ["TENGAH"],
    "Toa Payoh": ["TOA PAYOH"],
    "Woodlands": ["WOODLANDS"],
    "Yishun": ["YISHUN"],
}

HAVERSINE_RADII_M = [500, 750, 1000, 1500]

def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def normalize_name(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r'\b(pte|ltd|private|limited|co|corp)\b', '', name)
    name = re.sub(r'[^a-z0-9\s]', '', name)
    return re.sub(r'\s+', ' ', name).strip()


def fuzzy_match(name1: str, name2: str, threshold: float = 0.7) -> bool:
    return SequenceMatcher(None, normalize_name(name1), normalize_name(name2)).ratio() >= threshold


def step4_download_supplementary() -> int:
    success = 0
    for ds in SUPPLEMENTARY_DATASETS:
        output_path = SUPP_DIR / ds["filename"]
        if output_path.exists():
            print(f"{ds['filename']} already exists ({output_path.stat().st_size:,} bytes)")
            success += 1
            continue

        print(f"Downloading {ds['name']}")
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


def step5_merge() -> list[dict]:
    output_path = DATA_DIR / "outlets_raw.csv"
    if output_path.exists():
        print(f"{output_path} already exists")
        with open(output_path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def load_csv(path: Path) -> list[dict]:
        if not path.exists():
            return []
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    outlet_list = load_csv(RAW_DIR / "outlets_list.csv")
    scraped_outlets = load_csv(RAW_DIR / "outlets_with_addresses.csv")
    gra_outlets = load_csv(RAW_DIR / "gra_outlets.csv")

    print(f"Sources: aggregate={len(outlet_list)}, scraped={len(scraped_outlets)}, GRA={len(gra_outlets)}")

    gra_by_postal = {}
    for g in gra_outlets:
        pc = g.get("postal_code", "").strip()
        if re.match(r'^\d{6}$', pc):
            gra_by_postal[pc] = g

    scraped_by_name = {s.get("outlet_name", "").strip(): s for s in scraped_outlets}

    merged = {}
    used_gra_postals = set()

    for o in outlet_list:
        name = o.get("outlet_name", "").strip()
        if not name:
            continue
        g1 = int(o.get("group1_wins", 0))
        g2 = int(o.get("group2_wins", 0))

        scraped_info = scraped_by_name.get(name, {})
        postal = scraped_info.get("postal_code", "").strip()
        address = scraped_info.get("address", "").strip()

        gra_match = None
        if postal and postal in gra_by_postal:
            gra_match = gra_by_postal[postal]
        else:
            norm = normalize_name(name)
            for g in gra_outlets:
                gra_full = g.get("full_address", "") + " " + g.get("outlet_name", "")
                if norm and len(norm) > 5 and norm in normalize_name(gra_full):
                    gra_match = g
                    break
                if fuzzy_match(name, g.get("outlet_name", ""), threshold=0.6):
                    gra_match = g
                    break

        outlet_type = ""
        if gra_match:
            gp = gra_match.get("postal_code", "").strip()
            if gp and re.match(r'^\d{6}$', gp):
                postal = gp
                used_gra_postals.add(gp)
            if not address:
                address = gra_match.get("full_address", "")
            outlet_type = gra_match.get("outlet_type", "")

        source = "matched" if gra_match else ("scraped" if scraped_info else "aggregate_only")
        merged[name] = {
            "outlet_name": name,
            "address": address,
            "postal_code": postal,
            "outlet_type": outlet_type,
            "group1_wins": g1,
            "group2_wins": g2,
            "combined_wins": g1 + g2,
            "source": source,
        }

    for g in gra_outlets:
        gp = g.get("postal_code", "").strip()
        if gp in used_gra_postals:
            continue
        gname = g.get("full_address", g.get("outlet_name", "")).strip()[:80]
        if gname and gname not in merged:
            merged[gname] = {
                "outlet_name": gname,
                "address": g.get("full_address", ""),
                "postal_code": gp,
                "outlet_type": g.get("outlet_type", ""),
                "group1_wins": 0,
                "group2_wins": 0,
                "combined_wins": 0,
                "source": "gra_only",
            }

    outlets = list(merged.values())
    physical = [
        o for o in outlets
        if "account betting" not in o["outlet_name"].lower()
        and "itoto" not in o["outlet_name"].lower()
    ]

    fields = ["outlet_name", "address", "postal_code", "outlet_type", "group1_wins", "group2_wins", "combined_wins", "source"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(physical)

    print(f"Merged {len(physical)} physical outlets to {output_path}")
    return physical


def step6_geocode() -> list[dict]:
    input_path = DATA_DIR / "outlets_raw.csv"
    output_path = DATA_DIR / "outlets_geocoded.csv"

    if output_path.exists():
        print(f"{output_path} already exists")
        with open(output_path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    if not input_path.exists():
        print(f"{input_path} not found")
        return []

    onemap_email = os.environ.get("ONEMAP_EMAIL", "")
    onemap_password = os.environ.get("ONEMAP_PASSWORD", "")
    token = None

    if onemap_email and onemap_password:
        print("Authenticating with OneMap")
        payload = json.dumps({"email": onemap_email, "password": onemap_password}).encode()
        req = Request(
            ONEMAP_TOKEN_URL,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "SMU-IS630-Project/1.0"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                token = data.get("access_token")
                if token:
                    print("  Auth successful.")
        except (HTTPError, URLError):
            print("Auth failed.")

    with open(input_path, newline="", encoding="utf-8") as f:
        outlets = list(csv.DictReader(f))

    print(f"Geocoding {len(outlets)} outlets (~{len(outlets) / 60:.0f} min)...")

    geocoded = []
    failed_path = DATA_DIR / "outlets_geocode_failed.csv"
    failed = []

    for i, outlet in enumerate(outlets):
        name = outlet.get("outlet_name", "Unknown")
        postal = outlet.get("postal_code", "").strip()
        address = outlet.get("address", "").strip()

        result = None

        if postal and len(postal) == 6 and postal.isdigit():
            url = f"{ONEMAP_SEARCH_URL}?searchVal={postal}&returnGeom=Y&getAddrDetails=Y"
            req = Request(url, headers=API_HEADERS)
            try:
                with urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode())
                    if data.get("found", 0) > 0:
                        r = data["results"][0]
                        result = {
                            "latitude": float(r["LATITUDE"]),
                            "longitude": float(r["LONGITUDE"]),
                            "onemap_address": r.get("ADDRESS", ""),
                            "x_svy21": float(r.get("X", 0)),
                            "y_svy21": float(r.get("Y", 0)),
                        }
            except (HTTPError, URLError, TimeoutError):
                pass

        if result is None and address:
            encoded = quote(address)
            url = f"{ONEMAP_SEARCH_URL}?searchVal={encoded}&returnGeom=Y&getAddrDetails=Y"
            req = Request(url, headers=API_HEADERS)
            try:
                with urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode())
                    if data.get("found", 0) > 0:
                        r = data["results"][0]
                        result = {
                            "latitude": float(r["LATITUDE"]),
                            "longitude": float(r["LONGITUDE"]),
                            "onemap_address": r.get("ADDRESS", ""),
                            "x_svy21": float(r.get("X", 0)),
                            "y_svy21": float(r.get("Y", 0)),
                        }
            except (HTTPError, URLError, TimeoutError):
                pass

        if result is None:
            failed.append(outlet)
            geocoded.append({
                **outlet,
                "latitude": "",
                "longitude": "",
                "onemap_address": "",
                "planning_area": "",
                "x_svy21": "",
                "y_svy21": "",
                "geocode_status": "FAILED",
            })
        else:
            planning_area = ""
            if token:
                time.sleep(0.3)
                pa_url = f"{ONEMAP_PA_URL}?lat={result['latitude']}&lng={result['longitude']}&year=2019"
                pa_req = Request(pa_url, headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": "SMU-IS630-Project/1.0",
                })
                try:
                    with urlopen(pa_req, timeout=15) as resp:
                        pa_data = json.loads(resp.read().decode())
                        results = pa_data.get("GeocodeInfo", [])
                        if results:
                            planning_area = results[0].get("PLANNINGAREA", "")
                except (HTTPError, URLError, TimeoutError):
                    pass

            geocoded.append({
                **outlet,
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "onemap_address": result["onemap_address"],
                "planning_area": planning_area,
                "x_svy21": result["x_svy21"],
                "y_svy21": result["y_svy21"],
                "geocode_status": "OK",
            })

        if (i + 1) % 100 == 0:
            print(f"    [{i+1}/{len(outlets)}] geocoded...")

        time.sleep(1.0)

    if geocoded:
        fieldnames = list(geocoded[0].keys())
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(geocoded)

    if failed:
        fieldnames = list(failed[0].keys())
        with open(failed_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(failed)

    ok_count = sum(1 for r in geocoded if r["geocode_status"] == "OK")
    print(f"Geocoded: {ok_count} OK, {len(geocoded) - ok_count} failed out of {len(geocoded)}")
    return geocoded


def step7_build_final(geocoded_outlets: list[dict]) -> None:
    output_path = OUT_DIR / "outlets_final.csv"

    geojson_path = SUPP_DIR / "planning_area_boundary.geojson"
    hdb_path = SUPP_DIR / "hdb_dwelling_units_by_town.csv"

    if not geojson_path.exists():
        print(f"{geojson_path} not found.")
        return
    if not hdb_path.exists():
        print(f"{hdb_path} not found.")
        return

    with open(geojson_path, encoding="utf-8") as f:
        geojson = json.load(f)

    pa_centroids: dict[str, tuple[float, float]] = {}
    pa_regions: dict[str, str] = {}

    for feature in geojson["features"]:
        props = feature["properties"]
        pa_name = props["PLN_AREA_N"]
        region = props["REGION_N"]
        pa_regions[pa_name] = region

        geom = feature["geometry"]
        coords = geom["coordinates"]

        all_points = []
        if geom["type"] == "Polygon":
            all_points = coords[0]
        elif geom["type"] == "MultiPolygon":
            for polygon in coords:
                all_points.extend(polygon[0])

        if all_points:
            avg_lon = sum(p[0] for p in all_points) / len(all_points)
            avg_lat = sum(p[1] for p in all_points) / len(all_points)
            pa_centroids[pa_name] = (avg_lat, avg_lon)

    hdb_by_pa: dict[str, int] = defaultdict(int)

    with open(hdb_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["financial_year"] != "2021":
                continue
            town = row["town_or_estate"]
            raw_units = row["no_of_dwelling_units"].strip()
            if raw_units in ("", "-", "na", "n/a"):
                continue
            units = int(raw_units)
            target_pas = HDB_TOWN_TO_PA.get(town, [])
            if len(target_pas) == 1:
                hdb_by_pa[target_pas[0]] += units
            elif len(target_pas) > 1:
                share = units // len(target_pas)
                for pa in target_pas:
                    hdb_by_pa[pa] += share

    print(f"Loaded {len(pa_centroids)} planning area centroids")
    print(f"Loaded HDB units for {len(hdb_by_pa)} planning areas")

    valid_outlets = []
    for o in geocoded_outlets:
        if o.get("geocode_status") != "OK":
            continue
        try:
            lat = float(o["latitude"])
            lon = float(o["longitude"])
        except (ValueError, KeyError):
            continue
        valid_outlets.append({
            "outlet_name": o["outlet_name"],
            "address": o.get("address", ""),
            "postal_code": o.get("postal_code", ""),
            "outlet_type": o.get("outlet_type", ""),
            "group1_wins": int(o.get("group1_wins", 0)),
            "group2_wins": int(o.get("group2_wins", 0)),
            "combined_wins": int(o.get("combined_wins", 0)),
            "source": o.get("source", ""),
            "latitude": lat,
            "longitude": lon,
            "onemap_address": o.get("onemap_address", ""),
            "planning_area": o.get("planning_area", ""),
            "x_svy21": o.get("x_svy21", ""),
            "y_svy21": o.get("y_svy21", ""),
            "geocode_status": "OK",
        })

    pa_assign_count = 0
    for outlet in valid_outlets:
        pa = outlet["planning_area"].strip().upper()
        if not pa:
            best_pa = ""
            best_dist = float("inf")
            for pa_name, (clat, clon) in pa_centroids.items():
                d = haversine_m(outlet["latitude"], outlet["longitude"], clat, clon)
                if d < best_dist:
                    best_dist = d
                    best_pa = pa_name
            if best_pa and best_dist < 5000:
                outlet["planning_area"] = best_pa
                pa_assign_count += 1
            pa = outlet["planning_area"]

        outlet["region"] = pa_regions.get(pa.upper(), "")

    if pa_assign_count > 0:
        print(f"Assigned planning area via nearest centroid for {pa_assign_count} outlets")

    residential_pas = set()
    for pa_name in pa_centroids:
        if hdb_by_pa.get(pa_name, 0) > 0:
            residential_pas.add(pa_name)

    for outlet in valid_outlets:
        pa = outlet["planning_area"].upper()
        if pa in residential_pas:
            outlet["area_type"] = "residential"
        elif pa in pa_regions:
            outlet["area_type"] = "commercial"
        else:
            outlet["area_type"] = "unknown"

    for outlet in valid_outlets:
        pa = outlet["planning_area"].upper()
        outlet["pa_hdb_units"] = hdb_by_pa.get(pa, 0)

    print(f"Computing HDB proxy volumes at radii: {HAVERSINE_RADII_M}")

    all_pa_coords = []
    for pa_name, (clat, clon) in pa_centroids.items():
        all_pa_coords.append((pa_name, clat, clon, hdb_by_pa.get(pa_name, 0)))

    for outlet in valid_outlets:
        olat = outlet["latitude"]
        olon = outlet["longitude"]
        for radius in HAVERSINE_RADII_M:
            total = 0
            for pa_name, clat, clon, units in all_pa_coords:
                if units > 0:
                    dist = haversine_m(olat, olon, clat, clon)
                    if dist <= radius:
                        total += units
            outlet[f"proxy_{radius}m"] = total

    for outlet in valid_outlets:
        proxy_1000 = outlet.get("proxy_1000m", 0)
        combined = outlet["combined_wins"]
        if proxy_1000 > 0 and combined > 0:
            outlet["win_rate_1000m"] = round(combined / proxy_1000, 8)
        else:
            outlet["win_rate_1000m"] = 0.0

    fieldnames = [
        "outlet_name", "address", "postal_code", "outlet_type",
        "group1_wins", "group2_wins", "combined_wins", "source",
        "latitude", "longitude", "onemap_address", "planning_area",
        "x_svy21", "y_svy21", "geocode_status",
        "proxy_500m", "proxy_750m", "proxy_1000m", "proxy_1500m",
        "area_type", "region", "pa_hdb_units", "win_rate_1000m",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(valid_outlets)

    print(f"  Saved {len(valid_outlets)} outlets to {output_path}")

    residential_count = sum(1 for o in valid_outlets if o["area_type"] == "residential")
    commercial_count = sum(1 for o in valid_outlets if o["area_type"] == "commercial")
    with_proxy = sum(1 for o in valid_outlets if o["proxy_1000m"] > 0)
    regions = defaultdict(int)
    for o in valid_outlets:
        if o["region"]:
            regions[o["region"]] += 1

    print(f"Total outlets: {len(valid_outlets)}")
    print(f"Residential: {residential_count}, Commercial: {commercial_count}")
    print(f"With proxy_1000m > 0: {with_proxy}")
    print(f"Regions: {dict(regions)}")
    print(f"Planning areas covered: {len(set(o['planning_area'] for o in valid_outlets if o['planning_area']))}")

    top_10 = sorted(valid_outlets, key=lambda x: x["combined_wins"], reverse=True)[:10]
    print(f"\nTop 10 outlets by combined wins:")
    for i, o in enumerate(top_10, 1):
        print(f"{i:2d}. {o['outlet_name'][:35]:<35s}  wins={o['combined_wins']:>5d}  proxy1k={o['proxy_1000m']:>8d}  {o['area_type']}")


def main() -> None:
    print("Build Dataset")
    start_time = time.time()

    print("Download data.gov.sg datasets")
    step4_download_supplementary()

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