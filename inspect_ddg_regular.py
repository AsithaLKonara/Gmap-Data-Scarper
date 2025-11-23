from scrapers.social_common import HttpClient
from bs4 import BeautifulSoup
import urllib.parse

query = "hotels in kandy"
site = "instagram.com"
search_url = f"https://duckduckgo.com/?q={urllib.parse.quote_plus(f'site:{site} {query}')}&ia=web"

client = HttpClient()
resp = client.get(search_url)

print(f"Status: {resp.status_code}")
print(f"URL: {resp.url}")
print(f"Content length: {len(resp.text)}")
print("\n" + "="*60)
print("Searching for Instagram links...")
print("="*60)

soup = BeautifulSoup(resp.text, "lxml")

# Look for any links containing instagram
all_links = soup.find_all("a", href=True)
instagram_links = []
for link in all_links:
    href = link.get("href", "")
    if "instagram.com" in href.lower():
        instagram_links.append(href)
        print(f"Found: {href[:100]}")

print(f"\nTotal Instagram links found: {len(instagram_links)}")

# Also check for result containers
print("\nChecking for result containers...")
result_divs = soup.find_all("div", class_=lambda x: x and "result" in x.lower())
print(f"Result divs: {len(result_divs)}")

# Check for common result selectors
selectors = [
    "article",
    "[data-testid]",
    ".web-result",
    ".result",
    "a[data-uddg]",
]

for sel in selectors:
    elements = soup.select(sel)
    print(f"Selector '{sel}': {len(elements)} elements")

