"""Multi-layer phone number extraction from web pages."""
import re
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse


class PhoneExtractor:
    """Extracts phone numbers using multiple strategies."""
    
    # Comprehensive phone regex pattern
    # Fixed regex pattern - removed problematic nested groups
    PHONE_REGEX = re.compile(
        r'(\+?\d{1,3}[\s\-\.\(\)]?)?(\(?\d{1,4}\)?[\s\-\.\)]{0,2})?(\d{1,4}[\s\-\.\)]{0,2}){2,4}(\s*(?:ext|x|#|extension)\s*\d{1,5})?',
        re.IGNORECASE
    )
    
    def __init__(self, default_region: str = "US"):
        self.default_region = default_region
    
    def extract_from_driver(
        self,
        driver: WebDriver,
        url: str,
        enable_ocr: bool = False,
        enable_website_crawl: bool = True,
        debug_port: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract phone numbers from a Selenium WebDriver page.
        
        Args:
            driver: Selenium WebDriver instance
            url: Current page URL
            enable_ocr: Enable OCR extraction
            enable_website_crawl: Enable website crawling
            debug_port: Chrome debug port for coordinate extraction (optional)
        
        Returns list of phone data dictionaries with:
        - raw_phone: Original text
        - normalized_e164: Normalized format (if valid)
        - validation_status: valid/possible/invalid
        - confidence_score: 0-100
        - phone_source: tel_link/visible_text/jsonld/ocr/website
        - phone_element_selector: CSS/XPath selector
        - phone_screenshot_path: Path to screenshot (if OCR)
        - phone_timestamp: When extracted
        - phone_coordinates: Dict with x, y, width, height (normalized 0-1)
        - viewport_info: Dict with viewport dimensions and scroll position
        """
        phones = []
        seen_numbers = set()
        
        # Initialize CDP service if debug port is provided
        cdp_service = None
        if debug_port:
            try:
                from backend.services.chrome_cdp import ChromeCDPService
                cdp_service = ChromeCDPService(driver, debug_port)
            except Exception:
                pass  # CDP service not available
        
        # 1. Extract from tel: links (highest confidence)
        tel_phones = self._extract_tel_links(driver, cdp_service)
        for phone_data in tel_phones:
            raw = phone_data["raw_phone"]
            if raw not in seen_numbers:
                phones.append(phone_data)
                seen_numbers.add(raw)
        
        # 2. Extract from visible text
        text_phones = self._extract_from_text(driver)
        for phone_data in text_phones:
            raw = phone_data["raw_phone"]
            if raw not in seen_numbers:
                phones.append(phone_data)
                seen_numbers.add(raw)
        
        # 3. Extract from JSON-LD structured data
        jsonld_phones = self._extract_from_jsonld(driver)
        for phone_data in jsonld_phones:
            raw = phone_data["raw_phone"]
            if raw not in seen_numbers:
                phones.append(phone_data)
                seen_numbers.add(raw)
        
        # 4. Extract from data attributes
        attr_phones = self._extract_from_attributes(driver, cdp_service)
        for phone_data in attr_phones:
            raw = phone_data["raw_phone"]
            if raw not in seen_numbers:
                phones.append(phone_data)
                seen_numbers.add(raw)
        
        # 5. Website crawling (if website link found)
        if enable_website_crawl:
            website_phones = self._extract_from_website(driver, url)
            for phone_data in website_phones:
                raw = phone_data["raw_phone"]
                if raw not in seen_numbers:
                    phones.append(phone_data)
                    seen_numbers.add(raw)
        
        # 6. OCR extraction (if enabled and no high-confidence phones found)
        if enable_ocr and (not phones or all(p["confidence_score"] < 70 for p in phones)):
            ocr_phones = self._extract_from_ocr(driver)
            for phone_data in ocr_phones:
                raw = phone_data["raw_phone"]
                if raw not in seen_numbers:
                    phones.append(phone_data)
                    seen_numbers.add(raw)
        
        return phones
    
    def _extract_tel_links(self, driver: WebDriver, cdp_service: Optional[Any] = None) -> List[Dict[str, Any]]:
        """Extract phone numbers from tel: links."""
        phones = []
        try:
            tel_links = driver.find_elements(By.XPATH, "//a[starts-with(@href, 'tel:')]")
            for link in tel_links:
                href = link.get_attribute("href")
                if href:
                    raw_phone = href.replace("tel:", "").strip()
                    if raw_phone:
                        selector = self._get_element_selector(link)
                        phone_data = {
                            "raw_phone": raw_phone,
                            "phone_source": "tel_link",
                            "phone_element_selector": selector,
                            "confidence_score": 95,  # High confidence for tel: links
                            "phone_timestamp": datetime.now().isoformat(),
                        }
                        
                        # Add coordinates if CDP service is available
                        if cdp_service and selector:
                            coordinates = self._get_element_coordinates(cdp_service, selector)
                            if coordinates:
                                phone_data["phone_coordinates"] = coordinates
                                phone_data["viewport_info"] = cdp_service.get_viewport_info()
                        
                        phones.append(phone_data)
        except Exception as e:
            pass  # Silently fail
        
        return phones
    
    def _extract_from_text(self, driver: WebDriver) -> List[Dict[str, Any]]:
        """Extract phone numbers from visible text."""
        phones = []
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            
            # First, try standard regex
            matches = self.PHONE_REGEX.findall(body_text)
            
            for match in matches:
                # Join tuple groups if match is a tuple
                if isinstance(match, tuple):
                    raw_phone = ''.join(str(m) for m in match if m).strip()
                else:
                    raw_phone = str(match).strip()
                if len(raw_phone) >= 10:  # Minimum phone length
                    phones.append({
                        "raw_phone": raw_phone,
                        "phone_source": "visible_text",
                        "phone_element_selector": None,  # Can't easily get selector for regex match
                        "confidence_score": 70,  # Medium confidence
                        "phone_timestamp": datetime.now().isoformat(),
                    })
            
            # Second, try obfuscation parsing
            try:
                from extractors.obfuscation_parser import ObfuscationParser
                obfuscation_parser = ObfuscationParser()
                obfuscated_phones = obfuscation_parser.parse(body_text)
                
                for raw_phone in obfuscated_phones:
                    if len(raw_phone) >= 10:
                        # Check if not already found
                        if not any(p["raw_phone"] == raw_phone for p in phones):
                            phones.append({
                                "raw_phone": raw_phone,
                                "phone_source": "visible_text_obfuscated",
                                "phone_element_selector": None,
                                "confidence_score": 60,  # Lower confidence for obfuscated
                                "phone_timestamp": datetime.now().isoformat(),
                            })
            except ImportError:
                pass  # Obfuscation parser not available
            except Exception:
                pass  # Obfuscation parsing failed
                
        except Exception as e:
            pass
        
        return phones
    
    def _extract_from_jsonld(self, driver: WebDriver) -> List[Dict[str, Any]]:
        """Extract phone numbers from JSON-LD structured data."""
        phones = []
        try:
            scripts = driver.find_elements(By.XPATH, "//script[@type='application/ld+json']")
            for script in scripts:
                try:
                    json_data = json.loads(script.get_attribute("innerHTML"))
                    phone = self._extract_phone_from_json(json_data)
                    if phone:
                        phones.append({
                            "raw_phone": phone,
                            "phone_source": "jsonld",
                            "phone_element_selector": None,
                            "confidence_score": 85,  # High confidence for structured data
                            "phone_timestamp": datetime.now().isoformat(),
                        })
                except (json.JSONDecodeError, Exception):
                    continue
        except Exception as e:
            pass
        
        return phones
    
    def _extract_from_attributes(self, driver: WebDriver, cdp_service: Optional[Any] = None) -> List[Dict[str, Any]]:
        """Extract phone numbers from data attributes."""
        phones = []
        try:
            # Look for data-phone, data-tel attributes
            elements = driver.find_elements(By.XPATH, "//*[@data-phone or @data-tel]")
            for elem in elements:
                phone = elem.get_attribute("data-phone") or elem.get_attribute("data-tel")
                if phone:
                    selector = self._get_element_selector(elem)
                    phone_data = {
                        "raw_phone": phone.strip(),
                        "phone_source": "visible_text",  # Similar to visible text
                        "phone_element_selector": selector,
                        "confidence_score": 80,
                        "phone_timestamp": datetime.now().isoformat(),
                    }
                    
                    # Add coordinates if CDP service is available
                    if cdp_service and selector:
                        coordinates = self._get_element_coordinates(cdp_service, selector)
                        if coordinates:
                            phone_data["phone_coordinates"] = coordinates
                            phone_data["viewport_info"] = cdp_service.get_viewport_info()
                    
                    phones.append(phone_data)
        except Exception as e:
            pass
        
        return phones
    
    def _extract_from_website(self, driver: WebDriver, current_url: str) -> List[Dict[str, Any]]:
        """Extract phone numbers from linked website."""
        phones = []
        try:
            # Find website links
            website_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'http')]")
            website_url = None
            
            for link in website_links:
                href = link.get_attribute("href")
                if href and any(domain in href for domain in [".com", ".net", ".org", ".io"]):
                    # Avoid social media links
                    if not any(social in href for social in ["facebook.com", "instagram.com", "linkedin.com", "twitter.com", "x.com"]):
                        website_url = href
                        break
            
            if website_url:
                # Try to fetch contact pages
                contact_urls = [
                    urljoin(website_url, "/contact"),
                    urljoin(website_url, "/contact-us"),
                    urljoin(website_url, "/about"),
                ]
                
                for contact_url in contact_urls:
                    try:
                        response = requests.get(contact_url, timeout=5, headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        })
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, "html.parser")
                            
                            # Extract tel: links
                            for link in soup.find_all("a", href=re.compile(r"^tel:")):
                                phone = link["href"].replace("tel:", "").strip()
                                if phone:
                                    phones.append({
                                        "raw_phone": phone,
                                        "phone_source": "website",
                                        "phone_element_selector": None,
                                        "confidence_score": 75,
                                        "phone_timestamp": datetime.now().isoformat(),
                                    })
                            
                            # Extract from text
                            text = soup.get_text()
                            matches = self.PHONE_REGEX.findall(text)
                            for match in matches:
                                # Join tuple groups if match is a tuple
                                if isinstance(match, tuple):
                                    phone = ''.join(str(m) for m in match if m).strip()
                                else:
                                    phone = str(match).strip()
                                if len(phone) >= 10:
                                    phones.append({
                                        "raw_phone": phone,
                                        "phone_source": "website",
                                        "phone_element_selector": None,
                                        "confidence_score": 65,
                                        "phone_timestamp": datetime.now().isoformat(),
                                    })
                            
                            # Extract from JSON-LD
                            for script in soup.find_all("script", type="application/ld+json"):
                                try:
                                    json_data = json.loads(script.string)
                                    phone = self._extract_phone_from_json(json_data)
                                    if phone:
                                        phones.append({
                                            "raw_phone": phone,
                                            "phone_source": "website",
                                            "phone_element_selector": None,
                                            "confidence_score": 80,
                                            "phone_timestamp": datetime.now().isoformat(),
                                        })
                                except:
                                    continue
                            
                            break  # Found contact page, stop trying others
                    except Exception:
                        continue
        except Exception as e:
            pass
        
        return phones
    
    def _extract_from_ocr(self, driver: WebDriver) -> List[Dict[str, Any]]:
        """Extract phone numbers using OCR on page screenshot."""
        phones = []
        try:
            from ocr.image_phone_ocr import ImagePhoneOCR
            
            ocr_extractor = ImagePhoneOCR()
            screenshot_path = ocr_extractor.capture_screenshot(driver)
            
            if screenshot_path:
                ocr_text = ocr_extractor.extract_text(screenshot_path)
                matches = self.PHONE_REGEX.findall(ocr_text)
                
                for match in matches:
                    # Join tuple groups if match is a tuple
                    if isinstance(match, tuple):
                        phone = ''.join(str(m) for m in match if m).strip()
                    else:
                        phone = str(match).strip()
                    if len(phone) >= 10:
                        phones.append({
                            "raw_phone": phone,
                            "phone_source": "ocr",
                            "phone_element_selector": None,
                            "phone_screenshot_path": screenshot_path,
                            "confidence_score": 50,  # Lower confidence for OCR
                            "phone_timestamp": datetime.now().isoformat(),
                        })
        except ImportError:
            # OCR not available
            pass
        except Exception as e:
            pass
        
        return phones
    
    def _extract_phone_from_json(self, json_data: Any) -> Optional[str]:
        """Recursively extract phone from JSON structure."""
        if isinstance(json_data, dict):
            # Check for telephone field
            if "telephone" in json_data:
                return str(json_data["telephone"])
            if "phone" in json_data:
                return str(json_data["phone"])
            
            # Recursively search
            for value in json_data.values():
                phone = self._extract_phone_from_json(value)
                if phone:
                    return phone
        elif isinstance(json_data, list):
            for item in json_data:
                phone = self._extract_phone_from_json(item)
                if phone:
                    return phone
        
        return None
    
    def _get_element_selector(self, element) -> Optional[str]:
        """Generate CSS selector for an element."""
        try:
            # Try to get unique attributes
            elem_id = element.get_attribute("id")
            if elem_id:
                return f"#{elem_id}"
            
            elem_class = element.get_attribute("class")
            if elem_class:
                classes = ".".join(elem_class.split())
                tag = element.tag_name
                return f"{tag}.{classes}"
            
            # Fallback to tag name
            return element.tag_name
        except:
            return None
    
    def _get_element_coordinates(self, cdp_service: Any, selector: str) -> Optional[Dict[str, float]]:
        """Get element coordinates using CDP service."""
        try:
            return cdp_service.get_element_bounding_box(selector)
        except Exception:
            return None

