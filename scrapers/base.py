from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterable, Any


ScrapeResult = Dict[str, Any]


class BaseScraper(ABC):
	"""
	Abstract base for all platform scrapers.

	Implementations should yield normalized result dicts containing at least:
	- "Search Query"
	- "Platform"
	- "Profile URL"
	- "Handle"
	- "Display Name"

	Additional optional fields are allowed and will be written if present.
	"""

	name: str = "base"

	@abstractmethod
	def search(self, query: str, max_results: int) -> Iterable[ScrapeResult]:
		"""Search for public profiles matching the query and yield results."""
		raise NotImplementedError

	def normalize(self, raw: ScrapeResult) -> ScrapeResult:
		"""Optionally normalize a raw dict to the common schema."""
		return raw

	def platform_name(self) -> str:
		return self.name


# Common normalized field keys used across scrapers
COMMON_FIELDS = [
	"Search Query",
	"Platform",
	"Profile URL",
	"Handle",
	"Display Name",
	"Bio/About",
	"Website",
	"Email",
	"Phone",
	"Followers",
	"Location",
]


