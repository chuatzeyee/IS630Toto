# Shared-Postal Outlet Pairing Tables

Generated from `outlets_modeling.csv` (column `merge_role`) cross-referenced with the win-history draw timeline.

**How roles are assigned** (purely from when each outlet actually won TOTO prizes):

- **replacement** — winning periods do **not** overlap. Earlier outlet stopped; a successor took the same spot (renamed / re-tenanted). Safe to merge into one continuous location.
- **concurrent** — winning periods **overlap**. Two genuinely different shops in the same building at the same time. **Must NOT be merged** — doing so would fabricate the luck signal.
- **name_duplicate** — identical first/last draw range → same physical outlet under two names. De-duplicate (count once).
- *(alias records with zero wins are dropped during modeling and don't appear here.)*

## Summary

- Shared-postal groups: **22** — 14 replacement, 6 concurrent, 1 name-duplicate, 1 mixed
- Outlet rows by role: **29** replacement, **14** concurrent, **2** name_duplicate

## 1. Replacements (sequential — MERGE)

Earlier outlet's wins end before the successor's begin. Same betting location over time.

### Postal 098585 — Bukit Merah

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Giant VivoCity | replacement | 27/03/2017 | 07/06/2018 | 3252–3377 | 4 |
| NTUC FairPrice VivoCity | replacement | 21/11/2019 | 23/03/2026 | 3529–4167 | 13 |

### Postal 380119 — Geylang

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Li Thoe Trading | replacement | 17/07/1997 | 03/04/2025 | 1198–4066 | 94 |
| Dawn Florist - Aljunied Avenue 2 | replacement | 14/07/2025 | 27/04/2026 | 4095–4177 | 8 |

### Postal 449269 — Marine Parade

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Giant Parkway Parade | replacement | 28/01/2008 | 03/01/2020 | 2296–3541 | 47 |
| NTUC FairPrice Parkway Parade | replacement | 19/07/2021 | 30/03/2026 | 3679–4169 | 28 |

### Postal 460017 — Bedok

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Yeo Kean Fatt Dept Store | replacement | 17/09/2001 | 12/11/2018 | 1632–3422 | 31 |
| Cheng Chew Wah Agency - Bedok South Road | replacement | 25/03/2019 | 27/02/2026 | 3460–4160 | 26 |

### Postal 520824 — Paya Lebar

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Tampines Rovers Football Club | replacement | 15/07/2002 | 11/02/2016 | 1718–3135 | 32 |
| Tampines Trading - 824 | replacement | 27/07/2017 | 12/03/2026 | 3287–4164 | 22 |

### Postal 529509 — Tampines

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| NTUC FP Century Square | replacement | 18/10/2012 | 26/06/2017 | 2789–3278 | 14 |
| Prime Century Square | replacement | 11/06/2018 | 04/08/2023 | 3378–3892 | 15 |

### Postal 543277 — Sengkang

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Ichido Kopitiam City | replacement | 04/09/2017 | 16/12/2019 | 3298–3536 | 9 |
| NTUC FairPrice Compassvale Link | replacement | 21/01/2022 | 02/12/2024 | 3732–4031 | 12 |

### Postal 560555 — Serangoon

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Premier Security Co-operative Ltd | replacement | 30/01/2003 | 28/10/2024 | 1775–4021 | 30 |
| Clifford Gift Shop - Ang Mo Kio Avenue 10 | replacement | 09/02/2026 | 09/02/2026 | 4155–4155 | 1 |

### Postal 569922 — Ang Mo Kio

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| 7-Eleven Big Mac Centre | replacement | 07/08/2006 | 31/10/2016 | 2142–3210 | 26 |
| Ng Nam Thye Trading - Ang Mo Kio Avenue 3 | replacement | 02/03/2017 | 30/03/2026 | 3245–4169 | 32 |

### Postal 610399 — Jurong West

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| The Little Plaza | replacement | 06/07/2000 | 15/12/2014 | 1507–3014 | 38 |
| Ng Nam Thye Trading - Taman Jurong | replacement | 23/11/2015 | 18/08/2025 | 3112–4105 | 33 |

### Postal 671524 — Choa Chu Kang

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Giant Greenridge Shopping Centre | replacement | 10/08/2006 | 28/03/2024 | 2143–3960 | 28 |
| NTUC FairPrice Greenridge Shopping Centre | replacement | 08/08/2025 | 08/08/2025 | 4102–4102 | 1 |

### Postal 769098 — Yishun

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Cold Storage Northpoint | replacement | 11/08/2011 | 10/03/2022 | 2665–3746 | 52 |
| Singapore Pools Northpoint City Branch | replacement | 22/01/2024 | 04/05/2026 | 3941–4179 | 17 |

### Postal 797653 — Sengkang

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| NTUC Foodfare - Seletar Mall | replacement | 20/07/2017 | 04/09/2017 | 3285–3298 | 2 |
| NTUC FairPrice Seletar Mall | replacement | 21/11/2019 | 23/10/2025 | 3529–4124 | 21 |

### Postal 823308 — Punggol

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| NTUC FP Punggol Walk | replacement | 04/02/2016 | 16/07/2018 | 3133–3388 | 7 |
| Hao Mart Punggol Walk | replacement | 18/10/2021 | 17/04/2023 | 3705–3861 | 4 |

## 2. Concurrent (overlapping — DO NOT MERGE)

Both outlets won during overlapping periods → distinct shops co-located in one building.

### Postal 048441 — Downtown Core

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| China Square Betting Centre - Lottery Lobby (Public) | concurrent | 18/02/2011 | 25/03/2024 | 2615–3959 | 7 |
| China Square Betting Centre - Level 2 | concurrent | 14/07/2022 | 14/07/2022 | 3782–3782 | 1 |

### Postal 150084 — River Valley

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Teo Khar Bee Agency | concurrent | 30/03/1998 | 13/02/2023 | 1270–3843 | 56 |
| Goh Geok Kwee Agency - Redhill Lane | concurrent | 04/02/2002 | 02/01/2026 | 1672–4144 | 29 |

### Postal 310070 — Toa Payoh

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Yeo Soon Huat | concurrent | 26/06/2003 | 24/01/2022 | 1817–3733 | 38 |
| Balestier Khalsa Football Club | concurrent | 09/06/2008 | 04/05/2026 | 2334–4179 | 21 |

### Postal 500004 — Changi

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Kis Store | concurrent | 01/03/1999 | 13/02/2026 | 1366–4156 | 88 |
| Cheers Changi Village Road | concurrent | 04/03/2004 | 03/04/2025 | 1889–4066 | 96 |

### Postal 689812 — Choa Chu Kang

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| NTUC FairPrice Lot 1 Shoppers' Mall | concurrent | 26/02/2007 | 28/04/2025 | 2200–4073 | 63 |
| Singapore Pools LOT One Branch | concurrent | 15/11/2021 | 02/01/2026 | 3713–4144 | 27 |

### Postal 738078 — Sungei Kadut

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| STC Racecourse - Kranji 1 | concurrent | 23/04/2001 | 22/07/2019 | 1590–3494 | 7 |
| Singapore Racecourse - MRT Plaza (Public) | concurrent | 09/04/2018 | 23/02/2024 | 3360–3950 | 2 |

## 3. Name duplicates (same outlet, two names — DE-DUPLICATE)

Identical draw ranges → a single physical outlet logged under two labels.

### Postal 150169 — Bukit Merah

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| Bukit Merah Betting Centre | name_duplicate | 08/10/2007 | 31/07/2025 | 2264–4100 | 9 |
| Bukit Merah Betting Centre - Lottery Lobby (Public) | name_duplicate | 08/10/2007 | 31/07/2025 | 2264–4100 | 8 |

## 4. Mixed groups (per-outlet review)

Group contains a mix of roles. A replacement chain plus a concurrent outlet share the building; treat each row by its own `merge_role`.

### Postal 600352 — Tengah

| Outlet | Role | First win | Last win | Draws | Wins |
|---|---|---|---|---|---|
| S E Store | replacement | 25/02/1999 | 19/10/2020 | 1365–3601 | 44 |
| Jurong East Betting Centre - Lottery Lobby (Public) | concurrent | 26/02/2021 | 22/04/2021 | 3638–3654 | 2 |
| Tan Ah Leck Trading - Jurong East Street 31 | concurrent | 26/02/2021 | 18/08/2025 | 3638–4105 | 10 |

