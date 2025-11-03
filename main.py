from __future__ import annotations

import argparse
import csv
import os
import time
from typing import Dict, Iterable, List, Set, Tuple

import yaml

from scrapers.base import BaseScraper, COMMON_FIELDS
from scrapers.google_maps import GoogleMapsScraper
from scrapers.facebook import FacebookScraper
from scrapers.instagram import InstagramScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.x_twitter import XScraper
from scrapers.youtube import YouTubeScraper
from scrapers.tiktok import TikTokScraper
from utils.csv_writer import write_row_incremental


def read_config(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def read_queries(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [q.strip() for q in f.readlines() if q.strip()]


def load_processed_keys(csv_path: str) -> Set[Tuple[str, str, str]]:
    if not os.path.exists(os.path.expanduser(csv_path)):
        return set()
    processed: Set[Tuple[str, str, str]] = set()
    try:
        with open(os.path.expanduser(csv_path), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed.add((row.get("Search Query", ""), row.get("Platform", ""), row.get("Profile URL", "")))
    except Exception:
        pass
    return processed


def get_scraper_instances(enabled: List[str], headless: bool) -> List[BaseScraper]:
    instances: List[BaseScraper] = []
    mapping: Dict[str, BaseScraper] = {
        "google_maps": GoogleMapsScraper(headless=headless),
        "facebook": FacebookScraper(),
        "instagram": InstagramScraper(),
        "linkedin": LinkedInScraper(),
        "x": XScraper(),
        "youtube": YouTubeScraper(),
        "tiktok": TikTokScraper(),
    }
    for key in enabled:
        scraper = mapping.get(key)
        if scraper is not None:
            instances.append(scraper)
    return instances


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Platform Lead Scraper (public-only)")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML config")
    parser.add_argument("--queries", default="search_queries.txt", help="Path to queries file")
    parser.add_argument("--skip-gmaps", action="store_true", help="Skip Google Maps scraping")
    parser.add_argument("--platforms", default="", help="Comma-separated subset of platforms to run")
    parser.add_argument("--max-results", type=int, default=0, help="Override max results per query")
    args = parser.parse_args()

    cfg = read_config(args.config)
    enabled_cfg: List[str] = cfg.get("enabled_platforms", ["facebook", "instagram", "linkedin", "x", "youtube", "tiktok"])  # default
    if not args.skip_gmaps:
        enabled_cfg = ["google_maps"] + enabled_cfg
    if args.platforms:
        enabled_cfg = [p.strip() for p in args.platforms.split(",") if p.strip()]

    headless = bool(cfg.get("headless", True))
    per_platform_delay = float(cfg.get("per_platform_delay_seconds", 8))
    max_results = int(cfg.get("max_results_per_query", 5))
    if args.max_results > 0:
        max_results = args.max_results

    output_dir = os.path.expanduser(cfg.get("output_dir", "~/Documents/social_leads"))
    os.makedirs(output_dir, exist_ok=True)
    consolidated_csv = os.path.join(output_dir, "all_platforms.csv")

    processed = load_processed_keys(consolidated_csv) if bool(cfg.get("resume", True)) else set()

    scrapers: List[BaseScraper] = get_scraper_instances(enabled_cfg, headless=headless)
    queries = read_queries(args.queries)

    print(f"[START] Queries: {len(queries)} | Platforms: {', '.join([s.platform_name() for s in scrapers])}")

    for qi, query in enumerate(queries, 1):
        print(f"\n[QUERY {qi}/{len(queries)}] {query}")
        for si, scraper in enumerate(scrapers, 1):
            plat = scraper.platform_name()
            plat_csv = os.path.join(output_dir, f"{plat}.csv")
            print(f"  [SCRAPER {si}/{len(scrapers)}] {plat}")
            wrote_any = False
            try:
                for result in scraper.search(query=query, max_results=max_results):
                    key = (result.get("Search Query", ""), result.get("Platform", plat), result.get("Profile URL", ""))
                    if key in processed:
                        continue
                    # Write per-platform and consolidated
                    write_row_incremental(plat_csv, COMMON_FIELDS, result)
                    write_row_incremental(consolidated_csv, COMMON_FIELDS, result)
                    processed.add(key)
                    wrote_any = True
            except Exception as e:
                print(f"    [WARN] {plat} error: {e}")
            if wrote_any:
                print(f"    [OK] Wrote results for {plat}")
            time.sleep(per_platform_delay)

    print(f"\n[DONE] Consolidated CSV: {consolidated_csv}")


if __name__ == "__main__":
    main()


