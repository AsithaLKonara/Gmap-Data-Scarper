from __future__ import annotations

import csv
import datetime
import os
import time
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

import yaml

from scrapers.base import BaseScraper, COMMON_FIELDS
from scrapers.google_maps import GoogleMapsScraper
from scrapers.facebook import FacebookScraper
from scrapers.instagram import InstagramScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.x_twitter import XScraper
from scrapers.youtube import YouTubeScraper
from scrapers.tiktok import TikTokScraper
from scrapers.yelp import YelpScraper
from scrapers.crunchbase import CrunchbaseScraper
from scrapers.tripadvisor import TripAdvisorScraper
from scrapers.indeed import IndeedScraper
from scrapers.github import GitHubScraper
from utils.csv_writer import write_row_incremental

# v2.0+ Classification and enrichment modules
try:
    from classification import BusinessClassifier, JobClassifier, EducationParser
    from utils.geolocation import GeolocationExtractor
    CLASSIFICATION_ENABLED = True
except ImportError:
    CLASSIFICATION_ENABLED = False
    BusinessClassifier = None
    JobClassifier = None
    EducationParser = None
    GeolocationExtractor = None

# v3.0+ Individual lead classification
try:
    from classification.individual_classifier import IndividualClassifier
    INDIVIDUAL_CLASSIFICATION_ENABLED = True
except ImportError:
    INDIVIDUAL_CLASSIFICATION_ENABLED = False
    IndividualClassifier = None


OnLog = Callable[[str], None]
OnProgress = Callable[[Dict[str, int]], None]
OnResult = Callable[[Dict[str, str]], None]
OnFinish = Callable[[], None]


def read_config(path: str) -> Dict:
	"""Read YAML config file, return empty dict if file doesn't exist or is invalid."""
	try:
		if not os.path.exists(path):
			return {}
		with open(path, "r", encoding="utf-8") as f:
			return yaml.safe_load(f) or {}
	except (yaml.YAMLError, IOError, OSError):
		return {}


def read_queries(path: str) -> List[str]:
	with open(path, "r", encoding="utf-8") as f:
		return [q.strip() for q in f.readlines() if q.strip()]


def load_processed_keys(csv_path: str) -> Set[Tuple[str, str, str]]:
	if not os.path.exists(os.path.expanduser(csv_path)):
		return set()
	processed: Set[Tuple[str, str, str]] = set()
	try:
		with open(os.path.expanduser(csv_path), "r", encoding="utf-8") as f:
			reader = csv.DictReader(f)
			for row in reader:
				processed.add((row.get("Search Query", ""), row.get("Platform", ""), row.get("Profile URL", "")))
	except Exception:
		pass
	return processed


def get_scraper_instances(enabled: List[str], headless: bool) -> List[BaseScraper]:
	instances: List[BaseScraper] = []
	mapping: Dict[str, BaseScraper] = {
		"google_maps": GoogleMapsScraper(headless=headless),
		"facebook": FacebookScraper(),
		"instagram": InstagramScraper(),
		"linkedin": LinkedInScraper(),
		"x": XScraper(),
		"youtube": YouTubeScraper(),
		"tiktok": TikTokScraper(),
		"yelp": YelpScraper(headless=headless),
		"crunchbase": CrunchbaseScraper(headless=headless),
		"tripadvisor": TripAdvisorScraper(headless=headless),
		"indeed": IndeedScraper(headless=headless),
		"github": GitHubScraper(headless=headless),
	}
	for key in enabled:
		scraper = mapping.get(key)
		if scraper is not None:
			instances.append(scraper)
	return instances


class StopFlag:
	def __init__(self) -> None:
		self._stop = False

	def request_stop(self) -> None:
		self._stop = True

	def should_stop(self) -> bool:
		return self._stop

	def set(self) -> None:
		"""Alias for request_stop for compatibility."""
		self.request_stop()


class PauseFlag:
	"""Flag to pause and resume scraping operations."""
	def __init__(self) -> None:
		self._paused = False
		self._lock = False  # Lock to prevent race conditions

	def request_pause(self) -> None:
		"""Request to pause the scraping operation."""
		self._paused = True

	def request_resume(self) -> None:
		"""Request to resume the scraping operation."""
		self._paused = False

	def is_paused(self) -> bool:
		"""Check if scraping is currently paused."""
		return self._paused

	def wait_if_paused(self, check_interval: float = 0.5) -> None:
		"""Wait if paused, checking periodically for resume."""
		while self._paused:
			time.sleep(check_interval)


