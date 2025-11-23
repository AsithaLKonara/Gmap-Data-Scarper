from __future__ import annotations

import re
import time
import urllib.parse
from typing import Iterable, Dict, Any, List, Set, Optional
from selenium.webdriver.remote.webelement import WebElement

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

from .base import BaseScraper, ScrapeResult


class GoogleMapsScraper(BaseScraper):
    """
    Public Google Maps scraper yielding normalized business details.

    Notes:
    - Uses Selenium; requires Chrome installed.
    - Does NOT disable JavaScript or CSS.
    """

    name = "google_maps"

    def __init__(self, headless: bool = True, delay_between_results_seconds: int = 1) -> None:
        self.headless = headless
        self.delay_between_results_seconds = delay_between_results_seconds  # Reduced delay for faster processing

    def _setup_driver(self) -> webdriver.Chrome:
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        
        # Apply anti-detection enhancements
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from backend.services.anti_detection import get_anti_detection_service
            anti_detection = get_anti_detection_service()
            options = anti_detection.enhance_chrome_options(options)
        except Exception as e:
            # Fallback to basic options if anti-detection fails
            print(f"[GMAPS] Anti-detection not available: {e}")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Apply fingerprint randomization
        try:
            anti_detection.randomize_fingerprint(driver)
        except:
            pass
        
        return driver

    def _safe_get(self, driver: webdriver.Chrome, url: str, retries: int = 3) -> bool:
        for _ in range(retries):
            try:
                driver.get(url)
                return True
            except Exception:
                time.sleep(2)
        return False

    def _scroll_results(self, driver: webdriver.Chrome) -> bool:
        """Improved scroll function with multiple strategies and better error handling."""
        try:
            # Wait longer for results to load after search
            time.sleep(5)  # Give Google Maps time to render results
            
            # Try multiple selectors for the results panel
            results_box = None
            selectors_to_try = [
                (By.CLASS_NAME, "m6QErb"),  # Primary selector
                (By.CSS_SELECTOR, ".m6QErb"),  # CSS version
                (By.CSS_SELECTOR, "div.m6QErb"),  # More specific
                (By.XPATH, "//div[contains(@class, 'm6QErb')]"),  # XPath fallback
                (By.CSS_SELECTOR, "[role='main']"),  # Fallback
                (By.CSS_SELECTOR, "div[aria-label*='Results']"),  # Another fallback
            ]
            
            for selector_type, selector_value in selectors_to_try:
                try:
                    print(f"[SCROLL] Trying selector: {selector_type}={selector_value}")
                    results_box = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    if results_box:
                        print(f"[SCROLL] Found results panel with selector: {selector_value}")
                        break
                except TimeoutException:
                    continue
                except Exception as e:
                    print(f"[SCROLL] Selector {selector_value} failed: {e}")
                    continue
            
            # If still not found, try to find any scrollable container with results
            if not results_box:
                print(f"[SCROLL] Trying to find scrollable container with results...")
                try:
                    # Look for any element containing result items
                    result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                    if result_items:
                        print(f"[SCROLL] Found {len(result_items)} result items, finding parent container...")
                        # Try to find the scrollable parent
                        parent = result_items[0].find_element(By.XPATH, "./ancestor::div[contains(@class, 'm6QErb')]")
                        if parent:
                            results_box = parent
                            print(f"[SCROLL] Found parent container")
                except Exception as e:
                    print(f"[SCROLL] Could not find parent container: {e}")
            
            if not results_box:
                print(f"[SCROLL] Could not find results panel with any method")
                return False
            
            print(f"[SCROLL] Starting to load results...")
            
            last_count = 0
            stable_count = 0
            max_scrolls = 1000  # Increased from 500 - support even more results
            scroll_attempt = 0
            max_stable_count = 15  # Increased from 10 - wait longer to ensure all results load
            
            print(f"[SCROLL] Will attempt up to {max_scrolls} scroll cycles to load all results...")
            
            while scroll_attempt < max_scrolls:
                try:
                    # Strategy 1: Scroll to bottom
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_box)
                    time.sleep(0.5)
                    
                    # Strategy 2: Scroll by large increment
                    driver.execute_script("arguments[0].scrollTop += 2000", results_box)
                    time.sleep(0.5)
                    
                    # Strategy 3: Scroll smoothly with multiple steps
                    for step in range(3):
                        driver.execute_script(f"arguments[0].scrollTop += 500", results_box)
                        time.sleep(0.2)
                    
                    # Strategy 4: Use keyboard navigation (Page Down)
                    try:
                        results_box.send_keys(Keys.PAGE_DOWN)
                        time.sleep(0.3)
                    except Exception:
                        pass
                    
                    # Check current count
                    current = len(driver.find_elements(By.CLASS_NAME, "Nv2PK"))
                    
                    if current > last_count:
                        print(f"[SCROLL] Loaded {current} results (was {last_count})")
                        last_count = current
                        stable_count = 0
                    else:
                        stable_count += 1
                    
                    # If no new results for many consecutive scrolls, we're done
                    if stable_count >= max_stable_count:
                        print(f"[SCROLL] No more results loading after {stable_count} attempts. Final count: {last_count}")
                        break
                    
                    # Extra aggressive scroll every 3 attempts (more frequent for maximum results)
                    if scroll_attempt % 3 == 0 and scroll_attempt > 0:
                        print(f"[SCROLL] Aggressive scroll attempt {scroll_attempt} (current: {current} results)...")
                        for _ in range(15):  # Increased from 10 - more aggressive
                            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_box)
                            time.sleep(0.15)
                            driver.execute_script("arguments[0].scrollTop += 8000", results_box)  # Increased from 5000
                            time.sleep(0.15)
                            # Try scrolling by element
                            try:
                                last_item = driver.find_elements(By.CLASS_NAME, "Nv2PK")[-1] if driver.find_elements(By.CLASS_NAME, "Nv2PK") else None
                                if last_item:
                                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'end'});", last_item)
                                    time.sleep(0.2)
                            except Exception:
                                pass
                    
                    # Every 30 attempts, try even more aggressive scrolling (more frequent)
                    if scroll_attempt % 30 == 0 and scroll_attempt > 0:
                        print(f"[SCROLL] Super aggressive scroll pass {scroll_attempt}...")
                        for _ in range(30):  # Increased from 20
                            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_box)
                            time.sleep(0.08)
                            driver.execute_script("arguments[0].scrollTop += 15000", results_box)  # Increased from 10000
                            time.sleep(0.08)
                    
                    scroll_attempt += 1
                    time.sleep(0.5)  # Small delay between scroll cycles
                    
                except Exception as e:
                    print(f"[SCROLL] Error during scroll attempt {scroll_attempt}: {e}")
                    stable_count += 1
                    if stable_count >= 5:
                        break
                    scroll_attempt += 1
                    time.sleep(1)
            
            # Final aggressive scroll to ensure all are loaded
            try:
                print(f"[SCROLL] Performing final aggressive scroll pass to maximize results...")
                for _ in range(20):  # Increased from 10 - more final scrolls
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_box)
                    time.sleep(0.2)
                    driver.execute_script("arguments[0].scrollTop += 10000", results_box)  # Increased from 5000
                    time.sleep(0.2)
                
                # Try scrolling to each visible item to trigger loading (increased coverage)
                all_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                if all_items:
                    # Scroll to last 100 items instead of 50 for maximum coverage
                    scroll_count = min(100, len(all_items))
                    print(f"[SCROLL] Triggering load by scrolling to last {scroll_count} items...")
                    for item in all_items[-scroll_count:]:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", item)
                            time.sleep(0.08)  # Faster but still allows loading
                        except Exception:
                            continue
                    
                    # Additional pass: scroll to every 10th item to ensure nothing is missed
                    print(f"[SCROLL] Additional pass: scrolling to every 10th item...")
                    for i in range(0, len(all_items), 10):
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", all_items[i])
                            time.sleep(0.05)
                        except Exception:
                            continue
                
                # Scroll back to top to reset position
                driver.execute_script("arguments[0].scrollTop = 0", results_box)
                time.sleep(1)
            except Exception as e:
                print(f"[SCROLL] Warning during final scroll: {e}")
            
            final_count = len(driver.find_elements(By.CLASS_NAME, "Nv2PK"))
            print(f"[SCROLL] Complete. Total results available: {final_count}")
            return True
            
        except TimeoutException:
            print(f"[SCROLL] Timeout: Results panel not found. May be a single place page.")
            return False
        except Exception as e:
            print(f"[SCROLL] Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _extract_url_from_result_item(self, item: WebElement, driver: webdriver.Chrome) -> Optional[str]:
        """
        Extract Google Maps URL from a result item element.
        Tries multiple methods to get the URL.
        """
        try:
            # Method 1: Look for anchor tag with href inside the item
            try:
                anchor = item.find_element(By.TAG_NAME, "a")
                href = anchor.get_attribute("href")
                if href and ("maps.google.com" in href or "google.com/maps" in href):
                    return href
            except Exception:
                pass
            
            # Method 2: Check for data-url or data-href attributes
            try:
                data_url = item.get_attribute("data-url")
                if data_url:
                    return data_url
                data_href = item.get_attribute("data-href")
                if data_href:
                    return data_href
            except Exception:
                pass
            
            # Method 3: Use JavaScript to get the click handler's target URL
            try:
                # Try to find the onclick attribute
                onclick = item.get_attribute("onclick")
                if onclick:
                    # Extract URL from onclick if it contains one
                    url_match = re.search(r"['\"](https?://[^'\"]+)['\"]", onclick)
                    if url_match:
                        return url_match.group(1)
            except Exception:
                pass
            
            # Method 4: Use JavaScript to extract href from clickable elements
            # Try to find the actual link element that would be clicked
            try:
                # Look for elements with role="link" or button
                link_elements = item.find_elements(By.CSS_SELECTOR, "[role='link'], [role='button'], a, button")
                for link_elem in link_elements:
                    try:
                        href = link_elem.get_attribute("href")
                        if href and ("maps.google.com" in href or "google.com/maps" in href):
                            return href
                    except Exception:
                        pass
            except Exception:
                pass
            
            # Method 5: Look for any link element within the item
            try:
                links = item.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and ("maps.google.com" in href or "google.com/maps" in href):
                        return href
            except Exception:
                pass
            
            return None
        except Exception as e:
            print(f"[URL_EXTRACT] Error extracting URL: {e}")
            return None

    def _navigate_back_to_results(self, driver: webdriver.Chrome, query: str, original_search_url: Optional[str] = None) -> bool:
        """
        Navigate back to search results page.
        Uses driver.back() or reconstructs search URL if needed.
        """
        try:
            # Method 1: Use browser back button
            try:
                driver.back()
                time.sleep(3)  # Wait for page to load
                
                # Verify we're back on results page
                result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                if result_items:
                    print(f"[NAV_BACK] Successfully navigated back (found {len(result_items)} results)")
                    return True
            except Exception as e:
                print(f"[NAV_BACK] Browser back failed: {e}")
            
            # Method 2: Reconstruct search URL and navigate
            if original_search_url:
                try:
                    driver.get(original_search_url)
                    time.sleep(5)  # Wait for results to load
                    
                    # Verify results are loaded
                    result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                    if result_items:
                        print(f"[NAV_BACK] Successfully navigated via URL (found {len(result_items)} results)")
                        return True
                except Exception as e:
                    print(f"[NAV_BACK] URL navigation failed: {e}")
            
            # Method 3: Reconstruct search URL from query
            try:
                # Encode query for URL
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://www.google.com/maps/search/{encoded_query}"
                driver.get(search_url)
                time.sleep(5)  # Wait for results to load
                
                # Verify results are loaded
                result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                if result_items:
                    print(f"[NAV_BACK] Successfully navigated via reconstructed URL (found {len(result_items)} results)")
                    return True
            except Exception as e:
                print(f"[NAV_BACK] Reconstructed URL navigation failed: {e}")
            
            return False
        except Exception as e:
            print(f"[NAV_BACK] Error navigating back: {e}")
            return False

    def _extract_info(self, driver: webdriver.Chrome, query: str) -> ScrapeResult:
        def safe_find_text(by: By, value: str, fallback: str = "N/A") -> str:
            try:
                return driver.find_element(by, value).text
            except Exception:
                return fallback

        def safe_find_css(selector: str, fallback: str = "N/A") -> str:
            try:
                return driver.find_element(By.CSS_SELECTOR, selector).text
            except Exception:
                return fallback

        name = safe_find_css('h1[class*="DUwDvf"]')
        category = safe_find_css('button[class*="DkEaL"]')

        address, phone, website, plus_code = "N/A", "N/A", "N/A", "N/A"
        try:
            for el in driver.find_elements(By.CLASS_NAME, "Io6YTe"):
                text = el.text
                if re.search(r"\d{3} \d{3} \d{4}", text):
                    phone = text
                elif "." in text and any(ext in text for ext in [".com", ".net", ".org"]):
                    website = text
                elif "+" in text:
                    plus_code = text
                elif address == "N/A":
                    address = text
        except Exception:
            pass

        current_url = driver.current_url

        # Extract phone numbers using comprehensive phone extractor
        phone_data_list = []
        phone_raw = phone if phone != "N/A" else None
        phone_normalized = None
        phone_validation_status = "N/A"
        phone_confidence_score = 0
        phone_source = "N/A"
        phone_element_selector = None
        phone_screenshot_path = None
        phone_timestamp = None
        
        try:
            from extractors.phone_extractor import PhoneExtractor
            from normalize.phone_normalizer import PhoneNormalizer
            
            phone_extractor = PhoneExtractor(default_region="US")
            phones = phone_extractor.extract_from_driver(
                driver,
                current_url,
                enable_ocr=False,  # Can enable if needed
                enable_website_crawl=True
            )
            
            if phones:
                # Use the highest confidence phone
                best_phone = max(phones, key=lambda p: p.get("confidence_score", 0))
                phone_raw = best_phone.get("raw_phone")
                phone_source = best_phone.get("phone_source", "N/A")
                phone_element_selector = best_phone.get("phone_element_selector")
                phone_screenshot_path = best_phone.get("phone_screenshot_path")
                phone_timestamp = best_phone.get("phone_timestamp")
                
                # Normalize phone
                normalizer = PhoneNormalizer(default_region="US")
                phone_normalized, phone_validation_status = normalizer.normalize(phone_raw)
                
                # Calculate confidence
                phone_confidence_score = normalizer.calculate_confidence(
                    phone_raw,
                    phone_source,
                    phone_validation_status
                )
                
                # Store all phones in phone_data_list for detailed tracking
                phone_data_list = phones
        except ImportError:
            # Phone extraction modules not available, use legacy extraction
            pass
        except Exception:
            # Phone extraction failed, use legacy extraction
            pass

        result: ScrapeResult = {
            "Search Query": query,
            "Platform": self.name,
            "Profile URL": current_url,
            "Handle": "N/A",
            "Display Name": name,
            # Extras retained for platform-specific CSVs
            "Category": category,
            "Address": address,
            "Phone": phone_raw if phone_raw else phone,  # Use extracted phone or legacy
            "Website": website,
            "Plus Code": plus_code,
            # v3.0+ Phone extraction fields
            "phone_raw": phone_raw,
            "phone_normalized": phone_normalized,
            "phone_validation_status": phone_validation_status,
            "phone_confidence_score": phone_confidence_score,
            "phone_source": phone_source,
            "phone_element_selector": phone_element_selector,
            "phone_screenshot_path": phone_screenshot_path,
            "phone_timestamp": phone_timestamp,
            # Store phones list for detailed tracking (will be serialized)
            "phones": phone_data_list,
        }
        return result

    def search(self, query: str, max_results: int) -> Iterable[ScrapeResult]:
        driver = None
        try:
            print(f"[GMAPS] Starting search for: {query}")
            driver = self._setup_driver()
            
            if not self._safe_get(driver, "https://maps.google.com"):
                print(f"[GMAPS] ERROR: Failed to open Google Maps")
                return []

            original_search_url = None
            try:
                print(f"[GMAPS] Entering search query...")
                search_box = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "searchboxinput"))
                )
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.ENTER)
                time.sleep(6)  # Increased wait time for results to load
                print(f"[GMAPS] Search submitted, waiting for results...")
                
                # Store the search URL for navigation back
                original_search_url = driver.current_url
                print(f"[GMAPS] Stored search URL: {original_search_url[:80]}...")
                
                # Verify we're on the results page (not a single place)
                try:
                    # Check if results panel exists
                    results_check = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                    if results_check:
                        print(f"[GMAPS] Found {len(results_check)} result items on page")
                except Exception:
                    pass
            except TimeoutException:
                print(f"[GMAPS] ERROR: Search box not found")
                return []
            except Exception as e:
                print(f"[GMAPS] ERROR: Failed to enter search: {e}")
                return []

            # STEP 1: Scroll down until we reach the end to load ALL results
            print(f"[GMAPS] STEP 1: Scrolling to load all results...")
            has_list = self._scroll_results(driver)
            if not has_list:
                print(f"[GMAPS] Single place page detected, extracting...")
                try:
                    result = self._extract_info(driver, query)
                    yield result
                    print(f"[GMAPS] ✓ Collected: {result.get('Display Name', 'N/A')}")
                except Exception as e:
                    print(f"[GMAPS] ERROR: Failed to extract single place: {e}")
                return

            # STEP 2: Calculate total count and extract URLs from all results
            print(f"[GMAPS] STEP 2: Calculating total count and extracting URLs from results...")
            result_items: List[Any] = driver.find_elements(By.CLASS_NAME, "Nv2PK")
            total = len(result_items)
            print(f"[GMAPS] Found {total} total results after scrolling")
            
            # Apply max_results limit if set (removed artificial 1000 limit for true unlimited)
            if max_results > 0 and max_results < 999999:
                total = min(total, max_results)
                print(f"[GMAPS] Limited to {max_results} results per config")
            else:
                print(f"[GMAPS] Processing all {total} results (unlimited mode - collecting maximum leads)")
            
            if total == 0:
                print(f"[GMAPS] No results found to process")
                return
            
            # Extract URLs from all result items before processing
            print(f"[GMAPS] Extracting URLs from {total} result items...")
            result_urls: List[Optional[str]] = []
            for idx in range(total):
                try:
                    item = result_items[idx]
                    url = self._extract_url_from_result_item(item, driver)
                    if url:
                        result_urls.append(url)
                        if (idx + 1) % 10 == 0:
                            print(f"[GMAPS] Extracted {idx + 1}/{total} URLs...")
                    else:
                        print(f"[GMAPS] Warning: Could not extract URL for item {idx + 1}")
                        result_urls.append(None)
                except Exception as e:
                    print(f"[GMAPS] Error extracting URL for item {idx + 1}: {e}")
                    result_urls.append(None)
            
            # Filter out None URLs and adjust total
            valid_urls = [url for url in result_urls if url is not None]
            print(f"[GMAPS] Successfully extracted {len(valid_urls)}/{total} URLs")
            
            if len(valid_urls) == 0:
                print(f"[GMAPS] ERROR: Could not extract any URLs from results. Falling back to click-based method.")
                # Fall back to original click-based method
                use_url_navigation = False
            else:
                use_url_navigation = True
                total = len(valid_urls)
                print(f"[GMAPS] Will process {total} results using URL-based navigation")
            
            # STEP 3: Navigate to each result one by one in a loop
            if use_url_navigation:
                # URL-based navigation approach
                print(f"[GMAPS] STEP 3: Starting to process {total} results using URL-based navigation...")
                collected = 0
                processed_urls: Set[str] = set()
                
                for idx, url in enumerate(valid_urls):
                    if url is None:
                        continue
                    
                    try:
                        print(f"[GMAPS] [{idx+1}/{total}] Processing result via URL...")
                        
                        # Skip if already processed
                        if url in processed_urls:
                            print(f"[GMAPS] [SKIP] Already processed URL: {url[:60]}...")
                            continue
                        
                        # Navigate directly to the URL
                        try:
                            if not self._safe_get(driver, url):
                                print(f"[GMAPS] [{idx+1}/{total}] ERROR: Failed to navigate to URL")
                                continue
                            time.sleep(3)  # Wait for page to load
                        except Exception as e:
                            print(f"[GMAPS] [{idx+1}/{total}] ERROR: Navigation failed: {e}")
                            continue
                        
                        # Extract info from the loaded page
                        try:
                            result = self._extract_info(driver, query)
                            current_url = result.get('Profile URL', '')
                            
                            # Use the URL we navigated to, not the extracted one (in case of redirects)
                            result['Profile URL'] = url
                            
                            processed_urls.add(url)
                            name = result.get('Display Name', 'N/A')
                            address = result.get('Address', 'N/A')[:50] if result.get('Address') != 'N/A' else 'N/A'
                            print(f"[GMAPS] ✓ [{idx+1}/{total}] Collected: {name}")
                            if address != 'N/A':
                                print(f"           Address: {address}")
                            collected += 1
                            yield result
                            
                        except Exception as e:
                            print(f"[GMAPS] ERROR: Failed to extract info for item {idx+1}: {e}")
                            import traceback
                            traceback.print_exc()
                            continue
                        
                        # Navigate back to search results
                        try:
                            if not self._navigate_back_to_results(driver, query, original_search_url):
                                print(f"[GMAPS] [{idx+1}/{total}] Warning: Failed to navigate back, trying to continue...")
                                # Try to continue anyway - maybe we can still process next URL
                        except Exception as e:
                            print(f"[GMAPS] [{idx+1}/{total}] Warning: Error navigating back: {e}")
                        
                        time.sleep(self.delay_between_results_seconds)
                        
                    except Exception as e:
                        print(f"[GMAPS] ERROR: Exception processing item {idx+1}: {e}")
                        import traceback
                        traceback.print_exc()
                        # Try to navigate back before continuing
                        try:
                            self._navigate_back_to_results(driver, query, original_search_url)
                        except Exception:
                            pass
                        continue
                
                print(f"[GMAPS] Complete. Collected {collected}/{total} results using URL navigation")
            else:
                # Fallback to original click-based method
                print(f"[GMAPS] STEP 3: Starting to process {total} results using click-based method (fallback)...")
                collected = 0
                processed_urls: Set[str] = set()
                
                for idx in range(total):
                    try:
                        print(f"[GMAPS] [{idx+1}/{total}] Processing result...")
                    
                        # Always get fresh elements list before accessing by index
                        result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                        if idx >= len(result_items):
                            print(f"[GMAPS] [{idx+1}/{total}] No more items available (only {len(result_items)} found)")
                            break
                        
                        # Get the item element by index
                        try:
                            item = result_items[idx]
                        except Exception as e:
                            print(f"[GMAPS] [{idx+1}/{total}] ERROR: Could not get item: {e}")
                            continue
                        
                        # Scroll the results panel to show this item (scroll to its position)
                        try:
                            # Find the results container
                            results_box = driver.find_element(By.CSS_SELECTOR, "div.m6QErb")
                            # Scroll the item into view within the results panel
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", item)
                            time.sleep(1.0)  # Wait for scroll to complete
                        except Exception as e:
                            print(f"[GMAPS] [{idx+1}/{total}] Warning: Could not scroll item: {e}")
                            # Refresh element after scroll
                            try:
                                result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                                if idx < len(result_items):
                                    item = result_items[idx]
                                else:
                                    print(f"[GMAPS] [{idx+1}/{total}] Item no longer available after scroll")
                                    continue
                            except Exception:
                                continue
                        
                        # Click on the item to open its details panel
                        clicked = False
                        try:
                            # Try regular click first
                            item.click()
                            clicked = True
                        except (ElementClickInterceptedException, Exception) as e:
                            try:
                                # Use JavaScript click as fallback
                                driver.execute_script("arguments[0].click();", item)
                                clicked = True
                            except Exception as e2:
                                print(f"[GMAPS] [{idx+1}/{total}] Warning: Could not click item: {e2}")
                                # Try finding by XPath as last resort
                                try:
                                    xpath = f"(//div[@class='Nv2PK'])[{idx+1}]"
                                    element = driver.find_element(By.XPATH, xpath)
                                    driver.execute_script("arguments[0].click();", element)
                                    clicked = True
                                except Exception as e3:
                                    print(f"[GMAPS] [{idx+1}/{total}] ERROR: All click methods failed: {e3}")
                                    continue
                        
                        if not clicked:
                            continue
                        
                        # Wait for details panel to load
                        time.sleep(3.0)
                        
                        # Verify details panel opened
                        try:
                            WebDriverWait(driver, 5).until(
                                lambda d: len(d.find_elements(By.CSS_SELECTOR, "[data-value='Directions']")) > 0 or
                                         len(d.find_elements(By.CSS_SELECTOR, "[data-value='Website']")) > 0 or
                                         len(d.find_elements(By.CLASS_NAME, "Io6YTe")) > 0
                            )
                        except TimeoutException:
                            print(f"[GMAPS] [{idx+1}/{total}] Warning: Details panel may not have loaded")
                        
                        # Extract info
                        try:
                            result = self._extract_info(driver, query)
                            current_url = result.get('Profile URL', '')
                            
                            # Skip if we've already processed this URL
                            if current_url in processed_urls:
                                print(f"[GMAPS] [SKIP] Already processed: {result.get('Display Name', 'N/A')[:50]}")
                                # Close details panel
                                try:
                                    body = driver.find_element(By.TAG_NAME, "body")
                                    body.send_keys(Keys.ESCAPE)
                                    time.sleep(2.0)
                                except Exception:
                                    pass
                                continue
                            
                            processed_urls.add(current_url)
                            name = result.get('Display Name', 'N/A')
                            address = result.get('Address', 'N/A')[:50] if result.get('Address') != 'N/A' else 'N/A'
                            print(f"[GMAPS] ✓ [{idx+1}/{total}] Collected: {name}")
                            if address != 'N/A':
                                print(f"           Address: {address}")
                            collected += 1
                            yield result
                            
                            # Close details panel and return to results list
                            # Try multiple methods to close the details panel
                            panel_closed = False
                            
                            # Method 1: Try to find and click the close button (X) on details panel
                            try:
                                close_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Close'], button[aria-label*='close'], button[data-value='Close']")
                                close_button.click()
                                time.sleep(2.0)
                                panel_closed = True
                                print(f"[GMAPS] [{idx+1}/{total}] Closed panel via close button")
                            except Exception:
                                pass
                            
                            # Method 2: Press Escape key
                            if not panel_closed:
                                try:
                                    from selenium.webdriver.common.action_chains import ActionChains
                                    actions = ActionChains(driver)
                                    actions.send_keys(Keys.ESCAPE).perform()
                                    time.sleep(2.0)
                                    panel_closed = True
                                    print(f"[GMAPS] [{idx+1}/{total}] Closed panel via Escape key")
                                except Exception as e:
                                    print(f"[GMAPS] [{idx+1}/{total}] Escape key failed: {e}")
                            
                            # Method 3: Click search box (this should close details and return to list view)
                            if not panel_closed:
                                try:
                                    search_box = WebDriverWait(driver, 5).until(
                                        EC.element_to_be_clickable((By.CLASS_NAME, "searchboxinput"))
                                    )
                                    search_box.click()
                                    time.sleep(2.5)
                                    panel_closed = True
                                    print(f"[GMAPS] [{idx+1}/{total}] Closed panel via search box click")
                                except Exception as e:
                                    print(f"[GMAPS] [{idx+1}/{total}] Search box method failed: {e}")
                            
                            # Method 4: Click on the map background
                            if not panel_closed:
                                try:
                                    # Click on the map canvas area
                                    map_canvas = driver.find_element(By.CSS_SELECTOR, "div[role='main'] > div > div")
                                    ActionChains(driver).move_to_element_with_offset(map_canvas, 100, 100).click().perform()
                                    time.sleep(2.0)
                                    panel_closed = True
                                    print(f"[GMAPS] [{idx+1}/{total}] Closed panel via map click")
                                except Exception:
                                    pass
                            
                            # Wait for results list to be visible again and refresh it
                            if panel_closed:
                                try:
                                    # Wait a bit for panel to fully close
                                    time.sleep(1.5)
                                    
                                    # Try to scroll the results panel to make it visible/refresh it
                                    try:
                                        results_box = driver.find_element(By.CSS_SELECTOR, "div.m6QErb")
                                        # Scroll a bit to trigger refresh
                                        driver.execute_script("arguments[0].scrollTop += 100", results_box)
                                        time.sleep(0.5)
                                        driver.execute_script("arguments[0].scrollTop -= 100", results_box)
                                        time.sleep(0.5)
                                    except Exception:
                                        pass
                                    
                                    # Wait for results to reappear
                                    try:
                                        WebDriverWait(driver, 8).until(
                                            EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK"))
                                        )
                                    except TimeoutException:
                                        # If results don't appear, try clicking on the results panel area
                                        try:
                                            results_box = driver.find_element(By.CSS_SELECTOR, "div.m6QErb")
                                            results_box.click()
                                            time.sleep(1.5)
                                        except Exception:
                                            pass
                                    
                                    # Verify we have results
                                    result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                                    if result_items:
                                        print(f"[GMAPS] [{idx+1}/{total}] Returned to results list (found {len(result_items)} items)")
                                    else:
                                        print(f"[GMAPS] [{idx+1}/{total}] Warning: Results list empty, trying to reload...")
                                        # Try clicking search box again to refresh view
                                        try:
                                            search_box = driver.find_element(By.CLASS_NAME, "searchboxinput")
                                            search_box.click()
                                            time.sleep(2.0)
                                            # Re-scroll to reload results
                                            self._scroll_results(driver)
                                            result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                                            print(f"[GMAPS] [{idx+1}/{total}] Reloaded results, found {len(result_items)} items")
                                        except Exception as e:
                                            print(f"[GMAPS] [{idx+1}/{total}] Could not reload results: {e}")
                                except Exception as e:
                                    print(f"[GMAPS] [{idx+1}/{total}] Warning: Error refreshing results list: {e}")
                                    time.sleep(2)
                            else:
                                print(f"[GMAPS] [{idx+1}/{total}] Warning: Could not close details panel, trying to continue...")
                                # Even if we couldn't close, try to get results
                                try:
                                    result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                                    if result_items:
                                        print(f"[GMAPS] [{idx+1}/{total}] Found {len(result_items)} items without closing panel")
                                    else:
                                        # Try to close via search box
                                        try:
                                            search_box = driver.find_element(By.CLASS_NAME, "searchboxinput")
                                            search_box.click()
                                            time.sleep(2.0)
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                                time.sleep(2)
                            
                        except Exception as e:
                            print(f"[GMAPS] ERROR: Failed to extract info for item {idx+1}: {e}")
                            import traceback
                            traceback.print_exc()
                            # Try to close details panel and return to results
                            try:
                                body = driver.find_element(By.TAG_NAME, "body")
                                body.send_keys(Keys.ESCAPE)
                                time.sleep(2.0)
                            except Exception:
                                pass
                            continue
                        
                        time.sleep(self.delay_between_results_seconds)
                        
                    except Exception as e:
                        print(f"[GMAPS] ERROR: Exception processing item {idx+1}: {e}")
                        import traceback
                        traceback.print_exc()
                        # Try to recover by closing details panel
                        try:
                            body = driver.find_element(By.TAG_NAME, "body")
                            body.send_keys(Keys.ESCAPE)
                            time.sleep(2.0)
                        except Exception:
                            pass
                        continue
                
                print(f"[GMAPS] Complete. Collected {collected}/{total} results")
            
        except Exception as e:
            print(f"[GMAPS] FATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if driver:
                try:
                    driver.quit()
                    print(f"[GMAPS] Browser closed")
                except Exception as e:
                    print(f"[GMAPS] Warning: Error closing browser: {e}")


