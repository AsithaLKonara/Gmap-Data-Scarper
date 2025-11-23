from scrapers.facebook import FacebookScraper
from scrapers.instagram import InstagramScraper

print("Testing Facebook scraper...")
fb = FacebookScraper()
results = list(fb.search('hotels in kandy', 2))
print(f'Facebook: Found {len(results)} results')
for r in results:
    print(f"  - {r.get('Display Name')}: {r.get('Profile URL')}")

print("\nTesting Instagram scraper...")
ig = InstagramScraper()
results = list(ig.search('hotels in kandy', 2))
print(f'Instagram: Found {len(results)} results')
for r in results:
    print(f"  - {r.get('Display Name')}: {r.get('Profile URL')}")