def run_orchestrator(
	config_path: str,
	queries_path: Optional[str] = None,
	queries_list: Optional[List[str]] = None,
	enabled_platforms: Optional[List[str]] = None,
	skip_gmaps: bool = False,
	max_results_override: Optional[int] = None,
	on_log: Optional[OnLog] = None,
	on_progress: Optional[OnProgress] = None,
	on_result: Optional[OnResult] = None,
	on_finish: Optional[OnFinish] = None,
	stop_flag: Optional[StopFlag] = None,
	pause_flag: Optional[PauseFlag] = None,
	phone_only: bool = False,
) -> None:
	cfg = read_config(config_path)
	enabled_cfg: List[str] = cfg.get("enabled_platforms", ["facebook", "instagram", "linkedin", "x", "youtube", "tiktok"])  # default
	if not skip_gmaps:
		enabled_cfg = ["google_maps"] + enabled_cfg
	if enabled_platforms:
		enabled_cfg = enabled_platforms

	headless = bool(cfg.get("headless", True))
	per_platform_delay = float(cfg.get("per_platform_delay_seconds", 8))
	max_results = int(cfg.get("max_results_per_query", 0))  # 0 = unlimited
	if max_results_override is not None and max_results_override > 0:
		max_results = max_results_override
	elif max_results == 0:
		max_results = 9999999  # Increased from 999999 for truly unlimited mode (supports millions of results)

	output_dir = os.path.expanduser(cfg.get("output_dir", "~/Documents/social_leads"))
	os.makedirs(output_dir, exist_ok=True)
	consolidated_csv = os.path.join(output_dir, "all_platforms.csv")

	processed = load_processed_keys(consolidated_csv) if bool(cfg.get("resume", True)) else set()

	scrapers: List[BaseScraper] = get_scraper_instances(enabled_cfg, headless=headless)
	
	# Get queries from list or file
	if queries_list:
		queries = queries_list
	elif queries_path:
		queries = read_queries(queries_path)
	else:
		queries = []
		if on_log:
			on_log("[ERROR] No queries provided (neither queries_path nor queries_list)")
		return
	
	# Initialize v2.0+ classification and enrichment modules
	business_classifier = None
	job_classifier = None
	education_parser = None
	geolocation_extractor = None
	individual_classifier = None
	
	if CLASSIFICATION_ENABLED:
		try:
			business_classifier = BusinessClassifier()
			job_classifier = JobClassifier()
			education_parser = EducationParser()
			geolocation_extractor = GeolocationExtractor()
			if on_log:
				on_log("[v2.0] Classification and enrichment enabled")
		except Exception as e:
			if on_log:
				on_log(f"[v2.0] Warning: Could not initialize classifiers: {e}")
	
	# Initialize v3.0+ individual lead classifier
	if INDIVIDUAL_CLASSIFICATION_ENABLED:
		try:
			individual_classifier = IndividualClassifier()
			if on_log:
				on_log("[v3.0] Individual lead classification enabled")
		except Exception as e:
			if on_log:
				on_log(f"[v3.0] Warning: Could not initialize individual classifier: {e}")
	
	# Get filter options from config
	filters = cfg.get("filters", {})
	business_types_filter = filters.get("business_type", [])
	job_levels_filter = filters.get("job_level", [])
	location_filter = filters.get("location", None)
	radius_km = filters.get("radius_km", None)
	date_range = filters.get("date_range", None)
	active_within_days = filters.get("active_within_days", None)
	boosted_only = filters.get("boosted_only", False)
	education_levels_filter = filters.get("education_level", [])
	
	# v3.0+ Education/Career filters
	field_of_study_filter = filters.get("field_of_study", None)
	degree_type_filter = filters.get("degree_type", [])
	student_only_filter = filters.get("student_only", False)
	institution_filter = filters.get("institution", None)
	
	# Initialize activity scraper for Phase 2
	activity_scraper = None
	if CLASSIFICATION_ENABLED:
		try:
			from enrichment import ActivityScraper
			activity_scraper = ActivityScraper()
		except ImportError:
			pass
	
	# Initialize lead scorer for Phase 3
	lead_scorer = None
	try:
		from intelligence import LeadScorer
		lead_scorer = LeadScorer()
		if on_log:
			on_log("[v2.2] Lead scoring enabled")
	except ImportError:
		pass

	# Initialize performance features (v2.3+)
	url_cache = None
	rate_limiter = None
	try:
		from cache.url_cache import URLCache
		url_cache = URLCache(ttl_days=30)
		if on_log:
			on_log("[v2.3] URL caching enabled")
	except ImportError:
		pass
	
	try:
		from utils.rate_limiter import RateLimiter
		base_delay = float(cfg.get("per_platform_delay_seconds", 8))
		rate_limiter = RateLimiter(base_delay=base_delay, min_delay=0.5, max_delay=10.0)
		if on_log:
			on_log("[v2.3] Smart rate limiting enabled")
	except ImportError:
		pass

	if on_log:
		on_log(f"[START] Queries: {len(queries)} | Platforms: {', '.join([s.platform_name() for s in scrapers])}")

	progress_counts: Dict[str, int] = {s.platform_name(): 0 for s in scrapers}
	
	# Cross-platform deduplication tracking (by normalized phone and URL)
	seen_phones: Set[str] = set()
	seen_urls: Set[str] = set()

	for qi, query in enumerate(queries, 1):
		if stop_flag and stop_flag.should_stop():
			break
		# Check for pause before processing query
		if pause_flag:
			pause_flag.wait_if_paused()
		if on_log:
			on_log(f"\n[QUERY {qi}/{len(queries)}] {query}")
		for si, scraper in enumerate(scrapers, 1):
			if stop_flag and stop_flag.should_stop():
				break
			# Check for pause before processing platform
			if pause_flag:
				pause_flag.wait_if_paused()
			plat = scraper.platform_name()
			plat_csv = os.path.join(output_dir, f"{plat}.csv")
			if on_log:
				on_log(f"  [SCRAPER {si}/{len(scrapers)}] {plat}")
			try:
				result_count = 0
				
				# Apply rate limiting for social media scrapers (not Google Maps)
				if rate_limiter and plat != "google_maps":
					rate_limiter.wait()
				
				for result in scraper.search(query=query, max_results=max_results):
					if stop_flag and stop_flag.should_stop():
						break
					# Check for pause before processing each result
					if pause_flag:
						pause_flag.wait_if_paused()
					
					profile_url = result.get("Profile URL", "")
					
					# Check URL cache before processing
					if url_cache and profile_url and profile_url != "N/A":
						if url_cache.is_cached(profile_url):
							if on_log:
								on_log(f"    [CACHE HIT] Skipped (cached): {profile_url[:60]}")
							# Still record success for rate limiter
							if rate_limiter and plat != "google_maps":
								rate_limiter.record_success()
							continue
					
					key = (result.get("Search Query", ""), result.get("Platform", plat), profile_url)
					if key in processed:
						if on_log:
							on_log(f"    [SKIP] Already processed: {profile_url[:60]}")
						continue
					
					# v2.0+ Classification and enrichment
					if business_classifier:
						try:
							result = business_classifier.classify(result)
						except Exception as e:
							if on_log:
								on_log(f"    [WARN] Business classification failed: {e}")
					
					if job_classifier:
						try:
							result = job_classifier.classify(result)
						except Exception as e:
							if on_log:
								on_log(f"    [WARN] Job classification failed: {e}")
					
					# Extract location data
					if geolocation_extractor:
						try:
							address = result.get("Address", "")
							if address and address != "N/A":
								location_data = geolocation_extractor.extract_location(address)
								result.update(location_data)
						except Exception as e:
							if on_log:
								on_log(f"    [WARN] Geolocation extraction failed: {e}")
					
					# Extract education data (Phase 2)
					if education_parser:
						try:
							result = education_parser.parse(result)
						except Exception as e:
							if on_log:
								on_log(f"    [WARN] Education parsing failed: {e}")
					
					# Apply v3.0+ individual lead classification
					if individual_classifier:
						try:
							result = individual_classifier.classify(result)
						except Exception as e:
							if on_log:
								on_log(f"    [WARN] Individual classification failed: {e}")
					
					# Scrape activity data (Phase 2)
					if activity_scraper and plat in ["facebook", "instagram", "x", "tiktok"]:
						try:
							profile_url = result.get("Profile URL", "")
							if profile_url and profile_url != "N/A":
								activity_data = activity_scraper.scrape_activity(profile_url, plat)
								result.update(activity_data)
						except Exception as e:
							if on_log:
								on_log(f"    [WARN] Activity scraping failed: {e}")
					
					# Apply filters
					if business_types_filter and result.get("business_type", "N/A") not in business_types_filter:
						if on_log:
							on_log(f"    [FILTER] Skipped (business_type: {result.get('business_type', 'N/A')})")
						continue
					
					if job_levels_filter and result.get("seniority_level", "N/A") not in job_levels_filter:
						if on_log:
							on_log(f"    [FILTER] Skipped (seniority_level: {result.get('seniority_level', 'N/A')})")
						continue
					
					if location_filter and geolocation_extractor:
						location_matches = geolocation_extractor.filter_by_location([result], location_filter, radius_km)
						if not location_matches:
							if on_log:
								on_log(f"    [FILTER] Skipped (location: {location_filter})")
							continue
					
					# Time-based filtering (Phase 2)
					if active_within_days and activity_scraper:
						last_post = result.get("last_post_date", "N/A")
						if not activity_scraper.is_active_within_days(last_post, active_within_days):
							if on_log:
								on_log(f"    [FILTER] Skipped (not active within {active_within_days} days)")
							continue
					
					# Boosted posts only filter (Phase 2)
					if boosted_only:
						is_boosted = result.get("is_boosted", "false").lower()
						if is_boosted != "true":
							if on_log:
								on_log(f"    [FILTER] Skipped (not boosted)")
							continue
					
					# Education level filter (Phase 2)
					if education_levels_filter:
						result_education = result.get("education_level", "N/A")
						if result_education not in education_levels_filter:
							if on_log:
								on_log(f"    [FILTER] Skipped (education_level: {result_education})")
							continue
					
					# v3.0+ Education/Career filters
					if field_of_study_filter:
						result_field = result.get("field_of_study", "N/A")
						if field_of_study_filter.lower() not in result_field.lower():
							if on_log:
								on_log(f"    [FILTER] Skipped (field_of_study: {result_field})")
							continue
					
					if degree_type_filter:
						result_degree = result.get("degree_program", "N/A")
						degree_match = False
						for degree_type in degree_type_filter:
							if degree_type.lower() in result_degree.lower():
								degree_match = True
								break
						if not degree_match:
							if on_log:
								on_log(f"    [FILTER] Skipped (degree_type: {result_degree})")
							continue
					
					if student_only_filter:
						lead_type = result.get("lead_type", "business")
						if lead_type != "individual":
							if on_log:
								on_log(f"    [FILTER] Skipped (not individual lead)")
							continue
					
					if institution_filter:
						result_institution = result.get("institution_name", "N/A")
						if institution_filter.lower() not in result_institution.lower():
							if on_log:
								on_log(f"    [FILTER] Skipped (institution: {result_institution})")
							continue
					
					# Date range filtering (Phase 2)
					if date_range:
						# Parse date range (YYYY-MM-DD:YYYY-MM-DD)
						try:
							start_str, end_str = date_range.split(":")
							start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d")
							end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d")
							
							# Check extracted_at or last_post_date
							extracted_at = result.get("extracted_at", "")
							last_post = result.get("last_post_date", "")
							
							# Try to parse dates and check range
							date_to_check = None
							if extracted_at and extracted_at != "N/A":
								try:
									date_to_check = datetime.fromisoformat(extracted_at.replace("Z", "+00:00"))
								except:
									pass
							
							if not date_to_check and last_post and last_post != "N/A":
								# Try to parse relative dates
								if activity_scraper:
									# Use activity scraper's date parsing logic
									# For now, skip if we can't parse
									pass
							
							if date_to_check:
								if not (start_date <= date_to_check.date() <= end_date):
									if on_log:
										on_log(f"    [FILTER] Skipped (date out of range)")
									continue
						except Exception as e:
							if on_log:
								on_log(f"    [WARN] Date range filter error: {e}")
					
					# AI-powered insights (Phase 5)
					try:
						from ai import IntentDetector, SentimentAnalyzer, LeadSummarizer
						intent_detector = IntentDetector()
						sentiment_analyzer = SentimentAnalyzer()
						summarizer = LeadSummarizer()
						
						result = intent_detector.detect(result)
						result = sentiment_analyzer.analyze(result)
						result = summarizer.summarize(result)
					except ImportError:
						pass
					except Exception as e:
						if on_log:
							on_log(f"    [WARN] AI insights failed: {e}")
					
					# Calculate lead score (Phase 3)
					if lead_scorer:
						try:
							result = lead_scorer.score(result)
						except Exception as e:
							if on_log:
								on_log(f"    [WARN] Lead scoring failed: {e}")
							result["lead_score"] = "N/A"
					else:
						result["lead_score"] = "N/A"
					
					# Add extracted_at timestamp
					result["extracted_at"] = datetime.datetime.now().isoformat()
					
					# Initialize missing v2.0+ fields with N/A
					v2_fields = [
						"last_post_date", "is_boosted", "post_engagement",
						"education_level", "institution_name",
						"intent_category", "sentiment_score",
						"sentiment_trend", "lead_summary"
					]
					for field in v2_fields:
						if field not in result:
							result[field] = "N/A"
					
					# Initialize v3.0+ phone extraction fields
					v3_phone_fields = [
						"phone_raw", "phone_normalized", "phone_validation_status",
						"phone_confidence_score", "phone_source", "phone_element_selector",
						"phone_screenshot_path", "phone_timestamp"
					]
					for field in v3_phone_fields:
						if field not in result:
							result[field] = "N/A"
					
					# Initialize v3.0+ individual lead fields
					v3_lead_fields = [
						"lead_type", "field_of_study", "degree_program", "graduation_year"
					]
					for field in v3_lead_fields:
						if field not in result:
							result[field] = "N/A"
					
					# Cross-platform deduplication check
					# Check by normalized phone number
					phone_normalized = result.get("phone_normalized", "")
					if phone_normalized and phone_normalized != "N/A":
						if phone_normalized in seen_phones:
							if on_log:
								on_log(f"    [DEDUP] Skipped (duplicate phone across platforms): {phone_normalized[:20]}")
							continue
						seen_phones.add(phone_normalized)
					
					# Check by profile URL (already checked above, but ensure it's in seen_urls)
					if profile_url and profile_url != "N/A":
						if profile_url in seen_urls:
							if on_log:
								on_log(f"    [DEDUP] Skipped (duplicate URL across platforms): {profile_url[:60]}")
							continue
						seen_urls.add(profile_url)
					
					# Phone-only filter: Skip if phone_only is True and no phone found
					if phone_only:
						phone = result.get("Phone", "") or result.get("phone", "")
						phone_normalized_check = result.get("phone_normalized", "")
						has_phone = (
							(phone and phone != "N/A" and phone.strip()) or
							(phone_normalized_check and phone_normalized_check != "N/A" and phone_normalized_check.strip())
						)
						if not has_phone:
							if on_log:
								display_name_check = result.get("Display Name", "Unknown")
								on_log(f"    [FILTER] Skipped (no phone number): {display_name_check[:60]}")
							continue
					
					try:
						write_row_incremental(plat_csv, COMMON_FIELDS, result)
						write_row_incremental(consolidated_csv, COMMON_FIELDS, result)
						processed.add(key)
						
						# Add to URL cache
						if url_cache and profile_url and profile_url != "N/A":
							try:
								url_cache.add(profile_url, plat)
							except Exception as e:
								if on_log:
									on_log(f"    [WARN] Cache add failed: {e}")
						
						# Record success for rate limiter
						if rate_limiter and plat != "google_maps":
							rate_limiter.record_success()
						
						progress_counts[plat] = progress_counts.get(plat, 0) + 1
						result_count += 1
						
						# Show collected lead
						display_name = result.get("Display Name", "N/A")
						profile_url = result.get("Profile URL", "N/A")
						handle = result.get("Handle", "")
						
						if on_log:
							lead_info = f"    ✓ [{result_count}] {display_name[:60]}"
							if handle and handle != "N/A":
								lead_info += f" (@{handle})"
							lead_info += f"\n         URL: {profile_url[:70]}"
							on_log(lead_info)
						
						if on_result:
							on_result(result)
						if on_progress:
							on_progress(dict(progress_counts))
					except Exception as write_error:
						if on_log:
							on_log(f"    [ERROR] Failed to write result: {write_error}")
						continue
				
				if result_count > 0:
					if on_log:
						on_log(f"    [OK] {plat}: {result_count} leads collected")
				else:
					if on_log:
						on_log(f"    [INFO] {plat}: No new leads found")
						
			except KeyboardInterrupt:
				if on_log:
					on_log(f"    [INTERRUPTED] {plat} scraper stopped by user")
				raise
			except Exception as e:
				# Record error for rate limiter
				if rate_limiter and plat != "google_maps":
					rate_limiter.record_error()
				if on_log:
					on_log(f"    [ERROR] {plat} scraper error: {e}")
					import traceback
					error_trace = traceback.format_exc()
					on_log(f"    [TRACE] {error_trace}")
			time.sleep(per_platform_delay)

	if on_log:
		on_log(f"\n[DONE] Consolidated CSV: {consolidated_csv}")
	if on_finish:
		on_finish()


