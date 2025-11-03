from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlparse, urlunparse

import requests
from tenacity import (
	retry,
	stop_after_attempt,
	wait_exponential_jitter,
	retry_if_exception_type,
)


DEFAULT_UAS = [
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
]


def build_headers(accept_language: str = "en-US,en;q=0.9") -> Dict[str, str]:
	ua = random.choice(DEFAULT_UAS)
	return {
		"User-Agent": ua,
		"Accept-Language": accept_language,
		"Cache-Control": "no-cache",
	}


def rate_limit_delay(base_seconds: float, jitter_range: float = 0.75) -> None:
	"""Sleep with jitter to respect rate limits."""
	delay = base_seconds + random.uniform(0, jitter_range)
	time.sleep(delay)


@dataclass
class HttpClient:
	"""Simple HTTP client with retries and sane defaults for public pages."""
	timeout_seconds: float = 12.0
	accept_language: str = "en-US,en;q=0.9"

	def __post_init__(self) -> None:
		self.session = requests.Session()
		self.session.headers.update(build_headers(self.accept_language))

	@retry(
		stop=stop_after_attempt(3),
		wait=wait_exponential_jitter(initial=1, max=12),
		retry=retry_if_exception_type((requests.RequestException,)),
	)
	def get(self, url: str) -> requests.Response:
		resp = self.session.get(url, timeout=self.timeout_seconds)
		resp.raise_for_status()
		return resp


SOCIAL_HOST_PATTERNS = {
	"facebook": re.compile(r"(?:^|\.)facebook\.com$", re.I),
	"instagram": re.compile(r"(?:^|\.)instagram\.com$", re.I),
	"linkedin": re.compile(r"(?:^|\.)linkedin\.com$", re.I),
	"x": re.compile(r"(?:^|\.)twitter\.com$", re.I),
	"youtube": re.compile(r"(?:^|\.)youtube\.com$", re.I),
	"tiktok": re.compile(r"(?:^|\.)tiktok\.com$", re.I),
}


def normalize_url(url: str) -> str:
	parts = urlparse(url)
	netloc = parts.netloc.lower()
	path = re.sub(r"/+", "/", parts.path)
	return urlunparse((parts.scheme or "https", netloc, path, "", "", ""))


def extract_social_links_from_html(html: str) -> Dict[str, List[str]]:
	"""Extract social profile links from raw HTML by regex; keeps it dependency-light here."""
	results: Dict[str, List[str]] = {k: [] for k in SOCIAL_HOST_PATTERNS.keys()}
	for match in re.finditer(r"href=\"([^\"]+)\"", html, flags=re.I):
		url = match.group(1)
		try:
			normalized = normalize_url(url)
		except Exception:
			continue
		host = urlparse(normalized).netloc
		for platform, host_re in SOCIAL_HOST_PATTERNS.items():
			if host_re.search(host):
				results[platform].append(normalized)
	return results


def unique_keep_order(urls: Iterable[str]) -> List[str]:
	seen = set()
	ordered: List[str] = []
	for u in urls:
		if u in seen:
			continue
		seen.add(u)
		ordered.append(u)
	return ordered


