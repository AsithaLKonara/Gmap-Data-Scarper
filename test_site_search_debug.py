from scrapers.site_search import site_search

query = "hotels in kandy"
sites = [
    ("facebook.com", "Facebook"),
    ("instagram.com", "Instagram"),
    ("linkedin.com/company", "LinkedIn"),
    ("twitter.com", "X/Twitter"),
    ("youtube.com", "YouTube"),
    ("tiktok.com", "TikTok"),
]

print("Testing site_search with DEBUG enabled\n")
print("=" * 60)

for site, name in sites:
    print(f"\n{name} ({site}):")
    try:
        urls = site_search(query=query, site=site, num=3, engine="duckduckgo", debug=True)
        print(f"  FINAL RESULT: {len(urls)} URLs returned")
        if urls:
            for i, url in enumerate(urls, 1):
                print(f"    {i}. {url}")
        else:
            print("  WARNING: No URLs found!")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()

