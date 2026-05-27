# Data Collection Pipeline

## Quick Start

```bash
python3 toto_scrapper.py
```

Optional (enables planning area lookup via OneMap API):
```bash
export ONEMAP_EMAIL='your@email.com'
export ONEMAP_PASSWORD='yourpassword'
```

OneMap API: https://www.onemap.gov.sg/apidocs/register

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP requests to Singapore Pools, GRA |
| `beautifulsoup4` | HTML parsing of Singapore Pools pages |
| `lxml` | Fast HTML parser backend for BeautifulSoup |
| `pdfplumber` | PDF table extraction from GRA outlet list |

Install all dependencies:
```bash
pip install -r requirements.txt
```

Standard library modules used: `csv`, `json`, `math`, `os`, `re`, `sys`, `time`, `collections`, `difflib`, `pathlib`, `urllib`.

---

## Pipeline Steps

### Step 1: Scrape Winning Outlets Aggregate Page

**Source:** `https://www.singaporepools.com.sg/en/product/Pages/toto_wo.aspx`

**Output:** `data/raw/outlets_list.csv`

| Column | Description |
|--------|-------------|
| `outlet_name` | Display name from Singapore Pools |
| `detail_url` | Full URL to the outlet's detail page |
| `group1_wins` | Number of TOTO Group 1 (jackpot) wins |
| `group2_wins` | Number of TOTO Group 2 wins |
| `combined_wins` | Total wins (Group 1 + Group 2) |

---

### Step 2: Scrape Per-Outlet Winning History

**Source:** Individual outlet detail pages (`lo_details.aspx?sppl=...`)

**Outputs:**
- `data/raw/outlet_win_history.csv` — one row per win event (~19,000 records)
- `data/raw/outlets_with_addresses.csv` — one row per outlet with address and postal code

---

### Step 3: Parse GRA PDF

**Source:** Gambling Regulatory Authority official outlet directory PDF

**Output:** `data/raw/gra_outlets.csv` (~304 outlets)

| Column | Description |
|--------|-------------|
| `sn` | Serial number from PDF |
| `outlet_name` | Official registered name |
| `full_address` | Concatenated building + street + unit |
| `building` | Building name |
| `street` | Street address |
| `unit` | Unit number |
| `postal_code` | 6-digit Singapore postal code |
| `outlet_type` | Categorized outlet type |

---

### Step 4: Download Supplementary Datasets

**Source:** `data.gov.sg` open data API

**Outputs in `data/supplementary/`:**

| File | Description |
|------|-------------|------|
| `hdb_dwelling_units_by_town.csv` | HDB units by town, flat type, FY2008–2021
| `census2020_pop_by_dwelling.csv` | Census population by planning area & dwelling type |
| `census2020_pop_by_age_sex.csv` | Census population by planning area, age, sex |
| `planning_area_boundary.geojson` | URA Master Plan 2019 planning area polygons |
| `subzone_boundary.geojson` | URA Master Plan 2019 subzone polygons |

---

### Step 5: Merge Data Sources

**Output:** `data/outlets_raw.csv` (~375 physical outlets)

---

### Step 6: Geocode via OneMap API

**Source:** OneMap Singapore Geocoding API

**Output:** `data/outlets_geocoded.csv`

Added columns:

| Column | Description |
|--------|-------------|
| `latitude` | WGS84 latitude |
| `longitude` | WGS84 longitude |
| `onemap_address` | Standardized address from OneMap |
| `planning_area` | URA planning area name (e.g., "BEDOK") |
| `x_svy21` | SVY21 X coordinate |
| `y_svy21` | SVY21 Y coordinate |
| `geocode_status` | "OK" or "FAILED" |

---

### Step 7: Compute Proxy Volumes & Build Final Dataset

**Stesp:**

1. **Planning Area Assignment:** For outlets missing a planning area, assigns the nearest planning area by computing Haversine distance to each planning area centroid (max 5km threshold).

2. **Region Assignment:** Maps each outlet's planning area to its URA region (e.g., "EAST REGION", "CENTRAL REGION") using GeoJSON properties.

3. **Area Type Classification:** Classifies each outlet as `residential` (planning area has HDB units) or `commercial` (planning area exists but has no HDB units).

4. **HDB Proxy Computation:** For each outlet, counts total HDB dwelling units within 4 radii (500m, 750m, 1km, 1.5km) using Haversine distance from the outlet to each planning area centroid. The proxy represents nearby residential density as an approximation for potential foot traffic and ticket sales volume.

5. **Win Rate Computation:** `win_rate_1000m = combined_wins / proxy_1000m`: wins per HDB unit within 1km, measuring outlet "luckiness" normalised by local population density.

6. **Validation Summary:** counts of residential vs commercial outlets, proxy coverage, region distribution and top 10 outlets by combined wins.

**Output:** `data/analysis_ready/outlets_final.csv`

| Column | Type | Description |
|--------|------|-------------|
| `outlet_name` | str | Outlet display name |
| `address` | str | Raw scraped address |
| `postal_code` | str | 6-digit Singapore postal code |
| `outlet_type` | str | GRA-derived type (e.g., "Branch", "Authorised Retailer") |
| `group1_wins` | int | TOTO Group 1 (jackpot) wins |
| `group2_wins` | int | TOTO Group 2 wins |
| `combined_wins` | int | Total wins |
| `source` | str | Data source: matched/scraped/aggregate_only/gra_only |
| `latitude` | float | WGS84 latitude |
| `longitude` | float | WGS84 longitude |
| `onemap_address` | str | Standardized address from OneMap |
| `planning_area` | str | URA planning area (uppercase) |
| `x_svy21` | float | SVY21 X coordinate |
| `y_svy21` | float | SVY21 Y coordinate |
| `geocode_status` | str | "OK" |
| `proxy_500m` | int | HDB units within 500m radius |
| `proxy_750m` | int | HDB units within 750m radius |
| `proxy_1000m` | int | HDB units within 1km radius |
| `proxy_1500m` | int | HDB units within 1.5km radius |
| `area_type` | str | "residential" or "commercial" |
| `region` | str | URA region (e.g., "EAST REGION") |
| `pa_hdb_units` | int | Total HDB units in the outlet's planning area |
| `win_rate_1000m` | float | combined_wins / proxy_1000m |

---

## HDB Town-to-Planning Area Mapping

The HDB dataset uses 27 town names while URA uses 55 planning areas. The mapping is mostly 1:1, with two special cases:

| HDB Town | Planning Area(s) |
|----------|-----------------|
| Central Area | DOWNTOWN CORE, MARINA SOUTH, MUSEUM, OUTRAM, RIVER VALLEY, ROCHOR |
| Kallang/Whampoa | KALLANG |

For "Central Area", HDB units are split equally across the 6 corresponding planning areas. All other towns map to a single planning area of the same name (uppercase).
