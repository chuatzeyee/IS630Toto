import csv
import re
import time
from pathlib import Path

import pdfplumber
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)

SP_BASE_URL = "https://www.singaporepools.com.sg"
SP_TOTO_URL = f"{SP_BASE_URL}/en/product/Pages/toto_wo.aspx"
GRA_PDF_URL = "https://www.gra.gov.sg/docs/default-source/betting-operations--lottery-and-game-of-chance/list-of-approved-singapore-pools-gambling-venuesf0fae72f-58d2-433f-abbe-2da61f8b6f22.pdf"

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def step1_scrape_aggregate() -> list[dict]:
    output_path = RAW_DIR / "outlets_list.csv"
    if output_path.exists():
        print(f"{output_path} already exists")
        with open(output_path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    print(f"  Fetching {SP_TOTO_URL} ...")
    resp = requests.get(SP_TOTO_URL, headers=BROWSER_HEADERS, timeout=30)
    resp.raise_for_status()

    html_path = RAW_DIR / "toto_wo_page.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(resp.text)

    soup = BeautifulSoup(resp.text, "lxml")
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
                        href = SP_BASE_URL + href
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

    if not outlets:
        all_links = soup.find_all("a", href=re.compile(r"lo_details\.aspx|sppl="))
        for link in all_links:
            name = link.get_text(strip=True)
            if not name or len(name) < 3:
                continue
            href = link.get("href", "")
            if href and not href.startswith("http"):
                href = SP_BASE_URL + href
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

    seen = set()
    unique = []
    for o in outlets:
        if o["outlet_name"] not in seen:
            seen.add(o["outlet_name"])
            unique.append(o)

    fieldnames = ["outlet_name", "detail_url", "group1_wins", "group2_wins", "combined_wins"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique)

    print(f"Exported {len(unique)} outlets to {output_path}")
    return unique


def step2_scrape_details(outlet_list: list[dict]) -> tuple[list[dict], list[dict]]:
    win_path = RAW_DIR / "outlet_win_history.csv"
    addr_path = RAW_DIR / "outlets_with_addresses.csv"

    if win_path.exists() and addr_path.exists():
        print(f"{win_path} and {addr_path} already exist")
        with open(win_path, newline="", encoding="utf-8") as f:
            all_wins = list(csv.DictReader(f))
        with open(addr_path, newline="", encoding="utf-8") as f:
            all_outlets = list(csv.DictReader(f))
        return all_wins, all_outlets

    all_wins: list[dict] = []
    all_outlets: list[dict] = []
    done_names: set[str] = set()

    if win_path.exists():
        with open(win_path, newline="", encoding="utf-8") as f:
            all_wins = list(csv.DictReader(f))
    if addr_path.exists():
        with open(addr_path, newline="", encoding="utf-8") as f:
            all_outlets = list(csv.DictReader(f))
            done_names = {o["outlet_name"] for o in all_outlets}

    remaining = [o for o in outlet_list if o["outlet_name"] not in done_names]
    print(f"Already scraped: {len(done_names)}, remaining: {len(remaining)}")

    if not remaining:
        return all_wins, all_outlets

    print(f"Rate limit: 2s/request, ETA: ~{len(remaining) * 2 / 60:.0f} min")

    for i, outlet in enumerate(remaining):
        name = outlet["outlet_name"]
        url = outlet.get("detail_url", "")

        if not url or "lo_details" not in url:
            print(f"  [{i+1}/{len(remaining)}] {name} -- no detail URL, skip")
            continue

        print(f"  [{i+1}/{len(remaining)}] {name}...", end=" ")

        try:
            resp = requests.get(url, headers=BROWSER_HEADERS, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"cannot ({e})")
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        address = ""
        postal_code = ""

        for tag in soup.find_all(["div", "span", "p", "td"]):
            text = tag.get_text(strip=True)
            if re.search(r'Singapore\s+\d{6}', text) and len(text) < 200:
                address = text
                m = re.search(r'Singapore\s+(\d{6})', text)
                if m:
                    postal_code = m.group(1)
                break

        wins = []
        for table in soup.find_all("table"):
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
                    "outlet_name": name,
                    "draw_date": draw_date,
                    "draw_number": int(draw_no_str),
                    "prize_amount": amount,
                    "bet_type": bet_type,
                    "prize_group": prize_group,
                })

        all_outlets.append({
            "outlet_name": name,
            "address": address,
            "postal_code": postal_code,
            "detail_url": url,
        })
        all_wins.extend(wins)
        print(f"OK (postal: {'yes' if postal_code else 'no'}, wins: {len(wins)})")

        if (i + 1) % 50 == 0:
            _save_detail_checkpoint(all_wins, all_outlets)

        time.sleep(2.0)

    _save_detail_checkpoint(all_wins, all_outlets)
    return all_wins, all_outlets


