from __future__ import annotations

import re
from typing import Iterable, Dict, Any, List

from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapeResult
from .site_search import site_search
from .social_common import HttpClient, rate_limit_delay, normalize_url


class TikTokScraper(BaseScraper):
    name = "tiktok"

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

        followers = ""
        m = re.search(r"([\d,\.]+)\s+Followers", soup.get_text(" "), flags=re.I)
        if m:
            followers = m.group(1)

        handle = ""
        m2 = re.search(r"\(@([^\)]+)\)", display_name)
        if m2:
            handle = m2.group(1)

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
            "Followers": followers,
            "Location": "",
        }
        return result

    def search(self, query: str, max_results: int) -> Iterable[ScrapeResult]:
        candidates: List[str] = site_search(query=query, site="tiktok.com", num=max_results, engine="duckduckgo")
        for url in candidates:
            try:
                yield self._extract_profile(url, query)
            except Exception:
                continue


