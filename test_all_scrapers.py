"""Test all scrapers individually with verbose output."""
from scrapers.facebook import FacebookScraper
from scrapers.instagram import InstagramScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.x_twitter import XScraper
from scrapers.youtube import YouTubeScraper
from scrapers.tiktok import TikTokScraper

query = "hotels in kandy"
scrapers = [
    ("Facebook", FacebookScraper()),
    ("Instagram", InstagramScraper()),
    ("LinkedIn", LinkedInScraper()),
    ("X/Twitter", XScraper()),
    ("YouTube", YouTubeScraper()),
    ("TikTok", TikTokScraper()),
]

print(f"Testing with query: '{query}'\n")
print("=" * 60)

total_results = 0
for name, scraper in scrapers:
    print(f"\n{name}:")
    try:
        results = list(scraper.search(query, max_results=2))
        print(f"  Found {len(results)} results")
        total_results += len(results)
        for i, r in enumerate(results, 1):
            print(f"    {i}. {r.get('Display Name', 'N/A')[:50]}")
            print(f"       URL: {r.get('Profile URL', 'N/A')[:70]}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print(f"Total results across all platforms: {total_results}")

