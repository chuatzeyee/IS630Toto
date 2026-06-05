#!/usr/bin/env python3
"""
Geocode Singapore Pools outlets using OneMap API.

Usage:
    # Step 1: Prepare a CSV of outlets with postal codes (from scraping or GRA PDF)
    # Step 2: Run this script
    python3 geocode_outlets.py

Input:  ../data/outlets_raw.csv  (columns: outlet_name, address, postal_code)
Output: ../data/outlets_geocoded.csv (adds: latitude, longitude, planning_area, onemap_address)

OneMap API docs: https://www.onemap.gov.sg/apidocs/
- Search endpoint (no auth needed): /api/common/elastic/search
- Planning area endpoint (auth needed): /api/public/popapi/getPlanningArea
"""

import csv
import json
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError, URLError

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"

ONEMAP_SEARCH_URL = "https://www.onemap.gov.sg/api/common/elastic/search"
ONEMAP_TOKEN_URL = "https://www.onemap.gov.sg/api/auth/post/getToken"
ONEMAP_PLANNING_AREA_URL = "https://www.onemap.gov.sg/api/public/popapi/getPlanningArea"

REQUEST_DELAY = 1.0  # seconds between API calls


def onemap_search(postal_code: str) -> dict | None:
    """Geocode a 6-digit Singapore postal code via OneMap Search API (no auth)."""
    url = f"{ONEMAP_SEARCH_URL}?searchVal={postal_code}&returnGeom=Y&getAddrDetails=Y"
    req = Request(url, headers={"User-Agent": "SMU-IS630-Project/1.0"})

    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except (HTTPError, URLError, TimeoutError) as e:
        print(f"  [ERROR] Search failed for {postal_code}: {e}")
        return None

    if data.get("found", 0) == 0:
        return None

    result = data["results"][0]
    return {
        "latitude": float(result["LATITUDE"]),
        "longitude": float(result["LONGITUDE"]),
        "onemap_address": result.get("ADDRESS", ""),
        "building": result.get("BUILDING", ""),
        "road_name": result.get("ROAD_NAME", ""),
        "x_svy21": float(result.get("X", 0)),
        "y_svy21": float(result.get("Y", 0)),
    }


def onemap_search_by_address(address: str) -> dict | None:
    """Fallback: search by address string when postal code fails."""
    encoded = quote(address)
    url = f"{ONEMAP_SEARCH_URL}?searchVal={encoded}&returnGeom=Y&getAddrDetails=Y"
    req = Request(url, headers={"User-Agent": "SMU-IS630-Project/1.0"})

    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except (HTTPError, URLError, TimeoutError) as e:
        print(f"  [ERROR] Address search failed for '{address[:50]}': {e}")
        return None

    if data.get("found", 0) == 0:
        return None

    result = data["results"][0]
    return {
        "latitude": float(result["LATITUDE"]),
        "longitude": float(result["LONGITUDE"]),
        "onemap_address": result.get("ADDRESS", ""),
        "building": result.get("BUILDING", ""),
        "road_name": result.get("ROAD_NAME", ""),
        "x_svy21": float(result.get("X", 0)),
        "y_svy21": float(result.get("Y", 0)),
    }


def get_auth_token(email: str, password: str) -> str | None:
    """Get OneMap auth token for planning area lookups."""
    payload = json.dumps({"email": email, "password": password}).encode()
    req = Request(
        ONEMAP_TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "SMU-IS630-Project/1.0"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("access_token")
    except (HTTPError, URLError) as e:
        print(f"[ERROR] Auth failed: {e}")
        return None


def get_planning_area(lat: float, lon: float, token: str) -> str:
    """Look up planning area for a lat/lon coordinate (requires auth token)."""
    url = f"{ONEMAP_PLANNING_AREA_URL}?lat={lat}&lng={lon}&year=2019"
    req = Request(url, headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": "SMU-IS630-Project/1.0",
    })

    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            results = data.get("GeocodeInfo", [])
            if results:
                return results[0].get("PLANNINGAREA", "")
    except (HTTPError, URLError, TimeoutError) as e:
        print(f"  [WARN] Planning area lookup failed for ({lat}, {lon}): {e}")

    return ""


