# TOTO Lucky Outlet -- Data Collection & Geospatial Analysis

IS630 group project investigating whether a Singapore Pools outlet's proximity to residential or commercial land use clusters predicts its TOTO winning frequency.

## Quick Start

```bash
pip install -r requirements.txt

python3 toto_scraper.py          # Step 1: scrape Singapore Pools + GRA
python3 build_dataset.py         # Step 2: download gov data, merge, geocode, proxy
python3 geospatial_analysis.py   # Step 3: land use profiling + neighborhood classification
```

Or run all at once:
```bash
python3 collect_all_data.py      # runs toto_scraper + build_dataset steps 1-7
python3 geospatial_analysis.py   # enriches with URA land use zoning data
```

---

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| `toto_scraper.py` | Scrape Singapore Pools winning outlets + GRA PDF | ~12 min (first run) |
| `build_dataset.py` | Download gov datasets, merge, geocode, compute HDB proxy | ~8 min (first run) |
| `geospatial_analysis.py` | Download URA land use + HDB building data, compute land use profiles | ~20s |
| `collect_all_data.py` | Thin orchestrator that runs toto_scraper + build_dataset | ~20 min (first run) |

All scripts are idempotent. If intermediate files exist, those steps are skipped.

---

## Data Pipeline

### Phase 1: Scraping (`toto_scraper.py`)

1. **Scrape aggregate page** -- outlet names, Group 1/2 win counts from Singapore Pools
2. **Scrape detail pages** -- per-outlet addresses, postal codes, win history (~19,000 records)
3. **Parse GRA PDF** -- official outlet directory with outlet types (~304 outlets)

### Phase 2: Dataset Building (`build_dataset.py`)

4. **Download supplementary data** -- HDB dwelling units, census population, planning area + subzone GeoJSON from data.gov.sg
5. **Merge sources** -- combines Singapore Pools, scraped details, and GRA via postal code + fuzzy matching, filters non-physical outlets
6. **Geocode** -- latitude/longitude via OneMap API (postal code lookup, address fallback)
7. **Compute proxies** -- HDB dwelling unit counts at 4 radii, planning area assignment, region, win rate

### Phase 3: Geospatial Analysis (`geospatial_analysis.py`)

8. **Download URA Master Plan 2019 Land Use** (~166MB, 113,212 zoning polygons)
9. **Download HDB Existing Building** (~54MB, 13,404 block footprints)
10. **Extract centroids** -- pre-process both GeoJSON files into lightweight CSVs for fast reuse
11. **Compute land use profiles** -- for each outlet at 500m, 1000m, 1500m radii:
    - Sum zoned area by category (residential, commercial, mixed, institutional, open)
    - Count HDB blocks
    - Compute residential-commercial ratio
12. **Classify neighborhoods** -- residential / commercial / mixed based on 1km land use ratio + HDB density
13. **Output `outlets_geodata.csv`** -- 375 outlets x 38 columns, analysis-ready

---

## Output Files

### `data/analysis_ready/outlets_geodata.csv` (primary analysis file)

375 outlets, 38 columns. This is the main dataset for statistical analysis.

**Outlet identity:**

| Column | Type | Description |
|--------|------|-------------|
| `outlet_name` | str | Display name |
| `postal_code` | str | 6-digit Singapore postal code |
| `outlet_type` | str | GRA type (Branch, Authorised Retailer, etc.) |
| `source` | str | matched / scraped / aggregate_only / gra_only |

**Win data:**

| Column | Type | Description |
|--------|------|-------------|
| `group1_wins` | int | TOTO Group 1 (jackpot) wins |
| `group2_wins` | int | TOTO Group 2 wins |
| `combined_wins` | int | Total wins |

**Location:**

| Column | Type | Description |
|--------|------|-------------|
| `latitude` | float | WGS84 latitude |
| `longitude` | float | WGS84 longitude |
| `onemap_address` | str | Standardised address from OneMap |
| `planning_area` | str | URA planning area (e.g. BEDOK) |
| `region` | str | URA region (e.g. EAST REGION) |

**Land use profile (per radius: 500m, 1000m, 1500m):**

