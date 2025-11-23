from scrapers.facebook import FacebookScraper
from scrapers.site_search import site_search

print("Step 1: Testing site_search...")
candidates = site_search(query="hotels in kandy", site="facebook.com", num=10, engine="duckduckgo", debug=True)
print(f"\nFound {len(candidates)} candidate URLs")
for i, url in enumerate(candidates[:5], 1):
    print(f"  {i}. {url}")

if candidates:
    print("\nStep 2: Testing Facebook scraper...")
    fb = FacebookScraper()
    results = list(fb.search('hotels in kandy', 10))
    print(f"\nExtracted {len(results)} results")
    for i, r in enumerate(results[:5], 1):
        print(f"  {i}. {r.get('Display Name', 'N/A')[:50]}")
        print(f"     URL: {r.get('Profile URL', 'N/A')[:70]}")
else:
    print("\nNo candidates found, skipping scraper test")

