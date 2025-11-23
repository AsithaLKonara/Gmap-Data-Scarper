from __future__ import annotations

import re
from typing import Iterable, Dict, Any, List

from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapeResult
from .site_search import site_search
from .social_common import HttpClient, rate_limit_delay, normalize_url


class XScraper(BaseScraper):
    name = "x"

    def __init__(self, per_request_delay_seconds: float = 2.0, max_fetch_bytes: int = 1024 * 1024) -> None:
        self.per_request_delay_seconds = per_request_delay_seconds
        self.client = HttpClient()
        self.max_fetch_bytes = max_fetch_bytes

    def _extract_profile(self, url: str, query: str) -> ScrapeResult:
        rate_limit_delay(self.per_request_delay_seconds)
        resp = self.client.get(url)
        text = resp.text[: self.max_fetch_bytes]
        soup = BeautifulSoup(text, "lxml")

        og_title = soup.find("meta", attrs={"property": "og:title"})
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        display_name = og_title.get("content").strip() if og_title and og_title.get("content") else "N/A"
        desc = og_desc.get("content").strip() if og_desc and og_desc.get("content") else ""

        handle = ""
        m = re.search(r"\(@([^\)]+)\)", display_name)
        if m:
            handle = m.group(1)

        result: ScrapeResult = {
            "Search Query": query,
            "Platform": self.name,
            "Profile URL": normalize_url(url),
            "Handle": handle,
            "Display Name": display_name,
            "Bio/About": desc,
            "Website": "",
            "Email": "",
            "Phone": "",
            "Followers": "",
            "Location": "",
        }
        return result

    def search(self, query: str, max_results: int) -> Iterable[ScrapeResult]:
        search_limit = max(max_results * 10, 500) if max_results > 0 else 1000
        candidates: List[str] = site_search(query=query, site="twitter.com", num=search_limit, engine="duckduckgo", debug=False)
        if not candidates:
            return
        
        # Filter out generic Twitter URLs
        generic_patterns = [
            "/home",
            "/explore",
            "/login",
            "/signup",
            "/en_us",
            "/en",
            "/i/",
            "/settings",
            "/compose",
            "/notifications",
            "/messages",
            "/search",
        ]
        
        for url in candidates:
            # Skip generic pages
            if any(pattern in url.lower() for pattern in generic_patterns):
                continue
            # Only accept URLs with username pattern: twitter.com/username
            if not re.search(r'twitter\.com/[^/]+$', url, re.I) and not re.search(r'x\.com/[^/]+$', url, re.I):
                continue
            
            try:
                result = self._extract_profile(url, query)
                if result.get("Profile URL") and result.get("Profile URL") != "N/A":
                    yield result
            except Exception:
                continue


