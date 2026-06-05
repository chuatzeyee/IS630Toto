#!/usr/bin/env python3
"""
Step 1: Scrape the TOTO winning outlets aggregate page.
Extracts all outlet names, Group 1/Group 2 win counts, and detail page URLs.

Source: https://www.singaporepools.com.sg/en/product/Pages/toto_wo.aspx
Rendering: Server-side HTML (BeautifulSoup works, no JS needed)

Output: ../data/raw/outlets_list.csv
"""

import csv
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.singaporepools.com.sg"
WINNING_OUTLETS_URL = f"{BASE_URL}/en/product/Pages/toto_wo.aspx"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_winning_outlets():
    print(f"Fetching {WINNING_OUTLETS_URL} ...")
    resp = requests.get(WINNING_OUTLETS_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    print(f"  Status: {resp.status_code}, Size: {len(resp.text):,} bytes")

    soup = BeautifulSoup(resp.text, "lxml")
    outlets = []

    # Strategy 1: Look for table rows with outlet links
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 3:
                link = cells[0].find("a")
                if link:
                    name = link.get_text(strip=True)
                    href = link.get("href", "")
                    if href and not href.startswith("http"):
                        href = BASE_URL + href

                    counts = []
                    for cell in cells[1:]:
                        text = cell.get_text(strip=True).replace(",", "")
                        if text.isdigit():
                            counts.append(int(text))

                    g1 = counts[0] if len(counts) >= 1 else 0
                    g2 = counts[1] if len(counts) >= 2 else 0
                    combined = counts[2] if len(counts) >= 3 else g1 + g2

                    outlets.append({
                        "outlet_name": name,
                        "detail_url": href,
                        "group1_wins": g1,
                        "group2_wins": g2,
                        "combined_wins": combined,
                    })

    # Strategy 2: Look for links to outlet detail pages (div-based layout)
    if not outlets:
        print("  Table strategy found nothing, trying link-based parsing...")
        all_links = soup.find_all("a", href=re.compile(r"lo_details\.aspx|sppl="))
        for link in all_links:
            name = link.get_text(strip=True)
            if not name or len(name) < 3:
                continue
            href = link.get("href", "")
            if href and not href.startswith("http"):
                href = BASE_URL + href

            parent = link.find_parent(["tr", "div", "li", "span"])
            counts = []
            if parent:
                for t in re.findall(r'\b(\d{1,5})\b', parent.get_text()):
                    counts.append(int(t))

            outlets.append({
                "outlet_name": name,
                "detail_url": href,
                "group1_wins": counts[0] if len(counts) >= 2 else 0,
                "group2_wins": counts[1] if len(counts) >= 2 else 0,
                "combined_wins": counts[2] if len(counts) >= 3 else 0,
            })

    # Deduplicate
    seen = set()
    unique = []
    for o in outlets:
        if o["outlet_name"] not in seen:
            seen.add(o["outlet_name"])
            unique.append(o)

    print(f"  Found {len(unique)} unique outlets")

    # Save raw HTML for debugging
    html_path = DATA_DIR / "toto_wo_page.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(resp.text)
    print(f"  Saved raw HTML to {html_path}")

    return unique


def save_outlets(outlets):
    output_path = DATA_DIR / "outlets_list.csv"
    fieldnames = ["outlet_name", "detail_url", "group1_wins", "group2_wins", "combined_wins"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(outlets)
    print(f"\nSaved {len(outlets)} outlets to {output_path}")
    return output_path


def main():
    print("=" * 60)
    print("STEP 1: Scrape TOTO Winning Outlets Aggregate Page")
    print("=" * 60)

    outlets = scrape_winning_outlets()

    if not outlets:
        print("\nWARNING: No outlets found via BeautifulSoup.")
        print("The page may need JavaScript. Try 03_scrape_outlets_playwright.py instead.")
    else:
        save_outlets(outlets)
        print(f"\nTop 10 outlets by combined wins:")
        sorted_outlets = sorted(outlets, key=lambda x: x["combined_wins"], reverse=True)
        for i, o in enumerate(sorted_outlets[:10], 1):
            print(f"  {i:2d}. {o['outlet_name'][:40]:<40s} G1={o['group1_wins']:>4d}  G2={o['group2_wins']:>4d}  Total={o['combined_wins']:>5d}")

    print(f"\nNext: Run 02_scrape_outlet_details.py for per-outlet win history")


if __name__ == "__main__":
    main()
