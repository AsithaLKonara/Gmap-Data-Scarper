from scrapers.social_common import HttpClient
from bs4 import BeautifulSoup
import urllib.parse

query = "hotels in kandy"
site = "facebook.com"
search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(f'site:{site} {query}')}"

client = HttpClient()
resp = client.get(search_url)

print(f"Status: {resp.status_code}")
print(f"URL: {resp.url}")
print(f"Content length: {len(resp.text)}")
print("\n" + "="*60)
print("First 2000 chars of HTML:")
print("="*60)
print(resp.text[:2000])

print("\n" + "="*60)
print("Looking for links with 'facebook.com':")
print("="*60)

soup = BeautifulSoup(resp.text, "lxml")
all_links = soup.find_all("a", href=True)
for link in all_links[:20]:
    href = link.get("href", "")
    if "facebook.com" in href or "uddg" in href:
        print(f"  {href[:100]}")

