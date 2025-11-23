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
        
        # Try mbasic first, fallback to regular if needed
        try:
            resp = self.client.get(_to_mbasic(url))
        except Exception:
            try:
                resp = self.client.get(url)
            except Exception:
                # If both fail, return minimal data
                return {
                    "Search Query": query,
                    "Platform": self.name,
                    "Profile URL": normalize_url(url),
                    "Handle": self._extract_handle_from_url(url),
                    "Display Name": self._extract_handle_from_url(url).replace("_", " ").title(),
                    "Bio/About": "",
                    "Website": "",
                    "Email": "",
                    "Phone": "",
                    "Followers": "",
                    "Location": "",
                }
        
        text = resp.text[: self.max_fetch_bytes]
        soup = BeautifulSoup(text, "lxml")

        title = soup.title.text.strip() if soup.title else ""
        og_title = soup.find("meta", attrs={"property": "og:title"})
        display_name = og_title.get("content").strip() if og_title and og_title.get("content") else (title or "")
        
        # Extract handle from URL if we have a minimal URL structure
        handle = self._extract_handle_from_url(url)
        if not display_name or "log in" in display_name.lower() or "sign up" in display_name.lower():
            # Use URL-based name if login page
            display_name = handle.replace("_", " ").replace("-", " ").title() if handle else url.split("/")[-1].replace("_", " ").title()
            if not display_name or display_name == "N/A":
                display_name = url.split("/")[-1] if "/" in url else url

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
            "Handle": handle,
            "Display Name": display_name,
            "Bio/About": bio,
            "Website": "",
            "Email": "",
            "Phone": "",
            "Followers": followers,
            "Location": "",
        }
        return result
    
    def _extract_handle_from_url(self, url: str) -> str:
        """Extract handle/page name from Facebook URL."""
        import re
        # Pattern: facebook.com/username or facebook.com/pages/name
        patterns = [
            r"facebook\.com/([^/?]+)",
            r"facebook\.com/pages/[^/]+/([^/?]+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, url, re.I)
            if m:
                handle = m.group(1)
                if handle and handle not in ["groups", "pages", "profile", "login"]:
                    return handle
        return ""

    def search(self, query: str, max_results: int) -> Iterable[ScrapeResult]:
        print(f"[FACEBOOK] Searching for: {query}")
        try:
            # Discover candidates via DuckDuckGo site: search
            # Use much higher limit to get maximum results (multiply by 10 for more candidates)
            search_limit = max(max_results * 10, 500) if max_results > 0 else 1000
            candidates: List[str] = site_search(query=query, site="facebook.com", num=search_limit, engine="duckduckgo", debug=False)
            if not candidates:
                print(f"[FACEBOOK] No candidate URLs found")
                return  # No candidates found
            
            print(f"[FACEBOOK] Found {len(candidates)} candidate URLs, processing...")
            collected = 0
            
            for idx, url in enumerate(candidates, 1):
                try:
                    print(f"[FACEBOOK] Processing [{idx}/{len(candidates)}]: {url[:60]}...")
                    result = self._extract_page(url, query)
                    # Always yield if we have a valid URL - we'll extract what we can
                    if result.get("Profile URL") and result.get("Profile URL") != "N/A":
                        collected += 1
                        print(f"[FACEBOOK] ✓ [{collected}] Extracted: {result.get('Display Name', 'N/A')[:50]}")
                        yield result
                    else:
                        print(f"[FACEBOOK] [SKIP] Invalid result for URL")
                except ValueError as e:
                    # Login page detected
                    print(f"[FACEBOOK] [SKIP] Login required: {url[:60]}")
                    # Even on error, try to return minimal data from URL
                    try:
                        handle = self._extract_handle_from_url(url)
                        if handle:
                            collected += 1
                            result = {
                                "Search Query": query,
                                "Platform": self.name,
                                "Profile URL": normalize_url(url),
                                "Handle": handle,
                                "Display Name": handle.replace("_", " ").replace("-", " ").title(),
                                "Bio/About": "",
                                "Website": "",
                                "Email": "",
                                "Phone": "",
                                "Followers": "",
                                "Location": "",
                            }
                            print(f"[FACEBOOK] ✓ [{collected}] Extracted from URL: {result.get('Display Name')}")
                            yield result
                    except Exception:
                        continue
                except Exception as e:
                    print(f"[FACEBOOK] [ERROR] Failed to extract {url[:60]}: {e}")
                    # Even on error, try to return minimal data from URL
                    try:
                        handle = self._extract_handle_from_url(url)
                        if handle:
                            collected += 1
                            result = {
                                "Search Query": query,
                                "Platform": self.name,
                                "Profile URL": normalize_url(url),
                                "Handle": handle,
                                "Display Name": handle.replace("_", " ").replace("-", " ").title(),
                                "Bio/About": "",
                                "Website": "",
                                "Email": "",
                                "Phone": "",
                                "Followers": "",
                                "Location": "",
                            }
                            print(f"[FACEBOOK] ✓ [{collected}] Extracted from URL (minimal): {result.get('Display Name')}")
                            yield result
                    except Exception:
                        continue
            
            print(f"[FACEBOOK] Complete. Collected {collected}/{len(candidates)} results")
        except Exception as e:
            print(f"[FACEBOOK] FATAL ERROR: {e}")
            import traceback
            traceback.print_exc()


