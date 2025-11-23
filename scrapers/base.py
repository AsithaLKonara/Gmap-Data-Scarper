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
	# v2.0+ fields (optional, default to N/A)
	"business_type",
	"industry",
	"sub_category",
	"city",
	"region",
	"country",
	"postal_code",
	"job_title",
	"seniority_level",
	"education_level",
	"institution_name",
	"last_post_date",
	"is_boosted",
	"post_engagement",
	"lead_score",
	"intent_category",
	"sentiment_score",
	"sentiment_trend",
	"lead_summary",
	"extracted_at",
	# v3.0+ Phone extraction fields
	"phone_raw",
	"phone_normalized",
	"phone_validation_status",
	"phone_confidence_score",
	"phone_source",
	"phone_element_selector",
	"phone_screenshot_path",
	"phone_timestamp",
	# v3.0+ Individual lead fields
	"lead_type",
	"field_of_study",
	"degree_program",
	"graduation_year",
]


