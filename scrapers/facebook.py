from __future__ import annotations

import re
from typing import Iterable, Dict, Any, List
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapeResult
from .site_search import site_search
from .social_common import HttpClient, rate_limit_delay, normalize_url


def _to_mbasic(url: str) -> str:
    parts = urlparse(url)
    netloc = parts.netloc
    if "facebook.com" in netloc and not netloc.startswith("mbasic."):
        netloc = "mbasic.facebook.com"
    return urlunparse((parts.scheme or "https", netloc, parts.path, "", "", ""))


class FacebookScraper(BaseScraper):
    name = "facebook"

    def __init__(self, per_request_delay_seconds: float = 2.0, max_fetch_bytes: int = 1024 * 1024) -> None:
        self.per_request_delay_seconds = per_request_delay_seconds
        self.client = HttpClient()
        self.max_fetch_bytes = max_fetch_bytes

    def _extract_page(self, url: str, query: str) -> ScrapeResult:
        rate_limit_delay(self.per_request_delay_seconds)
        resp = self.client.get(_to_mbasic(url))
        text = resp.text[: self.max_fetch_bytes]
        soup = BeautifulSoup(text, "lxml")

        title = soup.title.text.strip() if soup.title else ""
        og_title = soup.find("meta", attrs={"property": "og:title"})
        display_name = og_title.get("content").strip() if og_title and og_title.get("content") else (title or "N/A")

        og_desc = soup.find("meta", attrs={"property": "og:description"})
        bio = og_desc.get("content").strip() if og_desc and og_desc.get("content") else ""

        # Followers heuristic
        followers = ""
        text_content = soup.get_text(" ")
        m = re.search(r"([\d,\.]+)\s+(followers|people follow this|likes)", text_content, flags=re.I)
        if m:
            followers = m.group(1)

        result: ScrapeResult = {
            "Search Query": query,
            "Platform": self.name,
            "Profile URL": normalize_url(url),
            "Handle": "",
            "Display Name": display_name,
            "Bio/About": bio,
            "Website": "",
            "Email": "",
            "Phone": "",
            "Followers": followers,
            "Location": "",
        }
        return result

    def search(self, query: str, max_results: int) -> Iterable[ScrapeResult]:
        # Discover candidates via DuckDuckGo site: search
        candidates: List[str] = site_search(query=query, site="facebook.com", num=max_results, engine="duckduckgo")
        for url in candidates:
            try:
                yield self._extract_page(url, query)
            except Exception:
                continue


