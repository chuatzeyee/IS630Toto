#!/usr/bin/env python3
"""
Step 3 (FALLBACK): Scrape winning outlets page using Playwright.
Use this if 01 fails because the page needs JavaScript.

Output: ../data/raw/outlets_list_playwright.csv
        ../data/raw/toto_wo_page_rendered.html
"""

import csv
import re
from pathlib import Path

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.singaporepools.com.sg"
WINNING_OUTLETS_URL = f"{BASE_URL}/en/product/Pages/toto_wo.aspx"


def scrape_with_playwright():
    print(f"Launching headless Chromium...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Navigating to {WINNING_OUTLETS_URL} ...")
        page.goto(WINNING_OUTLETS_URL, wait_until="networkidle", timeout=60000)

        load_more_clicks = 0
        while True:
            try:
                btn = page.locator("text=Load More").first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    load_more_clicks += 1
                    print(f"  Clicked 'Load More' ({load_more_clicks})")
                    page.wait_for_timeout(1500)
                else:
                    break
            except Exception:
                break

        try:
            show_all = page.locator("text=Show All").first
            if show_all.is_visible(timeout=2000):
                show_all.click()
                page.wait_for_timeout(3000)
        except Exception:
            pass

        html = page.content()
        browser.close()

    html_path = DATA_DIR / "toto_wo_page_rendered.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Saved rendered HTML ({len(html):,} bytes)")
    return html


def parse_outlets(html):
    soup = BeautifulSoup(html, "lxml")
    outlets = []

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
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
                    outlets.append({
                        "outlet_name": name,
                        "detail_url": href,
                        "group1_wins": counts[0] if len(counts) >= 1 else 0,
                        "group2_wins": counts[1] if len(counts) >= 2 else 0,
                        "combined_wins": counts[2] if len(counts) >= 3 else 0,
                    })

    if not outlets:
        for link in soup.find_all("a", href=re.compile(r"lo_details|sppl=")):
            name = link.get_text(strip=True)
            if not name or len(name) < 3:
                continue
            href = link.get("href", "")
            if href and not href.startswith("http"):
                href = BASE_URL + href
            outlets.append({
                "outlet_name": name, "detail_url": href,
                "group1_wins": 0, "group2_wins": 0, "combined_wins": 0,
            })

    seen = set()
    return [o for o in outlets if o["outlet_name"] not in seen and not seen.add(o["outlet_name"])]


def main():
    print("=" * 60)
    print("STEP 3: Scrape Winning Outlets (Playwright)")
    print("=" * 60)

    html = scrape_with_playwright()
    outlets = parse_outlets(html)
    print(f"\nFound {len(outlets)} unique outlets")

    if outlets:
        path = DATA_DIR / "outlets_list_playwright.csv"
        fields = ["outlet_name", "detail_url", "group1_wins", "group2_wins", "combined_wins"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(outlets)
        print(f"Saved to {path}")
        for i, o in enumerate(sorted(outlets, key=lambda x: x["combined_wins"], reverse=True)[:10], 1):
            print(f"  {i:2d}. {o['outlet_name'][:40]:<40s} Total={o['combined_wins']:>5d}")
    else:
        print("WARNING: No outlets found. Check toto_wo_page_rendered.html.")


if __name__ == "__main__":
    main()
