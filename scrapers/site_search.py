from __future__ import annotations

import html
import urllib.parse
from typing import List, Optional

from bs4 import BeautifulSoup

from .social_common import HttpClient, rate_limit_delay, normalize_url


def _duckduckgo_query_url(site: str, query: str, use_html: bool = True) -> str:
    q = f"site:{site} {query}"
    if use_html:
        return f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(q)}"
    else:
        # Try regular search endpoint
        return f"https://duckduckgo.com/?q={urllib.parse.quote_plus(q)}&ia=web"


def site_search(
    query: str, 
    site: str, 
    num: int = 500,  # Increased default from 100 to 500 for maximum results
    engine: str = "duckduckgo", 
    per_request_delay_seconds: float = 2.0,
    debug: bool = False
) -> List[str]:
    """Return top public result URLs for `site:<site> query` using DuckDuckGo HTML endpoint by default.
    
    Attempts multiple query variations to get more results when num > 10.
    """
    client = HttpClient()
    urls: List[str] = []

    if engine != "duckduckgo":
        engine = "duckduckgo"

    # If we need many results, try multiple query variations (lowered threshold)
    queries_to_try = [query]
    if num > 10:  # Lowered from 20 to trigger variations earlier
        # Add more variations to get maximum results
        queries_to_try.extend([
            f'"{query}"',  # Exact phrase
            f"{query} page",  # With "page"
            f"{query} profile",  # With "profile"
            f"{query} official",  # With "official"
            f"{query} account",  # With "account"
            f"{query} business",  # With "business"
            f"{query} company",  # With "company"
        ])
        if debug:
            print(f"[DEBUG] Will try {len(queries_to_try)} query variations to get more results")
    
    for query_variant in queries_to_try:
        if len(urls) >= num:
            break
        
        # Try HTML endpoint first, fallback to regular if needed
        search_url = _duckduckgo_query_url(site, query_variant, use_html=True)
        if debug:
            print(f"[DEBUG] site_search: {site} -> {search_url} (variant: {query_variant})")
        
        # Add longer delay before DuckDuckGo requests to avoid rate limiting
        rate_limit_delay(per_request_delay_seconds * 2)
        
        try:
            # Try with a session to maintain cookies
            session = client.session
            resp = session.get(search_url, allow_redirects=True)
            if debug:
                print(f"[DEBUG] Status: {resp.status_code}, Content length: {len(resp.text)}")
            
            # If blocked (202), wait longer and retry
            if resp.status_code == 202:
                if debug:
                    print(f"[DEBUG] Blocked (202), waiting longer and retrying...")
                rate_limit_delay(per_request_delay_seconds * 5)
                resp = session.get(search_url, allow_redirects=True)
                if debug:
                    print(f"[DEBUG] Retry Status: {resp.status_code}, Content length: {len(resp.text)}")
            
            # If still blocked, try regular endpoint
            if resp.status_code == 202 or ("DuckDuckGo" in resp.text[:500] and len(resp.text) < 20000):
                if debug:
                    print(f"[DEBUG] HTML endpoint blocked, trying regular endpoint...")
                rate_limit_delay(per_request_delay_seconds * 2)
                search_url = _duckduckgo_query_url(site, query_variant, use_html=False)
                resp = session.get(search_url, allow_redirects=True)
                if debug:
                    print(f"[DEBUG] Regular endpoint Status: {resp.status_code}, Content length: {len(resp.text)}")
            
            soup = BeautifulSoup(resp.text, "lxml")
            
            # Try multiple selectors in order of preference
            selectors = [
                "a.result__a",
                "a.result__url",
                ".result__title a",
                "div.result a",
                "a[class*='result']",
                "a[href]",
            ]
            
            # Also try to find links by domain match in href
            domain_match_links = soup.find_all("a", href=True)
            
            def extract_url_from_link(link, target_domain: str) -> Optional[str]:
                """Extract actual URL from a link element, handling DuckDuckGo redirects."""
                href = link.get("href")
                if not href:
                    return None
                
                # Handle DuckDuckGo redirect URLs
                if href.startswith("/l/") or "duckduckgo.com" in href:
                    # Try to extract from query parameter
                    if "uddg=" in href:
                        try:
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            if "uddg" in parsed and parsed["uddg"]:
                                href = urllib.parse.unquote(parsed["uddg"][0])
                            else:
                                return None
                        except Exception:
                            return None
                    # Check for data-uddg attribute
                    elif link.get("data-uddg"):
                        href = urllib.parse.unquote(link.get("data-uddg"))
                    else:
                        return None
                
                try:
                    normalized = normalize_url(html.unescape(href))
                    # Check if it matches the target domain
                    if target_domain in normalized:
                        return normalized
                except Exception:
                    pass
                return None
            
            target_domain = site.split('/')[0]
            
            # Try selectors first
            for selector in selectors:
                if len(urls) >= num:
                    break
                try:
                    links = soup.select(selector)
                    if debug:
                        print(f"[DEBUG] Selector '{selector}': {len(links)} links found")
                    
                    for link in links:
                        if len(urls) >= num:
                            break
                        url = extract_url_from_link(link, target_domain)
                        if url and url not in urls:
                            urls.append(url)
                            if debug:
                                print(f"[DEBUG] Added: {url}")
                except Exception as e:
                    if debug:
                        print(f"[DEBUG] Selector '{selector}' error: {e}")
                    continue
            
            # Fallback: search all links for domain match
            if len(urls) < num:
                for link in domain_match_links:
                    if len(urls) >= num:
                        break
                    url = extract_url_from_link(link, target_domain)
                    if url and url not in urls:
                        urls.append(url)
                        if debug:
                            print(f"[DEBUG] Added (fallback): {url}")
            
            if debug:
                print(f"[DEBUG] Found {len(urls)} URLs so far from variant '{query_variant}'")
        
        except Exception as e:
            if debug:
                print(f"[DEBUG] site_search error for variant '{query_variant}': {e}")
            continue  # Try next variant
        
        # Small delay between query variants
        if len(queries_to_try) > 1:
            rate_limit_delay(per_request_delay_seconds)
    
    if debug:
        print(f"[DEBUG] Final URLs found: {len(urls)}")

    return urls


