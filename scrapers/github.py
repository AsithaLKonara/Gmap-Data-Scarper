"""GitHub developer profiles scraper."""
from typing import Iterable, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapers.base import BaseScraper
import time


class GitHubScraper(BaseScraper):
    """Scraper for GitHub developer profiles."""
    
    name = "github"
    
    def __init__(self, headless: bool = True):
        """Initialize GitHub scraper."""
        self.headless = headless
        super().__init__()
    
    def search(self, query: str, max_results: int = 10) -> Iterable[Dict[str, Any]]:
        """
        Search GitHub for developers matching the query.
        
        Args:
            query: Search query (e.g., "Python developers in Toronto")
            max_results: Maximum number of results to return
            
        Yields:
            Dict with developer information
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
            # Navigate to GitHub user search
            search_url = f"https://github.com/search?q={query.replace(' ', '+')}&type=users"
            driver.get(search_url)
            time.sleep(4)
            
            # Wait for results
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='results']"))
            )
            
            # Extract results
            results = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='results'] > div")
            
            count = 0
            for result in results:
                if count >= max_results:
                    break
                
                try:
                    # Extract username
                    try:
                        username_elem = result.find_element(By.CSS_SELECTOR, "a[data-testid='user-name']")
                        username = username_elem.text.strip()
                        profile_url = username_elem.get_attribute("href")
                    except:
                        username = "N/A"
                        profile_url = "N/A"
                    
                    # Extract bio
                    bio = "N/A"
                    try:
                        bio_elem = result.find_element(By.CSS_SELECTOR, "p[data-testid='user-bio']")
                        bio = bio_elem.text.strip()
                    except:
                        pass
                    
                    # Extract location
                    location = "N/A"
                    try:
                        location_elem = result.find_element(By.CSS_SELECTOR, "span[data-testid='user-location']")
                        location = location_elem.text.strip()
                    except:
                        pass
                    
                    yield {
                        "Search Query": query,
                        "Platform": "github",
                        "Profile URL": profile_url,
                        "Handle": username,
                        "Display Name": username,
                        "Bio/About": bio,
                        "Website": None,
                        "Email": None,
                        "Phone": None,
                        "Followers": None,
                        "Location": location,
                        "business_type": "Developer",
                        "industry": "Technology",
                        "city": self._extract_city(location),
                        "region": None,
                        "country": self._extract_country(location),
                    }
                    count += 1
                except Exception as e:
                    print(f"[GITHUB] Error extracting result: {e}")
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

