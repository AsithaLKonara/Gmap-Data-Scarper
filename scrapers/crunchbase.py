"""Crunchbase company data scraper."""
from typing import Iterable, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapers.base import BaseScraper
import time
import re


class CrunchbaseScraper(BaseScraper):
    """Scraper for Crunchbase company profiles."""
    
    name = "crunchbase"
    
    def __init__(self, headless: bool = True):
        """Initialize Crunchbase scraper."""
        self.headless = headless
        super().__init__()
    
    def search(self, query: str, max_results: int = 10) -> Iterable[Dict[str, Any]]:
        """
        Search Crunchbase for companies matching the query.
        
        Args:
            query: Search query (e.g., "software companies in Toronto")
            max_results: Maximum number of results to return
            
        Yields:
            Dict with company information
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
            # Navigate to Crunchbase search
            search_url = f"https://www.crunchbase.com/discover/organization.companies/{query.replace(' ', '%20')}"
            driver.get(search_url)
            time.sleep(5)
            
            # Wait for results
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "entity-card"))
            )
            
            # Extract results
            results = driver.find_elements(By.CSS_SELECTOR, "entity-card")
            
            count = 0
            for result in results:
                if count >= max_results:
                    break
                
                try:
                    # Extract company name
                    name_elem = result.find_element(By.CSS_SELECTOR, "a[data-test='entity-card-title']")
                    name = name_elem.text.strip()
                    profile_url = name_elem.get_attribute("href")
                    
                    # Extract description
                    try:
                        desc_elem = result.find_element(By.CSS_SELECTOR, "[data-test='entity-card-description']")
                        description = desc_elem.text.strip()
                    except:
                        description = "N/A"
                    
                    # Extract location
                    location = "N/A"
                    try:
                        location_elem = result.find_element(By.CSS_SELECTOR, "[data-test='entity-card-location']")
                        location = location_elem.text.strip()
                    except:
                        pass
                    
                    # Extract funding info
                    funding = "N/A"
                    try:
                        funding_elem = result.find_element(By.CSS_SELECTOR, "[data-test='entity-card-funding']")
                        funding = funding_elem.text.strip()
                    except:
                        pass
                    
                    yield {
                        "Search Query": query,
                        "Platform": "crunchbase",
                        "Profile URL": profile_url,
                        "Handle": None,
                        "Display Name": name,
                        "Bio/About": description,
                        "Website": None,
                        "Email": None,
                        "Phone": None,
                        "Followers": funding,
                        "Location": location,
                        "business_type": "Software Company",
                        "industry": "Technology",
                        "city": self._extract_city(location),
                        "region": None,
                        "country": self._extract_country(location),
                    }
                    count += 1
                except Exception as e:
                    print(f"[CRUNCHBASE] Error extracting result: {e}")
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

