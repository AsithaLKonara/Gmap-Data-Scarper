from scrapers.instagram import InstagramScraper
import csv

ig = InstagramScraper()
results = list(ig.search('hotels in kandy', 2))

print(f"Direct test: {len(results)} results")
for r in results:
    print(f"  {r.get('Display Name', 'N/A')[:50]}: {r.get('Profile URL', 'N/A')}")

# Check CSV
import os
csv_path = os.path.expanduser("~/Documents/social_leads/instagram.csv")
if os.path.exists(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"\nCSV file has {len(rows)} rows")
        for r in rows:
            print(f"  CSV: {r.get('Display Name', 'N/A')[:50]}")
else:
    print(f"\nCSV file not found: {csv_path}")

