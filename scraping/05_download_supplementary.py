#!/usr/bin/env python3
"""
Step 5: Download supplementary datasets from data.gov.sg.

Output: ../data/supplementary/
"""

import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data" / "supplementary"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = [
    {"name": "HDB Dwelling Units by Town and Flat Type",
     "dataset_id": "d_07b1eeeb22efdf7faf5bd6a13667359d",
     "filename": "hdb_dwelling_units_by_town.csv",
     "description": "~4,900 rows, FY2008-FY2022, proxy for foot traffic"},
    {"name": "Census 2020 Population by Planning Area (Dwelling Type)",
     "dataset_id": "d_7f243956483d5901f237e6f87b096636",
     "filename": "census2020_pop_by_dwelling.csv",
     "description": "Population by planning area and dwelling type"},
    {"name": "Census 2020 Population by Planning Area (Age & Sex)",
     "dataset_id": "d_d95ae740c0f8961a0b10435836660ce0",
     "filename": "census2020_pop_by_age_sex.csv",
     "description": "130 KB, population by age group and sex"},
    {"name": "URA Master Plan 2019 Planning Area Boundary (No Sea)",
     "dataset_id": "d_4765db0e87b9c86336792efe8a1f7a66",
     "filename": "planning_area_boundary.geojson",
     "description": "GeoJSON boundaries for spatial joins"},
    {"name": "URA Master Plan 2019 Subzone Boundary (No Sea)",
     "dataset_id": "d_8594ae9ff96d0c708bc2af633048edfb",
     "filename": "subzone_boundary.geojson",
     "description": "More granular geographic boundaries"},
]

HEADERS = {"User-Agent": "SMU-IS630-Project/1.0"}


def download_file(url, output_path):
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req, timeout=60) as resp:
            content = resp.read()
            with open(output_path, "wb") as f:
                f.write(content)
            return len(content)
    except (HTTPError, URLError) as e:
        print(f"  [ERROR] {e}")
        return 0


def try_download_dataset(dataset):
    filename = dataset["filename"]
    dataset_id = dataset["dataset_id"]
    output_path = DATA_DIR / filename

    if output_path.exists():
        print(f"  Already exists: {filename} ({output_path.stat().st_size:,} bytes)")
        return True

    print(f"  Downloading {dataset['name']}...")

    poll_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/poll-download"
    req = Request(poll_url, headers=HEADERS)
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            download_url = data.get("data", {}).get("url")
            if download_url:
                size = download_file(download_url, output_path)
                if size > 0:
                    print(f"    Saved {filename} ({size:,} bytes)")
                    return True
    except (HTTPError, URLError, json.JSONDecodeError) as e:
        print(f"    API poll failed: {e}")

    initiate_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/initiate-download"
    req = Request(initiate_url, headers={**HEADERS, "Content-Type": "application/json"},
                  data=b'{}', method="POST")
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            download_url = data.get("data", {}).get("url")
            if download_url:
                size = download_file(download_url, output_path)
                if size > 0:
                    print(f"    Saved {filename} ({size:,} bytes)")
                    return True
    except (HTTPError, URLError, json.JSONDecodeError):
        pass

    print(f"    [MANUAL] https://data.gov.sg/datasets/{dataset_id}/view -> save as {filename}")
    return False


def main():
    print("=" * 60)
    print("STEP 5: Download Supplementary Datasets (data.gov.sg)")
    print("=" * 60)

    success = 0
    for ds in DATASETS:
        print(f"\n[{ds['filename']}] {ds['description']}")
        if try_download_dataset(ds):
            success += 1

    print(f"\n{'=' * 60}")
    print(f"Downloaded: {success}/{len(DATASETS)}")
    if success < len(DATASETS):
        print(f"\nFor manual downloads, save to: {DATA_DIR}/")
        for ds in DATASETS:
            if not (DATA_DIR / ds["filename"]).exists():
                print(f"  https://data.gov.sg/datasets/{ds['dataset_id']}/view -> {ds['filename']}")


if __name__ == "__main__":
    main()