| Column pattern | Type | Description |
|----------------|------|-------------|
| `res_area_{r}m` | int | Total residential-zoned area (sq m) within radius |
| `com_area_{r}m` | int | Total commercial/business-zoned area (sq m) |
| `mixed_area_{r}m` | int | Mixed commercial-residential area (sq m) |
| `inst_area_{r}m` | int | Institutional area (civic, education, healthcare) |
| `open_area_{r}m` | int | Open space + parks area (sq m) |
| `hdb_blocks_{r}m` | int | Count of HDB building blocks within radius |
| `rc_ratio_{r}m` | float | Residential share: res / (res + com), 0.0-1.0 |

**Classification:**

| Column | Type | Description |
|--------|------|-------------|
| `neighborhood_type` | str | residential / commercial / mixed (based on 1km) |
| `dominant_landuse_1000m` | str | Land use category with largest area at 1km |
| `landuse_diversity_1000m` | int | Count of distinct land use categories at 1km (1-5) |
| `win_rate_hdb_1000m` | float | combined_wins / hdb_blocks_1000m |

### `data/analysis_ready/outlets_final.csv` (legacy, from build_dataset.py)

375 outlets with HDB dwelling unit proxy. Superseded by `outlets_geodata.csv` for analysis.

---

## Land Use Categories

URA Master Plan 2019 has 33 zoning types. The script groups them into 6 categories:

| Category | URA Zoning Types |
|----------|-----------------|
| **residential** | RESIDENTIAL, RESIDENTIAL / INSTITUTION, RESIDENTIAL WITH COMMERCIAL AT 1ST STOREY |
| **commercial** | COMMERCIAL, COMMERCIAL / INSTITUTION, HOTEL, BUSINESS 1/2, BUSINESS PARK |
| **mixed** | COMMERCIAL & RESIDENTIAL |
| **institutional** | CIVIC & COMMUNITY INSTITUTION, EDUCATIONAL INSTITUTION, PLACE OF WORSHIP, HEALTH & MEDICAL CARE |
| **open** | OPEN SPACE, PARK, SPORTS & RECREATION, BEACH AREA |
| **infrastructure** | ROAD, TRANSPORT FACILITIES, MRT/LRT, UTILITY, WATERBODY, PORT / AIRPORT |

---

## Neighborhood Classification Rules

Based on the 1000m radius land use profile:

| Type | Criteria |
|------|----------|
| **residential** | rc_ratio >= 0.65 AND hdb_blocks >= 5 |
| **commercial** | rc_ratio <= 0.35 |
| **mixed** | Everything else |

The `rc_ratio` is computed as: `residential_area / (residential_area + commercial_area)`, where mixed-use area is split 50/50 between residential and commercial.

---

## Data Sources

| Dataset | Source | Size |
|---------|--------|------|
| TOTO winning outlets | Singapore Pools website | scraped |
| GRA approved outlets | Gambling Regulatory Authority PDF | scraped |
| HDB dwelling units by town | data.gov.sg `d_07b1eeeb22efdf7faf5bd6a13667359d` | 196 KB |
| Census 2020 population | data.gov.sg `d_7f243956483d5901f237e6f87b096636` | 18 KB |
| Planning area boundary | data.gov.sg `d_4765db0e87b9c86336792efe8a1f7a66` | 2.1 MB |
| Subzone boundary | data.gov.sg `d_8594ae9ff96d0c708bc2af633048edfb` | 3.2 MB |
| **URA Master Plan Land Use** | data.gov.sg `d_90d86daa5bfaa371668b84fa5f01424f` | **166 MB** |
| **HDB Existing Building** | data.gov.sg `d_16b157c52ed637edd6ba1232e026258d` | **54 MB** |

All government datasets are free and open under Singapore Open Data Licence.

---

## Directory Structure

```
toto-project/
  toto_scraper.py                     # scrape Singapore Pools + GRA
  build_dataset.py                    # merge, geocode, compute proxy
  geospatial_analysis.py              # URA land use profiling
  collect_all_data.py                 # orchestrator (steps 1-7)
  requirements.txt
  README.md
  data/
    raw/                              # scraped data (steps 1-3)
    supplementary/                    # government datasets (steps 4, 8-9)
      land_use_centroids.csv          # cached centroids (auto-generated)
      hdb_block_centroids.csv         # cached centroids (auto-generated)
    outlets_raw.csv                   # merged outlets (step 5)
    outlets_geocoded.csv              # geocoded outlets (step 6)
    analysis_ready/
      outlets_final.csv               # legacy output (step 7)
      outlets_geodata.csv             # primary analysis file (step 12)
```
