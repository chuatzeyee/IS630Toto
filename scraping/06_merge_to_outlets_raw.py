#!/usr/bin/env python3
"""
Step 6: Merge scraped outlet data + GRA directory into outlets_raw.csv for geocoding.

Input:  ../data/raw/outlets_with_addresses.csv, ../data/raw/gra_outlets.csv, ../data/raw/outlets_list.csv
Output: ../data/outlets_raw.csv
"""

import csv
import re
from pathlib import Path
from difflib import SequenceMatcher

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
RAW_DIR = DATA_DIR / "raw"


def load_csv(path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def normalize_name(name):
    name = name.lower().strip()
    name = re.sub(r'\b(pte|ltd|private|limited|co|corp)\b', '', name)
    name = re.sub(r'[^a-z0-9\s]', '', name)
    return re.sub(r'\s+', ' ', name).strip()


def fuzzy_match(name1, name2, threshold=0.7):
    return SequenceMatcher(None, normalize_name(name1), normalize_name(name2)).ratio() >= threshold


def find_gra_match(name: str, postal: str, gra_by_postal: dict, gra_list: list) -> dict | None:
    if postal and postal in gra_by_postal:
        return gra_by_postal[postal]
    norm = normalize_name(name)
    for g in gra_list:
        gra_full = g.get("full_address", "") + " " + g.get("outlet_name", "")
        if norm and len(norm) > 5 and norm in normalize_name(gra_full):
            return g
        if fuzzy_match(name, g.get("outlet_name", ""), threshold=0.6):
            return g
    return None


def main():
    print("=" * 60)
    print("STEP 6: Merge Data Sources into outlets_raw.csv")
    print("=" * 60)

    scraped = load_csv(RAW_DIR / "outlets_with_addresses.csv")
    gra = load_csv(RAW_DIR / "gra_outlets.csv")
    outlet_list = load_csv(RAW_DIR / "outlets_list.csv") or load_csv(RAW_DIR / "outlets_list_playwright.csv")

    print(f"  Scraped: {len(scraped)}, GRA: {len(gra)}, Aggregate: {len(outlet_list)}")

    gra_by_postal = {g["postal_code"].strip(): g for g in gra if re.match(r'^\d{6}$', g.get("postal_code", "").strip())}
    agg_by_name = {o.get("outlet_name", "").strip(): o for o in outlet_list}
    scraped_by_name = {s.get("outlet_name", "").strip(): s for s in scraped}

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

        gra_match = find_gra_match(name, postal, gra_by_postal, gra)
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
            "outlet_name": name, "address": address, "postal_code": postal,
            "outlet_type": outlet_type, "group1_wins": g1, "group2_wins": g2,
            "combined_wins": g1 + g2, "source": source,
        }

    for g in gra:
        gp = g.get("postal_code", "").strip()
        if gp in used_gra_postals:
            continue
        gname = g.get("full_address", g.get("outlet_name", "")).strip()[:80]
        if gname and gname not in merged:
            merged[gname] = {
                "outlet_name": gname, "address": g.get("full_address", ""),
                "postal_code": gp, "outlet_type": g.get("outlet_type", ""),
                "group1_wins": 0, "group2_wins": 0, "combined_wins": 0,
                "source": "gra_only",
            }

    outlets = list(merged.values())
    physical = [o for o in outlets if "account betting" not in o["outlet_name"].lower()
                and "itoto" not in o["outlet_name"].lower()]
    with_postal = sum(1 for o in physical if re.match(r'^\d{6}$', o["postal_code"]))

    print(f"\n  Merged: {len(outlets)}, Physical: {len(physical)}, With postal: {with_postal}")

    output_path = DATA_DIR / "outlets_raw.csv"
    fields = ["outlet_name", "address", "postal_code", "outlet_type", "group1_wins", "group2_wins", "combined_wins", "source"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(physical)

    print(f"  Saved {len(physical)} outlets to {output_path}")
    print(f"\nNext: cd ../scripts && python3 geocode_outlets.py")


if __name__ == "__main__":
    main()
