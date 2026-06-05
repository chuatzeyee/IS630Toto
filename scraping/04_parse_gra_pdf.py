#!/usr/bin/env python3
"""
Step 4: Parse the GRA PDF for the official outlet list with postal codes.

Source: https://www.gra.gov.sg (Betting Operations > Lottery)
Output: ../data/raw/gra_outlets.csv
"""

import csv
import re
from pathlib import Path

import pdfplumber
import requests

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

GRA_PDF_URL = "https://www.gra.gov.sg/docs/default-source/betting-operations--lottery-and-game-of-chance/list-of-approved-singapore-pools-gambling-venuesf0fae72f-58d2-433f-abbe-2da61f8b6f22.pdf"
PDF_PATH = DATA_DIR / "gra_approved_outlets.pdf"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def download_pdf():
    if PDF_PATH.exists():
        print(f"PDF already exists: {PDF_PATH}")
        return True
    print(f"Downloading GRA PDF...")
    try:
        resp = requests.get(GRA_PDF_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        with open(PDF_PATH, "wb") as f:
            f.write(resp.content)
        print(f"  Saved ({len(resp.content):,} bytes)")
        return True
    except requests.RequestException as e:
        print(f"  [ERROR] Download failed: {e}")
        print(f"  Download manually from gra.gov.sg and save as: {PDF_PATH}")
        return False


def extract_outlets():
    print(f"\nParsing PDF...")
    outlets = []

    with pdfplumber.open(PDF_PATH) as pdf:
        print(f"  Pages: {len(pdf.pages)}")
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or all(cell is None for cell in row):
                        continue
                    cells = [str(c).strip() if c else "" for c in row]
                    if any(h in cells[0].lower() for h in ["s/n", "serial", "no.", "building"]):
                        continue
                    if cells[0] and re.match(r'^\d+$', cells[0]):
                        sn = int(cells[0])
                        if len(cells) >= 6:
                            building, street, unit, outlet_name, postal_code = cells[1], cells[2], cells[3], cells[4], cells[5].replace(" ", "")
                        elif len(cells) >= 5:
                            building, street, unit, outlet_name, postal_code = cells[1], cells[2], "", cells[3], cells[4].replace(" ", "")
                        else:
                            continue
                        postal_match = re.search(r'(\d{6})', postal_code)
                        postal_code = postal_match.group(1) if postal_match else postal_code
                        full_address = " ".join(p for p in [building, street, unit] if p)
                        outlets.append({"sn": sn, "building": building, "street": street, "unit": unit,
                                       "outlet_name": outlet_name, "postal_code": postal_code, "full_address": full_address})
            print(f"  Page {page_num}: {len(outlets)} outlets so far")

    if not outlets:
        print("  Table extraction empty, trying text-based fallback...")
        with pdfplumber.open(PDF_PATH) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                for line in text.split("\n"):
                    m = re.search(r'(\d{6})\s*$', line.strip())
                    if m:
                        outlets.append({"sn": len(outlets)+1, "building": "", "street": "", "unit": "",
                                       "outlet_name": line.strip()[:50], "postal_code": m.group(1),
                                       "full_address": line.strip()})
    return outlets


def categorize_outlet(name, address):
    combined = (name + " " + address).lower()
    if "livewire" in combined: return "Livewire"
    if "betting centre" in combined or "ocb" in combined: return "Betting Centre"
    if "branch" in combined: return "Branch"
    if "lobby" in combined: return "Lottery Lobby"
    if "7-eleven" in combined or "7 eleven" in combined: return "Authorised Retailer (7-Eleven)"
    if "fairprice" in combined or "ntuc" in combined: return "Authorised Retailer (FairPrice)"
    return "Authorised Retailer"


def main():
    print("=" * 60)
    print("STEP 4: Parse GRA PDF (Official Outlet Directory)")
    print("=" * 60)
    if not download_pdf():
        return
    outlets = extract_outlets()
    print(f"\nExtracted {len(outlets)} outlets")
    if not outlets:
        print(f"WARNING: Check {PDF_PATH} manually.")
        return
    for o in outlets:
        o["outlet_type"] = categorize_outlet(o["outlet_name"], o["full_address"])
    output_path = DATA_DIR / "gra_outlets.csv"
    fields = ["sn", "outlet_name", "full_address", "building", "street", "unit", "postal_code", "outlet_type"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(outlets)
    print(f"Saved to {output_path}")
    from collections import Counter
    for t, c in Counter(o["outlet_type"] for o in outlets).most_common():
        print(f"  {t}: {c}")
    valid_count = sum(1 for o in outlets if re.match(r'^\d{6}$', o['postal_code']))
    print(f"Valid postal codes: {valid_count}/{len(outlets)}")


if __name__ == "__main__":
    main()
