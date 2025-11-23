#!/usr/bin/env python3
"""Deep test to find 10 leads from each platform with one query."""
import sys
import os
from scrapers.facebook import FacebookScraper
from scrapers.instagram import InstagramScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.x_twitter import XScraper
from scrapers.youtube import YouTubeScraper
from scrapers.tiktok import TikTokScraper
from scrapers.site_search import site_search

# Test query
query = "hotels in kandy"

scrapers = [
    ("Facebook", FacebookScraper()),
    ("Instagram", InstagramScraper()),
    ("LinkedIn", LinkedInScraper()),
    ("X/Twitter", XScraper()),
    ("YouTube", YouTubeScraper()),
    ("TikTok", TikTokScraper()),
]

print("=" * 80)
print(f"DEEP TEST: Finding 10 leads per platform with query: '{query}'")
print("=" * 80)

total_found = 0
total_attempted = 0

for platform_name, scraper in scrapers:
    print(f"\n{'='*80}")
    print(f"PLATFORM: {platform_name}")
    print(f"{'='*80}")
    
    # First, test site_search to see if we can find URLs
    site_map = {
        "Facebook": "facebook.com",
        "Instagram": "instagram.com",
        "LinkedIn": "linkedin.com/company",
        "X/Twitter": "twitter.com",
        "YouTube": "youtube.com",
        "TikTok": "tiktok.com",
    }
    
    site = site_map.get(platform_name, "")
    print(f"\n[STEP 1] Testing site_search for {site}...")
    try:
        urls = site_search(query=query, site=site, num=10, engine="duckduckgo", debug=True)
        print(f"  Found {len(urls)} candidate URLs from search")
        if urls:
            print("  Sample URLs:")
            for i, url in enumerate(urls[:5], 1):
                print(f"    {i}. {url[:80]}")
    except Exception as e:
        print(f"  ERROR in site_search: {e}")
        import traceback
        traceback.print_exc()
        continue
    
    # Now test the scraper
    print(f"\n[STEP 2] Testing {platform_name} scraper extraction...")
    try:
        results = list(scraper.search(query, max_results=10))
        print(f"  Successfully extracted {len(results)} results")
        total_attempted += 10
        total_found += len(results)
        
        if results:
            print(f"\n  Results ({len(results)}):")
            for i, r in enumerate(results, 1):
                name = r.get('Display Name', 'N/A')[:60]
                url = r.get('Profile URL', 'N/A')[:70]
                print(f"    {i}. {name}")
                print(f"       URL: {url}")
        else:
            print(f"  WARNING: No results extracted despite {len(urls)} candidate URLs found")
            if urls:
                print(f"  This suggests extraction is failing - likely due to login requirements")
    except Exception as e:
        print(f"  ERROR in scraper: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total platforms tested: {len(scrapers)}")
print(f"Total candidate URLs found: {total_attempted}")
print(f"Total results successfully extracted: {total_found}")
print(f"Success rate: {(total_found/total_attempted*100) if total_attempted > 0 else 0:.1f}%")
print("\nNOTE: Low success rate indicates platforms require authentication for full profile access.")

