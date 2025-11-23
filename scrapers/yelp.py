"""Yelp business listings scraper."""
from typing import Iterable, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapers.base import BaseScraper, COMMON_FIELDS
import time


class YelpScraper(BaseScraper):
    """Scraper for Yelp business listings."""
    
    name = "yelp"
    
    def __init__(self, headless: bool = True):
        """Initialize Yelp scraper."""
        self.headless = headless
        super().__init__()
    
    def search(self, query: str, max_results: int = 10) -> Iterable[Dict[str, Any]]:
        """
        Search Yelp for businesses matching the query.
        
        Args:
            query: Search query (e.g., "restaurants in Toronto")
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
            # Navigate to Yelp search
            search_url = f"https://www.yelp.com/search?find_desc={query.replace(' ', '+')}"
            driver.get(search_url)
            time.sleep(3)
            
            # Wait for results to load
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
                    
                    # Extract category
                    try:
                        category_elem = result.find_element(By.CSS_SELECTOR, "[data-testid='serp-ia-card-category']")
                        category = category_elem.text.strip()
                    except:
                        category = "N/A"
                    
                    # Extract address
                    try:
                        address_elem = result.find_element(By.CSS_SELECTOR, "[data-testid='serp-ia-card-address']")
                        address = address_elem.text.strip()
                    except:
                        address = "N/A"
                    
                    # Extract phone
                    phone = "N/A"
                    try:
                        phone_elem = result.find_element(By.CSS_SELECTOR, "[data-testid='serp-ia-card-phone']")
                        phone = phone_elem.text.strip()
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
                        "Platform": "yelp",
                        "Profile URL": profile_url,
                        "Handle": None,
                        "Display Name": name,
                        "Bio/About": category,
                        "Website": None,
                        "Email": None,
                        "Phone": phone,
                        "Followers": None,
                        "Location": address,
                        "business_type": category,
                        "industry": "Restaurant" if "restaurant" in category.lower() else "Business",
                        "city": self._extract_city(address),
                        "region": None,
                        "country": "US",  # Yelp is primarily US
                    }
                    count += 1
                except Exception as e:
                    print(f"[YELP] Error extracting result: {e}")
                    continue
                    
        finally:
            driver.quit()
    
    def _extract_city(self, address: str) -> str:
        """Extract city from address string."""
        if not address or address == "N/A":
            return "N/A"
        parts = address.split(",")
        if len(parts) >= 2:
            return parts[-2].strip()
        return "N/A"

