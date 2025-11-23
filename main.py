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
from orchestrator_core import run_orchestrator


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
    AVAILABLE_PLATFORMS = ["google_maps", "facebook", "instagram", "linkedin", "x", "youtube", "tiktok"]
    
    parser = argparse.ArgumentParser(
        description="Multi-Platform Lead Scraper (public-only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available platforms: {', '.join(AVAILABLE_PLATFORMS)}

Examples:
  # Run all platforms (from config.yaml)
  python main.py
  
  # Run only Google Maps and Facebook
  python main.py --platforms google_maps,facebook
  
  # Run only social platforms (skip Google Maps)
  python main.py --skip-gmaps --platforms instagram,facebook
  
  # Run with visible browser
  python main.py --no-headless
  
  # Run specific platforms with visible browser
  python main.py --platforms google_maps,instagram --no-headless
        """
    )
    parser.add_argument("--config", default="config.yaml", help="Path to YAML config file")
    parser.add_argument("--queries", default="search_queries.txt", help="Path to queries file")
    parser.add_argument("--skip-gmaps", action="store_true", help="Skip Google Maps scraping")
    parser.add_argument(
        "--platforms", 
        default="", 
        help=f"Comma-separated list of platforms to run. Available: {', '.join(AVAILABLE_PLATFORMS)}"
    )
    parser.add_argument("--max-results", type=int, default=0, help="Override max results per query (0 = use config)")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window (overrides config)")
    
    # v2.0+ Filter flags
    parser.add_argument("--location", type=str, default="", help="Filter by location (city, region, or country)")
    parser.add_argument("--radius", type=float, default=None, help="Radius in km for location filtering")
    parser.add_argument("--category", type=str, default="", help="Comma-separated list of categories to generate queries for")
    parser.add_argument("--business-type", type=str, default="", help="Comma-separated list of business types to filter")
    parser.add_argument("--job-level", type=str, default="", help="Comma-separated list of job levels (Junior, Mid, Senior, Executive, Freelancer)")
    parser.add_argument("--education-level", type=str, default="", help="Comma-separated list of education levels (High School, Undergraduate, Postgraduate, Doctorate)")
    parser.add_argument("--date-range", type=str, default="", help="Date range filter (YYYY-MM-DD:YYYY-MM-DD)")
    parser.add_argument("--active-within", type=int, default=None, help="Filter by activity within N days")
    parser.add_argument("--boosted-only", action="store_true", help="Only include leads with boosted/sponsored posts")
    
    args = parser.parse_args()

    cfg = read_config(args.config)
    enabled_cfg: List[str] = cfg.get("enabled_platforms", ["facebook", "instagram", "linkedin", "x", "youtube", "tiktok"])  # default
    
    # Handle platform selection
    if args.platforms:
        selected_platforms = [p.strip().lower() for p in args.platforms.split(",") if p.strip()]
        # Validate platforms
        invalid_platforms = [p for p in selected_platforms if p not in AVAILABLE_PLATFORMS]
        if invalid_platforms:
            print(f"[ERROR] Invalid platforms: {', '.join(invalid_platforms)}")
            print(f"[INFO] Available platforms: {', '.join(AVAILABLE_PLATFORMS)}")
            return
        enabled_cfg = selected_platforms
        print(f"[INFO] Selected platforms: {', '.join(enabled_cfg)}")
    elif not args.skip_gmaps:
        # If no --platforms specified and not skipping GMaps, add it
        enabled_cfg = ["google_maps"] + enabled_cfg
    else:
        # If skipping GMaps and no platforms specified, use config defaults (already set)
        pass

    # Handle headless mode (CLI flag overrides config)
    headless = bool(cfg.get("headless", True))
    if args.no_headless:
        headless = False
        print(f"[INFO] Browser window will be visible (--no-headless flag)")
    per_platform_delay = float(cfg.get("per_platform_delay_seconds", 8))
    max_results = int(cfg.get("max_results_per_query", 0))  # 0 = unlimited
    if args.max_results > 0:
        max_results = args.max_results
    elif max_results == 0:
        max_results = 999999  # Unlimited mode - process all results
        print(f"[INFO] Unlimited mode enabled - will process all available results")

    output_dir = os.path.expanduser(cfg.get("output_dir", "~/Documents/social_leads"))
    os.makedirs(output_dir, exist_ok=True)
    consolidated_csv = os.path.join(output_dir, "all_platforms.csv")

    processed = load_processed_keys(consolidated_csv) if bool(cfg.get("resume", True)) else set()

    scrapers: List[BaseScraper] = get_scraper_instances(enabled_cfg, headless=headless)
    
    # Handle category-based query generation (v2.0+)
    queries = []
    if args.category:
        try:
            from query_generator import CategoryQueryGenerator
            categories = [c.strip() for c in args.category.split(",") if c.strip()]
            query_gen = CategoryQueryGenerator()
            generated_queries = query_gen.generate_queries(categories)
            queries.extend(generated_queries)
            print(f"[v2.0] Generated {len(generated_queries)} queries from categories: {', '.join(categories)}")
        except ImportError:
            print("[WARN] Query generator not available, using queries file")
            queries = read_queries(args.queries)
        except Exception as e:
            print(f"[WARN] Query generation failed: {e}, using queries file")
            queries = read_queries(args.queries)
    else:
        queries = read_queries(args.queries)
    
    # Apply CLI filter overrides to config
    if (args.location or args.business_type or args.job_level or 
        args.education_level or args.date_range or args.active_within is not None or args.boosted_only):
        if "filters" not in cfg:
            cfg["filters"] = {}
        if args.location:
            cfg["filters"]["location"] = args.location
        if args.radius:
            cfg["filters"]["radius_km"] = args.radius
        if args.business_type:
            cfg["filters"]["business_type"] = [bt.strip() for bt in args.business_type.split(",") if bt.strip()]
        if args.job_level:
            cfg["filters"]["job_level"] = [jl.strip() for jl in args.job_level.split(",") if jl.strip()]
        if args.education_level:
            cfg["filters"]["education_level"] = [el.strip() for el in args.education_level.split(",") if el.strip()]
        if args.date_range:
            cfg["filters"]["date_range"] = args.date_range
        if args.active_within is not None:
            cfg["filters"]["active_within_days"] = args.active_within
        if args.boosted_only:
            cfg["filters"]["boosted_only"] = True

    print(f"\n{'='*80}")
    print(f"[START] Configuration")
    print(f"{'='*80}")
    print(f"Queries: {len(queries)}")
    print(f"Platforms: {', '.join([s.platform_name().upper() for s in scrapers])}")
    print(f"Headless mode: {headless} (browser {'hidden' if headless else 'visible'})")
    print(f"Max results per query: {max_results}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*80}\n")

    # Use orchestrator_core for v2.0+ features (classification, filtering, etc.)
    def on_log(msg: str) -> None:
        print(msg)
    
    def on_result(result: Dict) -> None:
        # Additional result handling if needed
        pass
    
    # Write config to temp file if we modified it
    import tempfile
    temp_config = None
    if args.location or args.business_type or args.job_level:
        import yaml
        temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.safe_dump(cfg, temp_config)
        temp_config.close()
        config_path = temp_config.name
    else:
        config_path = args.config
    
    try:
        # Determine which queries to use
        if args.category and queries:
            # Use generated queries from categories
            run_orchestrator(
                config_path=config_path,
                queries_path=None,
                queries_list=queries,
                enabled_platforms=enabled_cfg if args.platforms else None,
                skip_gmaps=args.skip_gmaps,
                max_results_override=args.max_results if args.max_results > 0 else None,
                on_log=on_log,
                on_result=on_result,
            )
        else:
            # Use queries from file
            run_orchestrator(
                config_path=config_path,
                queries_path=args.queries,
                queries_list=None,
                enabled_platforms=enabled_cfg if args.platforms else None,
                skip_gmaps=args.skip_gmaps,
                max_results_override=args.max_results if args.max_results > 0 else None,
                on_log=on_log,
                on_result=on_result,
            )
    finally:
        # Clean up temp config if created
        if temp_config and os.path.exists(temp_config.name):
            os.unlink(temp_config.name)
    
    print(f"\n{'='*80}")
    print(f"[DONE] All queries processed")
    print(f"[SAVE] Consolidated CSV: {consolidated_csv}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()


