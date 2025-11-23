import csv
import os

csv_path = os.path.expanduser(r"~/Documents/social_leads/all_platforms.csv")

if os.path.exists(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"Total rows in CSV: {len(rows)}")
        print("\nFirst 10 results:")
        for i, r in enumerate(rows[:10], 1):
            print(f"{i}. [{r.get('Platform', 'N/A')}] {r.get('Display Name', 'N/A')[:60]}")
            print(f"   URL: {r.get('Profile URL', 'N/A')[:80]}")
        if len(rows) == 0:
            print("WARNING: CSV is empty - no results found!")
else:
    print(f"CSV file not found at: {csv_path}")

