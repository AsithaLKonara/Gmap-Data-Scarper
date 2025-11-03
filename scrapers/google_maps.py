from __future__ import annotations

import re
import time
from typing import Iterable, Dict, Any, List, Set

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

    def __init__(self, headless: bool = True, delay_between_results_seconds: int = 2) -> None:
        self.headless = headless
        self.delay_between_results_seconds = delay_between_results_seconds

    def _setup_driver(self) -> webdriver.Chrome:
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _safe_get(self, driver: webdriver.Chrome, url: str, retries: int = 3) -> bool:
        for _ in range(retries):
            try:
                driver.get(url)
                return True
            except Exception:
                time.sleep(2)
        return False

    def _scroll_results(self, driver: webdriver.Chrome) -> bool:
        try:
            results_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "m6QErb"))
            )

            last_count = 0
            stable = 0
            for _ in range(30):
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_box)
                time.sleep(1.0)
                current = len(driver.find_elements(By.CLASS_NAME, "Nv2PK"))
                if current > last_count:
                    last_count = current
                    stable = 0
                else:
                    stable += 1
                if stable >= 3:
                    break
            return True
        except TimeoutException:
            return False
        except Exception:
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

        result: ScrapeResult = {
            "Search Query": query,
            "Platform": self.name,
            "Profile URL": current_url,
            "Handle": "N/A",
            "Display Name": name,
            # Extras retained for platform-specific CSVs
            "Category": category,
            "Address": address,
            "Phone": phone,
            "Website": website,
            "Plus Code": plus_code,
        }
        return result

    def search(self, query: str, max_results: int) -> Iterable[ScrapeResult]:
        driver = self._setup_driver()
        try:
            if not self._safe_get(driver, "https://maps.google.com"):
                return []

            try:
                search_box = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "searchboxinput"))
                )
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.ENTER)
                time.sleep(4)
            except Exception:
                return []

            has_list = self._scroll_results(driver)
            if not has_list:
                yield self._extract_info(driver, query)
                return

            result_items: List[Any] = driver.find_elements(By.CLASS_NAME, "Nv2PK")
            visited: Set[Any] = set()
            total = min(len(result_items), max_results)
            for idx in range(total):
                try:
                    result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                    if idx >= len(result_items):
                        break
                    item = result_items[idx]
                    if item in visited:
                        continue
                    visited.add(item)
                    driver.execute_script("arguments[0].scrollIntoView();", item)
                    time.sleep(1.0)
                    try:
                        item.click()
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", item)
                    time.sleep(2.0)
                    yield self._extract_info(driver, query)
                    time.sleep(self.delay_between_results_seconds)
                except Exception:
                    continue
        finally:
            driver.quit()


