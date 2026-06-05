#!/usr/bin/env python3
"""
Step 2: Scrape per-outlet winning history from detail pages.
For each outlet in outlets_list.csv, fetches the detail page and extracts
all winning records (draw date, draw number, prize amount, bet type, prize group).

Source: https://www.singaporepools.com.sg/outlets/Pages/lo_details.aspx?sppl=<base64>
Rendering: Server-side HTML (BeautifulSoup works)

Input:  ../data/raw/outlets_list.csv
Output: ../data/raw/outlet_win_history.csv
        ../data/raw/outlets_with_addresses.csv
"""

import csv
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data" / "raw"

BASE_URL = "https://www.singaporepools.com.sg"
REQUEST_DELAY = 2.0

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def load_outlets_list():
    for name in ["outlets_list.csv", "outlets_list_playwright.csv"]:
        path = DATA_DIR / name
        if path.exists():
            with open(path, newline="", encoding="utf-8") as f:
                data = list(csv.DictReader(f))
            print(f"Loaded {len(data)} outlets from {path}")
            return data
    print("ERROR: No outlets list found. Run step 01 or 03 first.")
    return []


def scrape_outlet_detail(url, outlet_name):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [ERROR] {e}")
        return None, []

    soup = BeautifulSoup(resp.text, "lxml")
    result = {"address": "", "postal_code": ""}
    wins = []

    # Extract address with postal code
    for tag in soup.find_all(["div", "span", "p", "td"]):
        text = tag.get_text(strip=True)
        if re.search(r'Singapore\s+\d{6}', text) and len(text) < 200:
            result["address"] = text
            postal_match = re.search(r'Singapore\s+(\d{6})', text)
            if postal_match:
                result["postal_code"] = postal_match.group(1)
            break

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue
        header_text = rows[0].get_text(strip=True).lower()
        if "draw date" not in header_text and "draw no" not in header_text:
            continue

        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            texts = [c.get_text(strip=True) for c in cells]
            draw_date = texts[1]
            draw_no_str = texts[2]
            share_text = texts[3]

            if not re.match(r'\d{2}/\d{2}/\d{4}', draw_date):
                continue
            if not draw_no_str.isdigit():
                continue

            amount = 0.0
            amt_match = re.search(r'S?\$?([\d,]+)', share_text)
            if amt_match:
                amount = float(amt_match.group(1).replace(",", ""))

            prize_group = 0
            grp_match = re.search(r'Group\s+(\d)', share_text)
            if grp_match:
                prize_group = int(grp_match.group(1))

            bet_type = ""
            type_match = re.search(r'Group\s+\d\s+(.*?)\)', share_text)
            if type_match:
                bet_type = type_match.group(1).strip()

            wins.append({
                "outlet_name": outlet_name,
                "draw_date": draw_date,
                "draw_number": int(draw_no_str),
                "prize_amount": amount,
                "bet_type": bet_type,
                "prize_group": prize_group,
            })

    return result, wins


def save_checkpoint(all_wins, all_outlets):
    if all_wins:
        path = DATA_DIR / "outlet_win_history.csv"
        fields = ["outlet_name", "draw_date", "draw_number", "prize_amount", "bet_type", "prize_group"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(all_wins)

    if all_outlets:
        path = DATA_DIR / "outlets_with_addresses.csv"
        fields = ["outlet_name", "address", "postal_code", "detail_url"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(all_outlets)


def load_existing_progress() -> tuple[list[dict], list[dict], set[str]]:
    all_wins: list[dict] = []
    all_outlets: list[dict] = []
    done_names: set[str] = set()

    win_path = DATA_DIR / "outlet_win_history.csv"
    addr_path = DATA_DIR / "outlets_with_addresses.csv"

    if win_path.exists():
        with open(win_path, newline="", encoding="utf-8") as f:
            all_wins = list(csv.DictReader(f))

    if addr_path.exists():
        with open(addr_path, newline="", encoding="utf-8") as f:
            all_outlets = list(csv.DictReader(f))
            done_names = {o["outlet_name"] for o in all_outlets}

    return all_wins, all_outlets, done_names


def main():
    print("=" * 60)
    print("STEP 2: Scrape Per-Outlet Winning History")
    print("=" * 60)

    outlets = load_outlets_list()
    if not outlets:
        return

    all_wins, all_outlets_enriched, done_names = load_existing_progress()
    remaining = [o for o in outlets if o["outlet_name"] not in done_names]

    print(f"Already scraped: {len(done_names)}, Remaining: {len(remaining)}")
    if not remaining:
        print("All outlets already scraped.")
        return

    print(f"Rate limit: {REQUEST_DELAY}s/request, ETA: ~{len(remaining) * REQUEST_DELAY / 60:.0f} min\n")

    failed: list[str] = []

    for i, outlet in enumerate(remaining):
        name = outlet["outlet_name"]
        url = outlet.get("detail_url", "")

        if not url or "lo_details" not in url:
            print(f"[{i+1}/{len(remaining)}] {name} -- no detail URL, skip")
            failed.append(name)
            continue

        print(f"[{i+1}/{len(remaining)}] {name}...", end=" ")
        detail, wins = scrape_outlet_detail(url, name)

        if detail is None:
            failed.append(name)
            print("FAILED")
        else:
            all_outlets_enriched.append({
                "outlet_name": name,
                "address": detail.get("address", ""),
                "postal_code": detail.get("postal_code", ""),
                "detail_url": url,
            })
            all_wins.extend(wins)
            postal_status = "yes" if detail.get("postal_code") else "no"
            print(f"OK (postal: {postal_status}, wins: {len(wins)})")

        if (i + 1) % 50 == 0:
            save_checkpoint(all_wins, all_outlets_enriched)
            print(f"  [Checkpoint] {len(all_wins)} wins saved")

        time.sleep(REQUEST_DELAY)

    save_checkpoint(all_wins, all_outlets_enriched)

    print(f"\n{'=' * 60}")
    print(f"Outlets processed: {len(all_outlets_enriched)}")
    print(f"With postal codes: {sum(1 for o in all_outlets_enriched if o['postal_code'])}")
    print(f"Win records: {len(all_wins)}")
    print(f"Failed: {len(failed)}")
    if failed:
        for name in failed[:10]:
            print(f"  - {name}")
    print(f"\nNext: Run 04_parse_gra_pdf.py or 05_download_supplementary.py")


if __name__ == "__main__":
    main()
