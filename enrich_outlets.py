#!/usr/bin/env python3

import csv
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
OUT_DIR = DATA_DIR / "analysis_ready"

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def parse_time_to_hours(s: str) -> float:
    s = s.strip().lower()
    m = re.match(r'(\d{1,2})[.:](\d{2})\s*(am|pm)', s)
    if not m:
        return -1.0
    h, mins, ampm = int(m.group(1)), int(m.group(2)), m.group(3)
    if ampm == "pm" and h != 12:
        h += 12
    if ampm == "am" and h == 12:
        h = 0
    return h + mins / 60.0


def format_time(hours_val: float) -> str:
    if hours_val < 0:
        return ""
    h = int(hours_val)
    m = int(round((hours_val - h) * 60))
    ampm = "am" if h < 12 else "pm"
    display_h = h if h <= 12 else h - 12
    if display_h == 0:
        display_h = 12
    return f"{display_h}.{m:02d} {ampm}"


def compute_earliest_win_years() -> dict[str, int]:
    path = RAW_DIR / "outlet_win_history.csv"
    if not path.exists():
        print("  [ERROR] outlet_win_history.csv not found")
        return {}

    earliest = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row["outlet_name"]
            date_str = row.get("draw_date", "")
            m = re.search(r'(\d{4})$', date_str)
            if not m:
                continue
            year = int(m.group(1))
            if name not in earliest or year < earliest[name]:
                earliest[name] = year

    print(f"  Computed earliest win year for {len(earliest)} outlets")
    print(f"  Range: {min(earliest.values())} to {max(earliest.values())}")
    return earliest


