from __future__ import annotations

from typing import Dict, List

from .social_common import HttpClient, extract_social_links_from_html, unique_keep_order


def discover_social_from_website(homepage_url: str) -> Dict[str, List[str]]:
    """Fetch homepage and return discovered social profile URLs grouped by platform."""
    client = HttpClient()
    resp = client.get(homepage_url)
    links = extract_social_links_from_html(resp.text)
    return {platform: unique_keep_order(urls) for platform, urls in links.items() if urls}


