"""TripAdvisor business listings scraper."""
from typing import Iterable, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapers.base import BaseScraper
import time


class TripAdvisorScraper(BaseScraper):
    """Scraper for TripAdvisor business listings."""
    
    name = "tripadvisor"
    
    def __init__(self, headless: bool = True):
        """Initialize TripAdvisor scraper."""
        self.headless = headless
        super().__init__()
    
    def search(self, query: str, max_results: int = 10) -> Iterable[Dict[str, Any]]:
        """
        Search TripAdvisor for businesses matching the query.
        
        Args:
            query: Search query (e.g., "hotels in Paris")
            max_results: Maximum number of results to return
            
        Yields:
            Dict with business information
        """
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            # Navigate to TripAdvisor search
            search_url = f"https://www.tripadvisor.com/Search?q={query.replace(' ', '+')}"
            driver.get(search_url)
            time.sleep(4)
            
            # Wait for results
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='serp-ia-card']"))
            )
            
            # Extract results
            results = driver.find_elements(By.CSS_SELECTOR, "[data-testid='serp-ia-card']")
            
            count = 0
            for result in results:
                if count >= max_results:
                    break
                
                try:
                    # Extract business name
                    name_elem = result.find_element(By.CSS_SELECTOR, "a[data-testid='serp-ia-card-title']")
                    name = name_elem.text.strip()
                    profile_url = name_elem.get_attribute("href")
                    
                    # Extract category/type
                    try:
                        category_elem = result.find_element(By.CSS_SELECTOR, "[data-testid='serp-ia-card-category']")
                        category = category_elem.text.strip()
                    except:
                        category = "N/A"
                    
                    # Extract location
                    location = "N/A"
                    try:
                        location_elem = result.find_element(By.CSS_SELECTOR, "[data-testid='serp-ia-card-location']")
                        location = location_elem.text.strip()
                    except:
                        pass
                    
                    # Extract rating
                    rating = "N/A"
                    try:
                        rating_elem = result.find_element(By.CSS_SELECTOR, "[data-testid='serp-ia-card-rating']")
                        rating = rating_elem.get_attribute("aria-label") or "N/A"
                    except:
                        pass
                    
                    yield {
                        "Search Query": query,
                        "Platform": "tripadvisor",
                        "Profile URL": profile_url,
                        "Handle": None,
                        "Display Name": name,
                        "Bio/About": category,
                        "Website": None,
                        "Email": None,
                        "Phone": None,
                        "Followers": rating,
                        "Location": location,
                        "business_type": category,
                        "industry": "Tourism",
                        "city": self._extract_city(location),
                        "region": None,
                        "country": self._extract_country(location),
                    }
                    count += 1
                except Exception as e:
                    print(f"[TRIPADVISOR] Error extracting result: {e}")
                    continue
                    
        finally:
            driver.quit()
    
    def _extract_city(self, location: str) -> str:
        """Extract city from location string."""
        if not location or location == "N/A":
            return "N/A"
        parts = location.split(",")
        if len(parts) > 0:
            return parts[0].strip()
        return "N/A"
    
    def _extract_country(self, location: str) -> str:
        """Extract country from location string."""
        if not location or location == "N/A":
            return "N/A"
        parts = location.split(",")
        if len(parts) >= 2:
            return parts[-1].strip()
        return "N/A"

