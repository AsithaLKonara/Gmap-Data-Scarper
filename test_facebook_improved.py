from scrapers.facebook import FacebookScraper

fb = FacebookScraper()
results = list(fb.search('hotels in kandy', 10))

print(f'Found {len(results)} results')
for i, r in enumerate(results[:10], 1):
    print(f"  {i}. {r.get('Display Name', 'N/A')[:50]}")
    print(f"     URL: {r.get('Profile URL', 'N/A')[:70]}")
    print(f"     Handle: {r.get('Handle', 'N/A')}")