def _save_detail_checkpoint(all_wins: list[dict], all_outlets: list[dict]) -> None:
    if all_wins:
        fields = ["outlet_name", "draw_date", "draw_number", "prize_amount", "bet_type", "prize_group"]
        with open(RAW_DIR / "outlet_win_history.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(all_wins)
    if all_outlets:
        fields = ["outlet_name", "address", "postal_code", "detail_url"]
        with open(RAW_DIR / "outlets_with_addresses.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(all_outlets)


def step3_parse_gra() -> list[dict]:
    output_path = RAW_DIR / "gra_outlets.csv"
    if output_path.exists():
        print(f"{output_path} already exists")
        with open(output_path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    pdf_path = RAW_DIR / "gra_approved_outlets.pdf"
    if not pdf_path.exists():
        print(f"Downloading GRA PDF")
        try:
            resp = requests.get(GRA_PDF_URL, headers=BROWSER_HEADERS, timeout=30)
            resp.raise_for_status()
            with open(pdf_path, "wb") as f:
                f.write(resp.content)
            print(f"Saved ({len(resp.content):,} bytes)")
        except requests.RequestException as e:
            print(f"Download failed: {e}")
            print(f"Download manually and save as: {pdf_path}")
            return []

    outlets = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
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
                        combined = (outlet_name + " " + full_address).lower()
                        if "livewire" in combined:
                            otype = "Livewire"
                        elif "betting centre" in combined or "ocb" in combined:
                            otype = "Betting Centre"
                        elif "branch" in combined:
                            otype = "Branch"
                        elif "lobby" in combined:
                            otype = "Lottery Lobby"
                        elif "7-eleven" in combined or "7 eleven" in combined:
                            otype = "Authorised Retailer (7-Eleven)"
                        elif "fairprice" in combined or "ntuc" in combined:
                            otype = "Authorised Retailer (FairPrice)"
                        else:
                            otype = "Authorised Retailer"
                        outlets.append({
                            "sn": sn,
                            "outlet_name": outlet_name,
                            "full_address": full_address,
                            "building": building,
                            "street": street,
                            "unit": unit,
                            "postal_code": postal_code,
                            "outlet_type": otype,
                        })

    if not outlets:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                for line in text.split("\n"):
                    m = re.search(r'(\d{6})\s*$', line.strip())
                    if m:
                        outlets.append({
                            "sn": len(outlets) + 1,
                            "outlet_name": line.strip()[:50],
                            "full_address": line.strip(),
                            "building": "",
                            "street": "",
                            "unit": "",
                            "postal_code": m.group(1),
                            "outlet_type": "Authorised Retailer",
                        })

    fields = ["sn", "outlet_name", "full_address", "building", "street", "unit", "postal_code", "outlet_type"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(outlets)

    print(f"Extracted {len(outlets)} outlets to {output_path}")
    return outlets


def main() -> None:
    print("-" * 70)
    print("TOTO Scraper")
    print("-" * 70)
    start_time = time.time()

    print(f"\n{'-'*70}")
    print("Scrape TOTO Winning Outlets Aggregate Page")
    print(f"{'-'*70}")
    outlet_list = step1_scrape_aggregate()
    if not outlet_list:
        print("No outlets scraped.")
        raise SystemExit(1)
    print(f"Result: {len(outlet_list)} outlets")

    print(f"\n{'-'*70}")
    print("Scrape Per-outlet Winning History & Addresses")
    print(f"{'-'*70}")
    all_wins, scraped_outlets = step2_scrape_details(outlet_list)
    print(f"Result: {len(scraped_outlets)} outlets with addresses, {len(all_wins)} win records")

    print(f"\n{'-'*70}")
    print("Parse GRA PDF")
    print(f"{'-'*70}")
    gra_outlets = step3_parse_gra()
    print(f"Result: {len(gra_outlets)} GRA outlets")

    elapsed = time.time() - start_time
    print(f"\n{'-'*70}")
    print(f"{elapsed:.0f}s")
    print(f"{'-'*70}")


if __name__ == "__main__":
    main()