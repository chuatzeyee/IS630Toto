# Section 0: Title

**Do "Lucky" Singapore Pools Outlets Really Exist? A Statistical Analysis of TOTO Winning Patterns Across Outlets**

---

# Section 1: Abstract / Introduction

Singapore Pools TOTO is the nation's most popular lottery game, drawing twice weekly with jackpots regularly exceeding S$1 million. A persistent belief among Singaporean lottery players is that certain outlets are "luckier" than others -- that purchasing a ticket from a historically winning outlet increases one's chances of winning. Media coverage reinforces this perception by regularly spotlighting outlets such as Tong Aik Huat and Delisia Agency, which have produced multiple Group 1 winners. This project investigates whether the observed variation in winning frequency across Singapore Pools outlets can be attributed to genuine differences in "luck" or is instead fully explained by differences in ticket sales volume. Using web-scraped TOTO winning outlet data (Oct 2014 -- May 2026, ~1,200 draws, ~377 outlets), supplemented with HDB dwelling unit counts and population data as proxies for foot traffic, we apply six complementary statistical analyses: Poisson goodness-of-fit, volume-adjusted chi-squared tests, Bayesian Beta-Binomial modelling, spatial autocorrelation (Moran's I), Wald-Wolfowitz runs tests for streak analysis, and Mann-Whitney U non-parametric comparisons. We expect to demonstrate that after controlling for estimated sales volume, no outlet exhibits a statistically significant advantage -- the "lucky outlet" phenomenon is a product of the availability heuristic, the hot hand fallacy, and media amplification rather than any genuine spatial or temporal pattern in lottery outcomes. (218 words)

---

# Section 2: Problem, Motivation and Objectives

## 2a. Problem (Motivation and Objectives)

### i. Problem Definition

The Singapore Pools TOTO lottery (6/49 format) produces Group 1 and Group 2 winners at specific retail outlets across Singapore. A well-documented consumer belief holds that certain outlets are inherently "luckier" than others. This belief manifests as measurable behavioral changes: after an outlet sells a winning ticket, foot traffic and ticket sales at that outlet increase by 12-38% (Guryan & Kearney, 2008), persisting for up to 40 weeks. In Singapore, outlets like Tong Aik Huat (Yishun, 23 Group 1 wins) and Delisia Agency (Fu Lu Shou Complex, 26 Group 1 wins) are specifically sought out by players who believe purchasing from these outlets confers a higher probability of winning.

The core statistical question is straightforward: does the observed non-uniform distribution of wins across outlets exceed what would be expected given differences in ticket sales volume?

### ii. Motivation

This problem matters at three levels:

1. **Public financial literacy:** Singaporeans collectively spend over S$9 billion annually on Singapore Pools products. The "lucky outlet" belief encourages suboptimal purchasing behavior -- players travel to specific outlets, queue for hours during cascade draws, and increase spending based on a statistical misconception.

2. **Statistical thinking education:** The project is an ideal vehicle for demonstrating core IS630 concepts (hypothesis testing, distributions, Bayesian inference) in a context every Singaporean recognizes. It illustrates how cognitive biases distort the interpretation of probabilistic events.

3. **Media accountability:** Singapore media (The Straits Times, CNA, Mothership) routinely publish articles identifying "lucky" outlets without noting that these outlets simply serve more customers. This project provides an evidence-based counter-narrative.

### iii. Objectives

1. Scrape and compile a comprehensive dataset of TOTO winning outlets from October 2014 to present (~1,200 draws).
2. Construct volume proxies using HDB dwelling units and population density data to estimate relative ticket sales per outlet.
3. Apply six statistical tests spanning frequentist, Bayesian, parametric, and non-parametric methods to assess whether winning patterns deviate from volume-based expectations.
4. Determine whether any spatial or temporal clustering of wins exists beyond what population density predicts.
5. Communicate findings in a way that is accessible to a general audience while maintaining statistical rigour.

---

## 2b. Analytical Questions

| # | Analytical Question | Why It Matters |
|---|-------------------|---------------|
| AQ1 | Does the distribution of wins across outlets follow a Poisson model (consistent with equal per-ticket probability)? | Establishes baseline: are raw win counts consistent with randomness? |
| AQ2 | After adjusting for estimated sales volume, are Group 1 wins distributed proportionally across outlets? | The central test -- do "lucky" outlets simply sell more tickets? |
| AQ3 | Using Bayesian updating from a skeptical prior, do posterior win-rate distributions differ meaningfully between "reputed lucky" and other outlets? | Provides intuitive credible intervals and a probability statement for the public |
| AQ4 | Are winning outlets spatially clustered beyond what population density predicts? | Tests the geographic version of the myth ("Toa Payoh is a lucky area") |
| AQ5 | Do outlets that produce a winner show higher-than-expected winning rates in subsequent draws (hot hand effect)? | Directly tests the "winning streak" belief |
| AQ6 | Do volume-adjusted win rates differ between outlets in high-density and low-density areas? | Clean before/after comparison: raw vs adjusted provides the most persuasive visual |

These six questions collectively provide a comprehensive, multi-method answer to the overarching research question. Each maps to specific IS630 course content (Sessions 1-5) and uses Python-based statistical techniques.

---

## 2c. Context and Novelty

### i. Literature Review

The "lucky store" phenomenon was first rigorously studied by **Guryan and Kearney (2008)**, who used Texas Lottery Commission sales data to document a 12-38% increase in ticket sales at outlets that recently sold a winning ticket. This increase was highly localized, persisted for up to 40 weeks, and was larger in areas with more economically disadvantaged populations. The authors attributed this to consumers' erroneous belief that a ticket from the winning store has a higher probability of winning.

**Lien, Yuan and Zheng (2015)** extended this work using Chinese lottery marketplace data, finding that players simultaneously exhibit the Gambler's Fallacy when choosing numbers (avoiding recently drawn numbers) while believing in Lucky Stores when choosing outlets. This dual behavior is consistent with **Rabin's (2002)** formalization of the Law of Small Numbers: when perceived uncertainty about underlying probabilities is greater (as with store "luck"), the hot hand fallacy dominates; when perceived uncertainty is lower (as with number frequencies), the gambler's fallacy dominates.

The cognitive foundations trace to **Tversky and Kahneman (1974)**, who identified the availability heuristic (judging probability by ease of recall) and the representativeness heuristic (expecting small samples to mirror populations). **Gilovich, Vallone and Tversky (1985)** demonstrated that the "hot hand" in basketball is a misperception of random sequences, providing the direct analogy for our streak analysis.

More recently, **Boto-Garcia, Muniz-Fernandez and Perez (2025)** documented a "compatriot win effect" in the Spanish Christmas Lottery, where jackpot wins in a province increase subsequent lottery sales through media salience, consistent with the availability bias mechanism.

Statistical methods for lottery analysis have been developed by **Joe (1993)** on testing for uniformity in lottery data, **Genest, Lockhart and Stephens (2002)** on chi-squared goodness-of-fit for lottery numbers, and **Baker and McHale (2009, 2011)** on modelling demand in lottery markets.

In the Singapore context, **Subramaniam et al. (2017)** studied gambling profiles in Singapore but did not address outlet-level patterns. The **National Council on Problem Gambling (NCPG, 2021)** survey provides context on gambling prevalence.

**Note:** All cited papers will be verified and accessed through SMU Library tools (Scopus AI, Scite, SciSpace) as required by the course GenAI policy. The citations above identify papers for the team to locate and review through approved channels.

### ii. Our Approach

Our project differs from Guryan and Kearney (2008) in three key ways:

1. **No sales data, creative proxy:** The Texas study used actual sales volume data from the lottery commission. Singapore Pools does not publish per-outlet sales. We construct a novel volume proxy using HDB dwelling unit counts within a defined radius of each outlet, supplemented by planning area population data from SingStat Census 2020. This proxy approach is itself a contribution -- it demonstrates how to conduct volume-adjusted analysis when direct sales data is unavailable.

2. **Multi-method triangulation:** Rather than relying on a single regression approach, we apply six complementary statistical tests spanning frequentist, Bayesian, parametric, and non-parametric methods. If all six methods converge on the same conclusion, the finding is robust.

3. **Singapore-specific context:** No published academic study has applied this analysis to Singapore Pools TOTO data. While the "lucky outlet" topic has received extensive media coverage in Singapore, it has not been subjected to rigorous statistical analysis. Our project fills this gap.

### iii. Novelty and Timeliness

- **Practical significance:** The finding directly applies to the ~2.5 million Singaporeans who participate in lottery games. It provides an evidence-based response to a widely held misconception.
- **Methodological contribution:** The HDB dwelling unit proxy for ticket sales volume is novel and potentially replicable in other contexts where direct sales data is unavailable.
- **Timeliness:** TOTO jackpots continue to generate significant media attention, with the most recent S$10 million cascade draws attracting hours-long queues at specific outlets.

---

# Section 3: Data Sources

## 3a. Dataset and Variables

We use **four primary datasets** and **two supplementary datasets**, combined through geocoding and spatial joins.

### Dataset 1: TOTO Winning Outlet Records (Primary)

| Attribute | Detail |
|-----------|--------|
| **Source** | Singapore Pools website (web scraping) |
| **URL** | `https://www.singaporepools.com.sg/en/product/Pages/toto_wo.aspx` (aggregate); individual outlet detail pages at `/outlets/Pages/lo_details.aspx?sppl=<base64_outlet_id>` |
| **Format** | HTML tables, scraped to structured CSV/SQLite |
| **Date range** | 9 October 2014 (TOTO 6/49 format start) to present (~May 2026) |
| **Estimated rows** | ~10,000-12,000 winning outlet records (Group 1 + Group 2 combined, across ~1,200 draws and ~377 outlets) |
| **Estimated columns** | 8 (after extraction) |
| **Update frequency** | After each draw (Monday and Thursday) |

**How to extract:** Each outlet detail page (accessible via base64-encoded outlet ID in the `sppl` URL parameter) contains a table of all historical winning records for that outlet. The aggregate page at `toto_wo.aspx` lists all 377 outlets with Group 1 and Group 2 win counts, providing a master list with links to each detail page.

**Extraction pipeline:**
1. Scrape the aggregate winning outlets page (`toto_wo.aspx`) using BeautifulSoup (server-rendered HTML) to obtain the list of all outlet names and their detail page URLs.
2. For each outlet, follow the detail page link and scrape the per-draw winning history table.
3. Parse each row: draw date, draw number, prize amount, bet type, prize group (1 or 2).
4. Store in a SQLite database with a normalized schema (outlets table + wins table).

**Alternative extraction (draw-by-draw):** Scrape TOTO results pages (`toto_results.aspx?sppl=<base64_draw_number>`) for each draw. These pages list the winning outlet names and addresses for Group 1 and Group 2. The draw list page at `/DataFileArchive/Lottery/Output/toto_result_draw_list_en.html` provides all available draw numbers. This approach requires Playwright/Selenium as the results pages are JavaScript-rendered.

**Existing GitHub scrapers for reference:**
- `yongyct/singapore-pools-analysis` (Python, BeautifulSoup, includes geographic mapping)
- `mapattacker/toto` (Python, Selenium, SQLite output, includes geocoding)
- `ccie48715/Toto_Singapore` (fork of above, includes pre-scraped data files 2018-2021)
- `alphatrl/sg-lottery-scraper` (TypeScript, Puppeteer, most actively maintained as of May 2025, but scrapes results only, not outlet data)

Note: All existing scrapers are outdated and require updates (Python 2 syntax, deprecated Selenium API, HTTP URLs changed to HTTPS, changed CSS selectors). They serve as architectural references, not drop-in solutions.

---

### Dataset 2: Singapore Pools Outlet Directory (Primary)

| Attribute | Detail |
|-----------|--------|
| **Source** | Gambling Regulatory Authority (GRA) |
| **URL** | `https://www.gra.gov.sg` (under Betting Operations > Lottery and Game of Chance) |
| **Format** | PDF (7 pages, ~303 KB) |
| **Rows** | 294 approved outlets (as at 13 February 2026) |
| **Columns** | 6 |
| **Update frequency** | Periodic (historical versions: Oct 2025, Jul 2025, Jun 2025, May 2025, Jul 2024, Apr 2023) |

**How to extract:** Download the PDF from the GRA website. Use `tabula-py` or `pdfplumber` in Python to extract the tabular data. The PDF contains a structured table with serial numbers, building names, street names, unit numbers, outlet names, and postal codes.

**Outlet categories in the GRA list:**
- 3 Livewires
- 8 Betting Centres (OCB)
- 76 SPPL Branches
- 8 OCB Lottery Lobbies
- 1 Singapore Pools Lobby
- ~198 Authorised Retailers (7-Eleven, NTUC FairPrice, independent retailers)

**Note:** The winning outlets page lists 377 outlets (including some that have since closed), while the GRA list shows 294 currently active outlets. Historical GRA PDFs can track outlet openings/closures over the study period.

---

### Dataset 3: HDB Dwelling Units (Primary -- Volume Proxy)

| Attribute | Detail |
|-----------|--------|
| **Source** | data.gov.sg (Housing & Development Board) |
| **URL (by town)** | `https://data.gov.sg/datasets/d_07b1eeeb22efdf7faf5bd6a13667359d/view` |
| **URL (by block)** | `https://data.gov.sg/datasets/d_16b157c52ed637edd6ba1232e026258d/view` |
| **Format** | CSV (by town, 191 KB) / JSON (by block) |
| **Rows** | ~4,900 (by town); ~10,000+ blocks (by block) |
| **Date range** | FY 2008 to FY 2022 |

**How to extract:** Download directly from data.gov.sg as CSV/JSON. The by-town dataset provides aggregate dwelling unit counts per HDB town per year. The by-block dataset provides the number of flats (broken down by flat type) at each HDB block, along with block addresses, coordinates, year of completion, and building type.

**Why this dataset:** Singapore Pools does not publish per-outlet ticket sales data. Since ~80% of Singapore's resident population lives in HDB flats, the number of HDB dwelling units near an outlet serves as a reasonable proxy for residential foot traffic and, by extension, ticket sales volume. This proxy is the key methodological innovation of our project.

**Volume proxy construction:**
```
For each outlet i:
    proxy_volume_i = sum of HDB dwelling units within radius r of outlet i
    (test with r = 500m, 750m, 1000m, 1500m for sensitivity analysis)
```

---

### Dataset 4: Population by Planning Area (Primary)

| Attribute | Detail |
|-----------|--------|
| **Source** | data.gov.sg / Singapore Department of Statistics (SingStat) |
| **URL** | `https://data.gov.sg/datasets/d_7f243956483d5901f237e6f87b096636/view` (Census 2020, by dwelling type) |
| **Additional URLs** | By age group & sex (`d_d95ae740c0f8961a0b10435836660ce0`, 130.3 KB); By ethnic group & sex (`d_e7ae90176a68945837ad67892b898466`, 39.1 KB) |
| **Format** | CSV |
| **Boundaries** | URA Master Plan 2019 planning areas |
| **Rows** | Varies (24.8 KB to 237.3 KB depending on breakdown) |

**How to extract:** Download CSVs directly from data.gov.sg. The Census 2020 data provides population counts by planning area and subzone, which we use for geographic-level analysis (Thread 4) and as an independent variable for density classification (Thread 6).

---

### Dataset 5: URA Planning Area Boundaries (Supplementary)

| Attribute | Detail |
|-----------|--------|
| **Source** | data.gov.sg / Urban Redevelopment Authority (URA) |
| **URL** | `https://data.gov.sg/datasets/d_4765db0e87b9c86336792efe8a1f7a66/view` (planning area, no sea) |
| **Additional** | Subzone boundary (`d_8594ae9ff96d0c708bc2af633048edfb`); Region boundary (`d_bf4d24df9129d5a8ff8cf82e20959ee0`) |
| **Format** | GeoJSON |
| **CRS** | WGS84 (EPSG:4326) |

**How to extract:** Download GeoJSON files from data.gov.sg. Load into Python using `geopandas.read_file()`. Use for spatial joins (assigning outlets to planning areas) and for choropleth map visualizations.

---

### Dataset 6: Geocoded Outlet Coordinates (Supplementary -- Derived)

| Attribute | Detail |
|-----------|--------|
| **Source** | OneMap API (free, by Singapore Land Authority) |
| **API endpoint** | `GET https://www.onemap.gov.sg/api/common/elastic/search?searchVal=<POSTAL_CODE>&returnGeom=Y&getAddrDetails=Y` |
| **Authentication** | Free registration at `https://developers.onemap.sg/signup/`; token via `POST /api/auth/post/getToken` |
| **Response fields** | LATITUDE, LONGITUDE, BUILDING, ROAD_NAME, POSTAL, X (SVY21), Y (SVY21) |
| **Planning area lookup** | `GET /api/public/popapi/getPlanningArea?lat=<LAT>&lon=<LON>&year=2019` |

**How to extract:** For each of the ~294-377 outlets, use the postal code from the GRA PDF or scraped outlet page to query the OneMap Search API. The API returns WGS84 latitude/longitude coordinates, which are then used for:
1. Spatial joins with URA planning area boundaries
2. Proximity calculations to HDB blocks (for computing the dwelling unit proxy)
3. Map visualizations

**Python client libraries:** `pip install pyonemap` or `pip install onemapsg`.

---

### ii. Data Dictionary

#### Table: `outlets`

| Variable | Type | Description | Source |
|----------|------|-------------|--------|
| `outlet_id` | Integer (PK) | Unique identifier (from Singapore Pools base64 ID) | Singapore Pools |
| `outlet_name` | Text | Registered outlet name (e.g., "Tong Aik Huat") | Singapore Pools / GRA |
| `address` | Text | Full street address including building name | Singapore Pools / GRA |
| `postal_code` | Text (6 digits) | Singapore postal code | GRA PDF |
| `latitude` | Float | WGS84 latitude coordinate | OneMap API |
| `longitude` | Float | WGS84 longitude coordinate | OneMap API |
| `planning_area` | Text | URA planning area name (e.g., "Yishun", "Bedok") | OneMap API / spatial join |
| `outlet_type` | Categorical | "Branch" / "Authorised Retailer" / "Betting Centre" / "Livewire" / "OCB Lottery Lobby" | GRA PDF |
| `is_active` | Boolean | Whether outlet is currently operating | Cross-ref GRA PDFs |
| `proxy_volume_500m` | Integer | HDB dwelling units within 500m radius | Derived (HDB data + spatial) |
| `proxy_volume_1000m` | Integer | HDB dwelling units within 1000m radius | Derived (HDB data + spatial) |
| `proxy_volume_1500m` | Integer | HDB dwelling units within 1500m radius | Derived (HDB data + spatial) |
| `planning_area_pop` | Integer | Total population of the outlet's planning area | Census 2020 |
| `planning_area_density` | Float | Population per sq km in outlet's planning area | Derived (Census / URA area) |

#### Table: `draws`

| Variable | Type | Description | Source |
|----------|------|-------------|--------|
| `draw_id` | Integer (PK) | TOTO draw number (e.g., 3238, 4167) | Singapore Pools |
| `draw_date` | Date | Date of draw (YYYY-MM-DD) | Singapore Pools |
| `day_of_week` | Categorical | "Monday" / "Thursday" / "Friday" (special draws) | Derived |
| `winning_numbers` | Text | Comma-separated 6 winning numbers | Singapore Pools results page |
| `additional_number` | Integer | The additional (bonus) number | Singapore Pools results page |
| `group1_prize` | Float | Group 1 prize amount in S$ | Singapore Pools results page |
| `group1_winners` | Integer | Number of Group 1 winning shares | Singapore Pools results page |
| `is_cascade` | Boolean | Whether this was a cascade/snowball draw | Derived (from prize amount pattern) |

#### Table: `wins` (the core analysis table)

| Variable | Type | Description | Source |
|----------|------|-------------|--------|
| `win_id` | Integer (PK) | Auto-incremented unique ID | Generated |
| `draw_id` | Integer (FK) | References `draws.draw_id` | Singapore Pools |
| `outlet_id` | Integer (FK) | References `outlets.outlet_id` | Singapore Pools |
| `prize_group` | Integer | 1 (Group 1 / jackpot) or 2 (Group 2) | Singapore Pools outlet detail page |
| `prize_amount` | Float | Prize share amount in S$ | Singapore Pools outlet detail page |
| `bet_type` | Categorical | "Ordinary" / "QuickPick" / "System 7" / ... / "System 12" / "System Roll" / "iTOTO" | Singapore Pools outlet detail page |
| `draw_date` | Date | Denormalized for convenience | Singapore Pools |

#### Derived Analysis Variables (computed from the above)

| Variable | Type | Description | Formula |
|----------|------|-------------|---------|
| `wins_g1` | Integer | Total Group 1 wins per outlet | `COUNT(wins WHERE prize_group=1) GROUP BY outlet_id` |
| `wins_g2` | Integer | Total Group 2 wins per outlet | `COUNT(wins WHERE prize_group=2) GROUP BY outlet_id` |
| `wins_total` | Integer | Total wins (G1+G2) per outlet | `wins_g1 + wins_g2` |
| `adjusted_win_rate` | Float | Volume-adjusted win rate | `wins_total / proxy_volume_1000m` |
| `density_group` | Categorical | "High" / "Medium" / "Low" based on planning area population density tertiles | `pd.qcut(planning_area_density, q=3)` |
| `is_lucky_reputed` | Boolean | Whether outlet is frequently cited in media as "lucky" | Manual labelling from media articles |

---

## 3b. Data Quality and Preparation

### i. Data Quality Issues

| Issue | Dataset | Severity | Description |
|-------|---------|----------|-------------|
| **Online betting entries** | Winning outlets | High | "Singapore Pools Account Betting Service" appears as the #1 outlet (236 Group 1, 1,323 Group 2 wins) but is not a physical location. Must be **excluded** from all spatial analyses. Similarly, "iTOTO" entries represent online/system bets. |
| **Closed outlets** | Winning outlets / GRA | Medium | Some of the 377 outlets on the winning page may have since closed. The GRA list shows 294 active outlets. Historical GRA PDFs (2023-2026) can identify closure dates. Closed outlets should be retained in the analysis with a flag, not dropped. |
| **Missing geocoding matches** | OneMap | Medium | Some outlet addresses (especially in commercial complexes like "Fu Lu Shou Complex" or "Lucky Plaza") may not geocode cleanly via postal code alone. Manual verification needed for ~5-10% of outlets. |
| **Volume proxy imprecision** | HDB dwelling units | Medium | The HDB proxy underestimates foot traffic for outlets in commercial/tourist areas (Orchard, CBD, Chinatown) where transient visitors, not residents, drive ticket sales. Outlets in these areas will appear to have anomalously high win rates after volume adjustment. We flag these as known limitations. |
| **Bet type confounding** | Winning outlets | Low | System bets (System 7-12, System Roll) generate more winning combinations per bet. Outlets favored by system bettors may produce more wins per nominal "ticket." We include bet type as a variable but note this as a limitation. |
| **Census data staleness** | Census 2020 | Low | Population data is from 2020; TOTO data spans 2014-2026. Population distribution shifts over this period (e.g., new Tengah town). We use the most recent available data and acknowledge this limitation. |
| **No duplicate records expected** | All | Low | Each winning record is a unique draw-outlet-prize_group combination. However, one outlet can win multiple groups in the same draw (rare but possible). These are distinct records, not duplicates. |

### ii. Data Cleaning and Transformation

**Step 1: Scraping and initial cleaning**
- Remove "Singapore Pools Account Betting Service" and "iTOTO" entries from spatial analysis (retain for aggregate statistics with a flag)
- Standardize outlet names across datasets (Singapore Pools website vs GRA PDF may use slightly different names)
- Parse dates to consistent `YYYY-MM-DD` format
- Extract prize group and bet type from text fields using regex

**Step 2: Geocoding**
- Batch geocode all outlet postal codes via OneMap API
- Manually verify outlets with no match or multiple matches
- Project coordinates to SVY21 (EPSG:3414) for distance calculations in meters
- Spatial join with URA planning area boundaries to assign each outlet to a planning area

**Step 3: Volume proxy computation**
- For each outlet, compute a circular buffer at 500m, 750m, 1000m, and 1500m radii (in SVY21 projection)
- Count total HDB dwelling units within each buffer using spatial intersection with HDB block locations
- Store all four radius values for sensitivity analysis

**Step 4: Merge and enrich**
- Join Census 2020 population data by planning area
- Compute planning area density (population / land area from URA boundary geometry)
- Classify outlets into density tertiles
- Flag "reputed lucky" outlets based on media mentions (manual labelling)

**Step 5: Construct analysis-ready views**
- `outlet_summary`: one row per outlet with total wins, proxy volumes, planning area, density group
- `draw_outlet_matrix`: one row per (draw, outlet) pair with binary win indicator (for time series / streak analysis)
- `area_summary`: one row per planning area with aggregated wins, population, density

### iii. How Multiple Datasets Are Combined

The four primary datasets are linked through a geocoding-and-spatial-join pipeline:

```
Singapore Pools Website          GRA PDF
(outlet names, win history)      (outlet names, addresses, postal codes)
         |                               |
         +---------- Name match ---------+
                        |
                  Unified Outlet List
                  (name, address, postal code, win history)
                        |
                  OneMap API Geocoding
                  (postal code -> latitude, longitude)
                        |
              +-------- Spatial Join --------+
              |                              |
    URA GeoJSON Boundaries          HDB Block Locations
    (planning area assignment)      (dwelling unit proxy)
              |                              |
              +---------- Merge -------------+
                        |
                Census 2020 Population
                (by planning area)
                        |
                Analysis-Ready Dataset
```

**Join keys:**
- Singapore Pools <-> GRA: outlet name (fuzzy match) + postal code (exact match)
- Outlet <-> Planning Area: spatial containment (point-in-polygon)
- Outlet <-> HDB blocks: spatial proximity (buffer intersection)
- Outlet <-> Census: planning area name (exact match after spatial join)

**Key assumption:** Each outlet's ticket sales volume is proportional to the number of HDB dwelling units within a 1km radius. This assumption is tested via sensitivity analysis across multiple radii (500m-1500m) and validated by checking whether the volume-adjusted chi-squared test results are robust to radius choice.

---

## 3c. Data Extraction Technical Details

### Scraping Architecture

The Singapore Pools website is built on Microsoft SharePoint 2013/2016 (identified by the `/_layouts/15/` path pattern). Two different rendering modes require different scraping tools:

| Page Type | Rendering | Scraping Tool | Reason |
|-----------|-----------|---------------|--------|
| Winning outlets aggregate (`toto_wo.aspx`) | Server-side HTML | BeautifulSoup (`requests` + `bs4`) | All 377 outlets pre-rendered in page HTML |
| Outlet detail pages (`lo_details.aspx`) | Server-side HTML | BeautifulSoup | Winning history tables are in the static HTML response |
| TOTO results per draw (`toto_results.aspx`) | JavaScript-rendered | Playwright / Selenium | Page template is a shell; actual draw data loads via AJAX |
| Outlet locator (`lo.aspx`) | JavaScript-rendered | Playwright / Selenium | Results load dynamically |
| Draw list archive (`/DataFileArchive/`) | Static HTML | BeautifulSoup | Simple HTML page listing draw numbers |

### Recommended Scraping Pipeline

```
Phase 1: Outlet List (BeautifulSoup, ~10 minutes)
  1. GET toto_wo.aspx -> parse all outlet rows
  2. Extract: outlet_name, detail_page_url, group1_count, group2_count

Phase 2: Per-Outlet Win History (BeautifulSoup, ~2 hours for 377 outlets)
  For each outlet in Phase 1:
    3. GET lo_details.aspx?sppl=<base64_id> -> parse winning history table
    4. Extract: draw_date, draw_number, prize_amount, bet_type, prize_group
    5. Rate limit: 1 request per 2 seconds (~750 requests total)

Phase 3: GRA Outlet List (PDF parsing, ~5 minutes)
  6. Download GRA PDF -> extract table with tabula-py or pdfplumber
  7. Parse: serial_number, building, street, unit, outlet_name, postal_code

Phase 4: Geocoding (OneMap API, ~30 minutes for 377 outlets)
  8. For each outlet postal code: query OneMap Search API
  9. Store: latitude, longitude, building, road_name
  10. Rate limit: 1 request per second

Phase 5: Supplementary Data (direct download, ~5 minutes)
  11. Download HDB dwelling units CSV/JSON from data.gov.sg
  12. Download Census 2020 population CSVs from data.gov.sg
  13. Download URA planning area GeoJSON from data.gov.sg

Phase 6: Data Integration (Python, ~1 hour)
  14. Spatial join outlets to planning areas (geopandas point-in-polygon)
  15. Compute HDB dwelling unit proxy per outlet per radius
  16. Merge Census population data by planning area
  17. Build analysis-ready SQLite database
```

**Estimated total coding time:** ~14 hours for the complete pipeline (scraping + geocoding + integration).

### Ethical Considerations

- Singapore Pools does not have a `robots.txt` entry explicitly disallowing scraping of results/outlet pages
- We scrape only publicly available information that any user can access through a browser
- Rate limiting (1-2 second delays between requests) ensures minimal impact on their servers
- Data is used strictly for academic research purposes under SMU's educational framework

---

## 3d. Proposed Database Schema (SQLite)

```sql
CREATE TABLE outlets (
    outlet_id       INTEGER PRIMARY KEY,
    outlet_name     TEXT NOT NULL,
    address         TEXT,
    postal_code     TEXT,
    latitude        REAL,
    longitude       REAL,
    planning_area   TEXT,
    outlet_type     TEXT,
    is_physical     BOOLEAN DEFAULT 1,
    is_active       BOOLEAN DEFAULT 1
);

CREATE TABLE draws (
    draw_id         INTEGER PRIMARY KEY,
    draw_date       DATE NOT NULL,
    day_of_week     TEXT,
    winning_numbers TEXT,
    additional_num  INTEGER,
    group1_prize    REAL,
    group1_winners  INTEGER,
    is_cascade      BOOLEAN DEFAULT 0
);

CREATE TABLE wins (
    win_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_id         INTEGER REFERENCES draws(draw_id),
    outlet_id       INTEGER REFERENCES outlets(outlet_id),
    prize_group     INTEGER CHECK (prize_group IN (1, 2)),
    prize_amount    REAL,
    bet_type        TEXT,
    UNIQUE(draw_id, outlet_id, prize_group, bet_type)
);

CREATE TABLE outlet_volumes (
    outlet_id       INTEGER REFERENCES outlets(outlet_id),
    radius_m        INTEGER,
    hdb_units       INTEGER,
    PRIMARY KEY (outlet_id, radius_m)
);

CREATE TABLE planning_areas (
    area_name       TEXT PRIMARY KEY,
    population      INTEGER,
    land_area_sqkm  REAL,
    density         REAL
);
```

---

# Section 4: Methodology and Results

## 4a. Approach / Methodology

We design six statistical analysis threads, each assigned to one team member, collectively covering frequentist and Bayesian approaches, parametric and non-parametric tests, and spatial and temporal dimensions. All analyses use Python with `scipy.stats`, `statsmodels`, `geopandas`, and standard data science libraries.

### Thread 1: Poisson Goodness-of-Fit (Member A -- Session 3: Distributions)

**Question:** Do wins follow a Poisson distribution across outlets, as would be expected if all outlets have equal per-ticket winning probability?

**Hypotheses:**
- H_0: X_i ~ Poisson(lambda), where lambda = total_wins / n_outlets
- H_1: X_i does not follow Poisson(lambda)

**Method:** Chi-squared goodness-of-fit test. Bin outlets by win count (0, 1, 2, ..., 5+), compute expected frequencies from Poisson(lambda) PMF, compare observed vs expected. Also compute the dispersion index (Var/Mean); Poisson requires this to equal 1.

**Python:** `scipy.stats.chisquare()`, `scipy.stats.poisson.pmf()`

**Expected result:** Reject H_0 (overdispersion). This sets up the puzzle: wins are not uniform, but is it luck or volume?

**Visualizations:** Observed histogram overlaid with Poisson PMF; observed vs expected bar chart.

---

### Thread 2: Chi-Squared Volume-Adjusted Test (Member B -- Session 5: Hypothesis Testing)

**Question:** After adjusting for estimated sales volume, are Group 1 wins distributed proportionally across outlets?

**Hypotheses:**
- H_0: Wins at outlet i are proportional to its estimated volume (p_i = v_i / sum(v_i))
- H_1: Some outlets deviate significantly from volume-based expectations

**Method:** Chi-squared test with expected counts E_i = total_wins x (v_i / sum(v_i)). Monte Carlo simulation for p-value (robust when many E_i < 5). Sensitivity analysis across proxy radii (500m, 750m, 1000m, 1500m).

**Python:** `scipy.stats.chisquare()`, `numpy.random.multinomial()` for Monte Carlo

**Expected result:** Fail to reject H_0 after volume adjustment -- volume explains the variation.

**Visualizations:** Scatter plot (proxy volume vs wins, with R-squared); residual analysis; sensitivity chart across radii.

---

### Thread 3: Bayesian Beta-Binomial Analysis (Member C -- Sessions 3+4: Distributions + Intervals)

**Question:** Starting from a skeptical prior, does the data shift beliefs enough to distinguish "lucky" from "unlucky" outlets?

**Framework:**
- Prior: theta_i ~ Beta(alpha_0, beta_0) for all outlets
- Likelihood: X_i | theta_i ~ Binomial(n_i, theta_i)
- Posterior: theta_i | X_i ~ Beta(alpha_0 + x_i, beta_0 + n_i - x_i)
- Decision: Compute P(theta_lucky > theta_other | data) via Monte Carlo sampling

**Python:** `scipy.stats.beta`, Monte Carlo sampling with `numpy`

**Expected result:** P(theta_lucky > theta_other | data) near 0.5 -- no evidence of differential luck. Prior sensitivity analysis (uninformative, weak, strong skeptical) shows convergence.

**Visualizations:** Prior vs posterior density plots; forest plot of credible intervals; prior sensitivity chart.

---

### Thread 4: Geographic Clustering / Moran's I (Member D -- Sessions 2+5: EDA + Chi-squared)

**Question:** Are winning outlets spatially clustered beyond what population density predicts?

**Hypotheses:**
- H_0: Residuals (observed - expected wins per area) show no spatial autocorrelation (Moran's I near 0)
- H_1: Residuals show spatial clustering

**Method:** Aggregate wins by planning area. Chi-squared test (observed vs population-proportional expected). Moran's I spatial autocorrelation on standardized residuals using Queen contiguity weights.

**Python:** `libpysal.weights.Queen`, `esda.moran.Moran`, `geopandas` for mapping

**Expected result:** Chi-squared significant (dense areas win more), but Moran's I not significant on residuals (no spatial "luck" beyond density).

**Visualizations:** Three choropleth maps (observed wins, population, residuals); Moran scatter plot; LISA cluster map.

---

### Thread 5: Streak / Hot Hand Analysis (Member E -- Sessions 3+5: Independence + Non-parametric)

**Question:** Do outlets that produce a winner continue to produce winners at higher-than-expected rates in subsequent draws?

**Hypotheses:**
- H_0: Win sequence at each outlet is random (number of runs is consistent with independence)
- H_1: Win sequences show clustering (fewer runs than expected = hot hand)

**Method:** Wald-Wolfowitz runs test on each outlet's binary win sequence. Conditional probability comparison: P(win in next k draws | recent win) vs P(win | no recent win), tested via two-proportion z-test.

**Python:** Custom runs test function, `statsmodels.stats.proportion.proportions_ztest()`

**Expected result:** ~5% of outlets show significant non-randomness (consistent with Type I error rate). No aggregate hot hand effect.

**Visualizations:** Win timelines for top outlets; distribution of p-values (should be uniform under H_0); conditional probability comparison.

---

### Thread 6: Mann-Whitney U Non-Parametric Comparison (Member F -- Session 5: Non-parametric)

**Question:** Do volume-adjusted win rates differ between high-density and low-density outlet locations?

**Hypotheses:**
- H_0: F_high(x) = F_low(x) (same distribution of adjusted win rates)
- H_1: F_high(x) != F_low(x)

**Method:** Mann-Whitney U test comparing adjusted_win_rate between density groups. Kruskal-Wallis extension to three groups. Bootstrap 95% CI for difference in medians.

**Python:** `scipy.stats.mannwhitneyu()`, `scipy.stats.kruskal()`, bootstrap with `numpy`

**Expected result:** Raw comparison (significant) vs adjusted comparison (not significant) provides the clearest demonstration that volume, not luck, drives the difference.

**Visualizations:** Side-by-side box plots (raw vs adjusted); violin plots; bootstrap median difference histogram with CI.

---

### Thread-to-IS630-Session Mapping Summary

| Thread | IS630 Session | Statistical Technique | Freq/Bayes |
|--------|--------------|----------------------|------------|
| 1. Poisson GOF | Session 3 (Distributions) | Chi-squared GOF, dispersion index | Frequentist |
| 2. Volume-adjusted chi-sq | Session 5 (Hypothesis Testing) | Chi-squared homogeneity, Monte Carlo | Frequentist |
| 3. Bayesian Beta-Binomial | Sessions 3+4 (Dist + CI) | Conjugate Beta-Binomial, posterior comparison | Bayesian |
| 4. Geographic clustering | Sessions 2+5 (EDA + Chi-sq) | Moran's I, chi-squared | Frequentist |
| 5. Streak analysis | Sessions 3+5 (Independence + Non-param) | Runs test, two-proportion z-test | Frequentist |
| 6. Mann-Whitney U | Session 5 (Non-parametric) | Mann-Whitney U, Kruskal-Wallis, bootstrap | Frequentist |

---

# Section 5: Conclusion / Summary

## Expected Key Findings

1. **Raw wins are NOT uniformly distributed** (Thread 1 -- Poisson test rejects). Some outlets clearly produce more winners than others. This is the observation that fuels the "lucky outlet" myth.

2. **Volume explains the variation** (Thread 2 -- chi-squared fails to reject after adjustment). Once we account for estimated ticket sales volume, the distribution of wins matches volume-based expectations. "Lucky" outlets are simply high-volume outlets.

3. **Bayesian analysis confirms no differential luck** (Thread 3). Starting from any reasonable prior, the posterior distributions for "lucky" and "other" outlets converge. P(lucky > other) near 0.5.

4. **No geographic luck factor** (Thread 4). Wins track population density. Moran's I on residuals is not significant. "Lucky neighborhoods" are simply densely populated areas.

5. **No hot hand / winning streaks** (Thread 5). The runs test shows outlet win sequences are consistent with randomness. The proportion of "non-random" outlets (~5%) matches the expected Type I error rate.

6. **Volume is the sole driver** (Thread 6). The raw vs adjusted Mann-Whitney comparison provides the most visually compelling evidence: high-density outlets win more in raw counts, but per-ticket win rates are statistically identical.

## Recommendations

1. **For consumers:** Buying a TOTO ticket from any outlet gives you the same probability of winning. Travelling to a "lucky" outlet wastes time without improving your odds. The only factor that changes your odds is the number of tickets you buy.

2. **For media:** When reporting on lottery wins, include context about outlet sales volume. Stating that "Outlet X has produced Y jackpot winners" without noting that it serves Z times more customers than an average outlet is misleading.

3. **For Singapore Pools:** Consider publishing aggregate sales data by outlet or region, which would allow researchers and the public to directly verify the volume explanation. Alternatively, include a footnote on the "winning outlets" page explaining that win frequency correlates with ticket sales volume.

## Limitations

1. **Volume proxy, not actual sales:** The HDB dwelling unit proxy underestimates foot traffic for outlets in commercial/tourist areas and overestimates for residential areas with low lottery participation. Direct sales data from Singapore Pools would be ideal but is not publicly available.

2. **Census data point-in-time:** Population data from Census 2020 may not fully reflect conditions across the entire 2014-2026 study period.

3. **System bet confounding:** System bets generate more winning combinations per entry. If certain outlets attract disproportionately more system bettors, their win counts would be inflated relative to simple ticket counts.

4. **Self-fulfilling prophecy:** The "lucky outlet" belief itself increases foot traffic (and thus sales and wins) at reputed outlets, creating a feedback loop that strengthens the myth. Our cross-sectional analysis cannot fully disentangle this endogeneity.

## Future Work

- Obtain actual sales data from Singapore Pools (via PDPA request or research collaboration) to validate the proxy approach.
- Extend analysis to 4D results for a robustness check across lottery products.
- Conduct a survey of TOTO buyers to quantify the prevalence and strength of the "lucky outlet" belief in Singapore.
- Apply causal inference methods (difference-in-differences around new outlet openings) to estimate the volume-to-wins relationship more precisely.

---

# References

*The following references should be verified and accessed through SMU Library tools (Scopus AI, Scite, SciSpace) as required by the IS630 GenAI policy. Full bibliographic details should be confirmed at the time of writing the final deliverable.*

1. Ayton, P., & Fischer, I. (2004). The hot hand fallacy and the gambler's fallacy: Two faces of subjective randomness? *Memory & Cognition*, 32(8), 1369-1378.
2. Baker, R. D., & McHale, I. G. (2009). Modelling the probability distribution of prize winnings in the UK National Lottery. *Journal of the Royal Statistical Society: Series A*, 172(4), 813-834.
3. Baker, R. D., & McHale, I. G. (2011). Investigating the behavioural characteristics of lottery players by using a combination choice model for single and multiple line play. *Journal of the Royal Statistical Society: Series A*, 174(4), 1071-1090.
4. Boto-Garcia, D., Muniz-Fernandez, A., & Perez, L. (2025). The compatriot win effect and behavioural biases in lottery markets. *Oxford Bulletin of Economics and Statistics*, 88(2), 375-396.
5. Clotfelter, C. T., & Cook, P. J. (1993). The "gambler's fallacy" in lottery play. *Management Science*, 39(12), 1521-1525.
6. Genest, C., Lockhart, R. A., & Stephens, M. A. (2002). Chi-squared and other goodness-of-fit tests for the Poisson distribution. *Journal of Statistical Computation and Simulation*, 72(2), 107-139.
7. Gilovich, T., Vallone, R., & Tversky, A. (1985). The hot hand in basketball: On the misperception of random sequences. *Cognitive Psychology*, 17(3), 295-314.
8. Guryan, J., & Kearney, M. S. (2008). Gambling at lucky stores: Empirical evidence from state lottery sales. *American Economic Review*, 98(1), 458-473.
9. Joe, H. (1993). Tests of uniformity for sets of lotto numbers. *Statistics & Probability Letters*, 16(3), 181-188.
10. Lien, J. W., Yuan, J., & Zheng, J. (2015). Representativeness biases and lucky store effects. SSRN Working Paper No. 2635427.
11. National Council on Problem Gambling (NCPG). (2021). *Report of Survey on Participation in Gambling Activities among Singapore Residents, 2020*. Singapore: NCPG.
12. Rabin, M. (2002). Inference by believers in the law of small numbers. *Quarterly Journal of Economics*, 117(3), 775-816.
13. Rabin, M., & Vayanos, D. (2010). The gambler's and hot-hand fallacies: Theory and applications. *Review of Economic Studies*, 77(2), 730-778.
14. Subramaniam, M., et al. (2017). Prevalence and correlates of gambling in Singapore. *Annals of the Academy of Medicine, Singapore*, 46(3), 82-90.
15. Suetens, S., Galbo-Jorgensen, C. B., & Tyran, J.-R. (2016). Predicting lotto numbers: A natural experiment on the gambler's fallacy and the hot-hand fallacy. *Journal of the European Economic Association*, 14(3), 584-607.
16. Tversky, A., & Kahneman, D. (1971). Belief in the law of small numbers. *Psychological Bulletin*, 76(2), 105-110.
17. Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124-1131.

---

# GenAI Declaration

This project proposal was developed with assistance from Claude (Anthropic). Generative AI was used for:
- Brainstorming project structure and analytical approaches
- Identifying relevant academic papers and data sources
- Drafting initial code outlines for scraping and statistical analysis
- Structuring the data dictionary and database schema

All final analytical questions, statistical interpretations, and recommendations are the team's own work. All cited academic papers will be independently verified through SMU Library tools (Scopus AI, Scite, SciSpace) before inclusion in the final deliverable.