def scrape_operating_hours() -> dict[str, dict]:
    cache_path = RAW_DIR / "outlet_operating_hours.csv"

    done = {}
    if cache_path.exists():
        with open(cache_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done[row["outlet_name"]] = row

    with open(RAW_DIR / "outlets_list.csv", newline="", encoding="utf-8") as f:
        outlet_list = list(csv.DictReader(f))

    remaining = [o for o in outlet_list if o["outlet_name"] not in done]

    if not remaining:
        print(f"  All {len(done)} outlets already scraped")
        return done

    print(f"  Already scraped: {len(done)}, remaining: {len(remaining)}")
    print(f"  Rate limit: 2s/request, ETA: ~{len(remaining) * 2 / 60:.0f} min")

    for i, outlet in enumerate(remaining):
        name = outlet["outlet_name"]
        url = outlet.get("detail_url", "")

        if not url or "lo_details" not in url:
            done[name] = _empty_hours(name)
            continue

        try:
            resp = requests.get(url, headers=BROWSER_HEADERS, timeout=30)
            resp.raise_for_status()
        except requests.RequestException:
            done[name] = _empty_hours(name)
            if (i + 1) % 50 == 0:
                _save_hours_checkpoint(done)
            time.sleep(2.0)
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        hours = _extract_hours_from_soup(soup, name)
        done[name] = hours

        if (i + 1) % 50 == 0:
            _save_hours_checkpoint(done)
            print(f"  [{i+1}/{len(remaining)}] scraped...")

        time.sleep(2.0)

    _save_hours_checkpoint(done)
    print(f"  Scraped operating hours for {len(done)} outlets")
    return done


def _extract_hours_from_soup(soup, name: str) -> dict:
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        opening_row = None
        closing_row = None
        for row in rows:
            cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            if not cells:
                continue
            if cells[0].lower() == "opening":
                opening_row = cells[1:]
            elif cells[0].lower() == "closing":
                closing_row = cells[1:]

        if opening_row and closing_row:
            open_times = [parse_time_to_hours(t) for t in opening_row[:7]]
            close_times = [parse_time_to_hours(t) for t in closing_row[:7]]

            while len(open_times) < 7:
                open_times.append(-1.0)
            while len(close_times) < 7:
                close_times.append(-1.0)

            daily_hours = []
            for o, c in zip(open_times, close_times):
                if o >= 0 and c >= 0:
                    h = c - o
                    if h < 0:
                        h += 24
                    daily_hours.append(h)

            avg_hours = sum(daily_hours) / len(daily_hours) if daily_hours else 0.0
            valid_opens = [o for o in open_times if o >= 0]
            valid_closes = [c for c in close_times if c >= 0]
            varying = len(set(round(o, 2) for o in valid_opens)) > 1 or len(set(round(c, 2) for c in valid_closes)) > 1

            mode_open = max(set(valid_opens), key=valid_opens.count) if valid_opens else -1
            mode_close = max(set(valid_closes), key=valid_closes.count) if valid_closes else -1

            result = {"outlet_name": name}
            for j, day in enumerate(DAYS):
                result[f"open_{day}"] = format_time(open_times[j])
                result[f"close_{day}"] = format_time(close_times[j])
            result["open_time"] = format_time(mode_open)
            result["close_time"] = format_time(mode_close)
            result["open_hours_daily"] = round(avg_hours, 2)
            result["has_varying_hours"] = "1" if varying else "0"
            return result

    return _empty_hours(name)


def _empty_hours(name: str) -> dict:
    result = {"outlet_name": name}
    for day in DAYS:
        result[f"open_{day}"] = ""
        result[f"close_{day}"] = ""
    result["open_time"] = ""
    result["close_time"] = ""
    result["open_hours_daily"] = ""
    result["has_varying_hours"] = ""
    return result


def _save_hours_checkpoint(done: dict) -> None:
    path = RAW_DIR / "outlet_operating_hours.csv"
    rows = list(done.values())
    if not rows:
        return
    fields = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def enrich_geodata(hours: dict, earliest_years: dict) -> None:
    input_path = OUT_DIR / "outlets_geodata.csv"
    if not input_path.exists():
        print(f"  [ERROR] {input_path} not found. Run geospatial_analysis.py first.")
        return

    with open(input_path, newline="", encoding="utf-8") as f:
        outlets = list(csv.DictReader(f))

    for outlet in outlets:
        name = outlet["outlet_name"]

        year = earliest_years.get(name)
        outlet["earliest_win_year"] = year if year else ""
        outlet["years_winning"] = 2026 - year if year else ""

        h = hours.get(name, {})
        outlet["open_time"] = h.get("open_time", "")
        outlet["close_time"] = h.get("close_time", "")
        outlet["open_hours_daily"] = h.get("open_hours_daily", "")
        outlet["has_varying_hours"] = h.get("has_varying_hours", "")

    existing_fields = list(outlets[0].keys())
    new_fields = ["earliest_win_year", "years_winning", "open_time", "close_time", "open_hours_daily", "has_varying_hours"]
    fieldnames = [f for f in existing_fields if f not in new_fields] + new_fields

    with open(input_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(outlets)

    with_hours = sum(1 for o in outlets if o.get("open_hours_daily"))
    with_year = sum(1 for o in outlets if o.get("earliest_win_year"))
    print(f"  Enriched {len(outlets)} outlets: {with_hours} with hours, {with_year} with earliest win year")
    print(f"  Saved to {input_path}")


def main() -> None:
    print("=" * 70)
    print("  Enrich Outlets: Operating Hours + Earliest Win Year")
    print("=" * 70)
    start = time.time()

    print("\n[Step 1] Compute earliest win year from win history")
    earliest_years = compute_earliest_win_years()

    print("\n[Step 2] Scrape operating hours from Singapore Pools")
    hours = scrape_operating_hours()

    print("\n[Step 3] Merge into outlets_geodata.csv")
    enrich_geodata(hours, earliest_years)

    hrs_vals = [float(h["open_hours_daily"]) for h in hours.values() if h.get("open_hours_daily")]
    if hrs_vals:
        print(f"\n  Operating hours summary:")
        print(f"    Min: {min(hrs_vals):.1f}h, Max: {max(hrs_vals):.1f}h, Avg: {sum(hrs_vals)/len(hrs_vals):.1f}h")
        varying = sum(1 for h in hours.values() if h.get("has_varying_hours") == "1")
        print(f"    Uniform hours: {len(hrs_vals) - varying}, Varying by day: {varying}")

    if earliest_years:
        vals = sorted(earliest_years.values())
        print(f"\n  Earliest win year summary:")
        print(f"    Oldest: {vals[0]}, Newest: {vals[-1]}, Median: {vals[len(vals)//2]}")

    elapsed = time.time() - start
    print(f"\n  Completed in {elapsed:.0f}s")


if __name__ == "__main__":
    main()
