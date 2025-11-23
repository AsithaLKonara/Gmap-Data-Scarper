import csv
import os

csv_path = os.path.expanduser(r"~/Documents/social_leads/all_platforms.csv")

if os.path.exists(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        print(f"Total rows in consolidated CSV: {len(rows)}")
        print("\nResults by platform:")
        
        by_platform = {}
        for r in rows:
            platform = r.get('Platform', 'Unknown')
            by_platform[platform] = by_platform.get(platform, 0) + 1
        
        for platform, count in sorted(by_platform.items()):
            print(f"  {platform}: {count} leads")
        
        print("\nSample results:")
        for i, r in enumerate(rows[:20], 1):
            platform = r.get('Platform', 'N/A')
            name = r.get('Display Name', 'N/A')[:50]
            url = r.get('Profile URL', 'N/A')[:70]
            print(f"{i}. [{platform}] {name}")
            print(f"   {url}")
        
        if len(rows) == 0:
            print("\nWARNING: CSV is empty!")
else:
    print(f"CSV file not found: {csv_path}")

# Also check individual platform CSVs
print("\n" + "="*60)
print("Checking individual platform CSVs:")
print("="*60)
output_dir = os.path.expanduser("~/Documents/social_leads")
platforms = ['facebook', 'instagram', 'linkedin', 'x', 'youtube', 'tiktok']

for platform in platforms:
    csv_file = os.path.join(output_dir, f"{platform}.csv")
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print(f"  {platform}.csv: {len(rows)} rows")
    else:
        print(f"  {platform}.csv: not found")

