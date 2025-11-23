"""Indeed job listings scraper."""
from typing import Iterable, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapers.base import BaseScraper
import time


class IndeedScraper(BaseScraper):
    """Scraper for Indeed job listings and companies."""
    
    name = "indeed"
    
    def __init__(self, headless: bool = True):
        """Initialize Indeed scraper."""
        self.headless = headless
        super().__init__()
    
    def search(self, query: str, max_results: int = 10) -> Iterable[Dict[str, Any]]:
        """
        Search Indeed for companies/jobs matching the query.
        
        Args:
            query: Search query (e.g., "software companies hiring in Toronto")
            max_results: Maximum number of results to return
            
        Yields:
            Dict with company/job information
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
            # Navigate to Indeed search
            search_url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}"
            driver.get(search_url)
            time.sleep(4)
            
            # Wait for results
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-jk]"))
            )
            
            # Extract results
            results = driver.find_elements(By.CSS_SELECTOR, "div[data-jk]")
            
            count = 0
            for result in results:
                if count >= max_results:
                    break
                
                try:
                    # Extract company name
                    try:
                        company_elem = result.find_element(By.CSS_SELECTOR, "span[data-testid='company-name']")
                        company_name = company_elem.text.strip()
                    except:
                        company_name = "N/A"
                    
                    # Extract job title
                    try:
                        title_elem = result.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
                        job_title = title_elem.text.strip()
                        profile_url = title_elem.get_attribute("href")
                    except:
                        job_title = "N/A"
                        profile_url = "N/A"
                    
                    # Extract location
                    location = "N/A"
                    try:
                        location_elem = result.find_element(By.CSS_SELECTOR, "div[data-testid='text-location']")
                        location = location_elem.text.strip()
                    except:
                        pass
                    
                    # Extract salary (if available)
                    salary = "N/A"
                    try:
                        salary_elem = result.find_element(By.CSS_SELECTOR, "span[data-testid='attribute_snippet_testid']")
                        salary = salary_elem.text.strip()
                    except:
                        pass
                    
                    yield {
                        "Search Query": query,
                        "Platform": "indeed",
                        "Profile URL": profile_url,
                        "Handle": None,
                        "Display Name": company_name,
                        "Bio/About": f"Job: {job_title}",
                        "Website": None,
                        "Email": None,
                        "Phone": None,
                        "Followers": salary,
                        "Location": location,
                        "business_type": "Company",
                        "industry": "Technology",
                        "job_title": job_title,
                        "city": self._extract_city(location),
                        "region": None,
                        "country": self._extract_country(location),
                    }
                    count += 1
                except Exception as e:
                    print(f"[INDEED] Error extracting result: {e}")
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

