#!/usr/bin/env python3
"""Quick test of improved scrapers with debug output."""
import sys
from scrapers.site_search import site_search

print("Testing site_search improvements...")
print("=" * 60)

test_query = "hotels in kandy"
sites = [
    ("facebook.com", "Facebook"),
    ("instagram.com", "Instagram"),
]

for site, name in sites:
    print(f"\n{name} ({site}):")
    try:
        urls = site_search(query=test_query, site=site, num=3, engine="duckduckgo", debug=True)
        print(f"  RESULT: Found {len(urls)} URLs")
        for i, url in enumerate(urls, 1):
            print(f"    {i}. {url}")
        if not urls:
            print("  WARNING: No URLs found!")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete.")

