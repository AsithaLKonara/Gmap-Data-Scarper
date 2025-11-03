from __future__ import annotations

import html
import urllib.parse
from typing import List

from bs4 import BeautifulSoup

from .social_common import HttpClient, rate_limit_delay, normalize_url


def _duckduckgo_query_url(site: str, query: str) -> str:
    q = f"site:{site} {query}"
    return f"https://duckduckgo.com/html/?q={urllib.parse.quote_plus(q)}"


def site_search(query: str, site: str, num: int = 5, engine: str = "duckduckgo", per_request_delay_seconds: float = 2.0) -> List[str]:
    """Return top public result URLs for `site:<site> query` using DuckDuckGo HTML endpoint by default."""
    client = HttpClient()
    urls: List[str] = []

    if engine != "duckduckgo":
        # Default to DuckDuckGo to avoid brittle scraping of Google SERP.
        engine = "duckduckgo"

    search_url = _duckduckgo_query_url(site, query)
    rate_limit_delay(per_request_delay_seconds)
    resp = client.get(search_url)
    soup = BeautifulSoup(resp.text, "lxml")

    # DuckDuckGo HTML results
    for a in soup.select("a.result__a"):
        href = a.get("href")
        if not href:
            continue
        normalized = normalize_url(html.unescape(href))
        urls.append(normalized)
        if len(urls) >= num:
            break

    # Fallback selector
    if not urls:
        for a in soup.select("div.result a[href]"):
            href = a.get("href")
            if not href:
                continue
            normalized = normalize_url(html.unescape(href))
            urls.append(normalized)
            if len(urls) >= num:
                break

    return urls


