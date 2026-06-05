#!/usr/bin/env python3

import sys
import time

from toto_scraper import step1_scrape_aggregate, step2_scrape_details, step3_parse_gra
from build_dataset import step4_download_supplementary, step5_merge, step6_geocode, step7_build_final, OUT_DIR


def main() -> None:
    print("=" * 70)
    print("  TOTO Lucky Outlet — Unified Data Collection Pipeline")
    print("  IS630 Group Project")
    print("=" * 70)
    start_time = time.time()

    print(f"\n{'='*70}")
    print("STEP 1/7: Scrape TOTO Winning Outlets Aggregate Page")
    print(f"{'='*70}")
    outlet_list = step1_scrape_aggregate()
    if not outlet_list:
        print("[FATAL] No outlets scraped. Aborting.")
        sys.exit(1)
    print(f"  Result: {len(outlet_list)} outlets")

    print(f"\n{'='*70}")
    print("STEP 2/7: Scrape Per-Outlet Winning History & Addresses")
    print(f"{'='*70}")
    all_wins, scraped_outlets = step2_scrape_details(outlet_list)
    print(f"  Result: {len(scraped_outlets)} outlets with addresses, {len(all_wins)} win records")

    print(f"\n{'='*70}")
    print("STEP 3/7: Parse GRA PDF (Official Outlet Directory)")
    print(f"{'='*70}")
    gra_outlets = step3_parse_gra()
    print(f"  Result: {len(gra_outlets)} GRA outlets")

    print(f"\n{'='*70}")
    print("STEP 4/7: Download Supplementary Datasets (data.gov.sg)")
    print(f"{'='*70}")
    step4_download_supplementary()

    print(f"\n{'='*70}")
    print("STEP 5/7: Merge Data Sources into outlets_raw.csv")
    print(f"{'='*70}")
    step5_merge()

    print(f"\n{'='*70}")
    print("STEP 6/7: Geocode Outlets via OneMap API")
    print(f"{'='*70}")
    geocoded_outlets = step6_geocode()
    if not geocoded_outlets:
        print("[FATAL] Geocoding failed. Aborting.")
        sys.exit(1)
    ok_count = sum(1 for o in geocoded_outlets if o.get("geocode_status") == "OK")
    print(f"  Result: {ok_count} geocoded outlets")

    print(f"\n{'='*70}")
    print("STEP 7/7: Compute Proxy Volumes & Build Final Dataset")
    print(f"{'='*70}")
    step7_build_final(geocoded_outlets)

    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"  PIPELINE COMPLETE in {elapsed:.0f}s")
    print(f"  Final dataset: {OUT_DIR / 'outlets_final.csv'}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