def create_sample_input():
    """Create a sample outlets_raw.csv for testing."""
    sample_path = DATA_DIR / "outlets_raw_SAMPLE.csv"
    rows = [
        {"outlet_name": "Tong Aik Huat", "address": "292 Yishun Street 22", "postal_code": "760292"},
        {"outlet_name": "Delisia Agency Pte Ltd", "address": "149 Rochor Road #B1-26 Fu Lu Shou Complex", "postal_code": "188425"},
        {"outlet_name": "NTUC FairPrice - NEX", "address": "23 Serangoon Central", "postal_code": "556083"},
        {"outlet_name": "Singapore Pools Bedok North Branch", "address": "212 Bedok North Street 1 #01-189", "postal_code": "460212"},
        {"outlet_name": "7-Eleven Toa Payoh", "address": "177 Toa Payoh Central #01-170", "postal_code": "310177"},
    ]

    with open(sample_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["outlet_name", "address", "postal_code"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created sample input: {sample_path}")
    print("Replace this with your actual scraped data, then re-run.")
    return sample_path


def main():
    input_path = DATA_DIR / "outlets_raw.csv"
    output_path = DATA_DIR / "outlets_geocoded.csv"
    failed_path = DATA_DIR / "outlets_geocode_failed.csv"

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        print("Creating sample file...")
        create_sample_input()
        input_path = DATA_DIR / "outlets_raw_SAMPLE.csv"
        output_path = DATA_DIR / "outlets_geocoded_SAMPLE.csv"
        failed_path = DATA_DIR / "outlets_geocode_failed_SAMPLE.csv"

    # Optional: OneMap auth for planning area lookups
    onemap_email = os.environ.get("ONEMAP_EMAIL", "")
    onemap_password = os.environ.get("ONEMAP_PASSWORD", "")
    token = None

    if onemap_email and onemap_password:
        print("Authenticating with OneMap for planning area lookups...")
        token = get_auth_token(onemap_email, onemap_password)
        if token:
            print("  Auth successful.")
        else:
            print("  Auth failed. Planning area column will be empty.")
            print("  Register free at: https://developers.onemap.sg/signup/")
    else:
        print("No ONEMAP_EMAIL / ONEMAP_PASSWORD set. Skipping planning area lookups.")
        print("To enable: export ONEMAP_EMAIL='you@email.com' ONEMAP_PASSWORD='yourpass'")
        print("Register free at: https://developers.onemap.sg/signup/")
        print()

    # Read input
    with open(input_path, newline="") as f:
        reader = csv.DictReader(f)
        outlets = list(reader)

    print(f"Loaded {len(outlets)} outlets from {input_path}")
    print(f"Geocoding with ~{REQUEST_DELAY}s delay per request...")
    print(f"Estimated time: ~{len(outlets) * REQUEST_DELAY / 60:.1f} minutes")
    print()

    geocoded = []
    failed = []

    for i, outlet in enumerate(outlets):
        name = outlet.get("outlet_name", "Unknown")
        postal = outlet.get("postal_code", "").strip()
        address = outlet.get("address", "").strip()

        print(f"[{i+1}/{len(outlets)}] {name} (postal: {postal})...", end=" ")

        result = None

        # Try postal code first
        if postal and len(postal) == 6 and postal.isdigit():
            result = onemap_search(postal)

        # Fallback to address string
        if result is None and address:
            print("postal miss, trying address...", end=" ")
            result = onemap_search_by_address(address)

        if result is None:
            print("FAILED")
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
                planning_area = get_planning_area(result["latitude"], result["longitude"], token)

            print(f"OK ({result['latitude']:.6f}, {result['longitude']:.6f})"
                  + (f" [{planning_area}]" if planning_area else ""))

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

        time.sleep(REQUEST_DELAY)

    # Write output
    if geocoded:
        fieldnames = list(geocoded[0].keys())
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(geocoded)
        print(f"\nSaved {len(geocoded)} outlets to {output_path}")

    if failed:
        fieldnames = list(failed[0].keys())
        with open(failed_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(failed)
        print(f"Saved {len(failed)} failed lookups to {failed_path}")

    # Summary
    ok_count = sum(1 for r in geocoded if r["geocode_status"] == "OK")
    fail_count = len(geocoded) - ok_count
    print(f"\nSummary: {ok_count} geocoded, {fail_count} failed out of {len(geocoded)} total")

    if fail_count > 0:
        print("\nFailed outlets need manual geocoding. Options:")
        print("  1. Search manually at https://www.onemap.gov.sg/")
        print("  2. Try Google Maps geocoding as fallback")
        print("  3. Look up the postal code on Google Maps and copy coordinates")


if __name__ == "__main__":
    main()
