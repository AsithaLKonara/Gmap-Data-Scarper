"""Email extraction service from websites."""
from typing import Optional, List
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class EmailExtractor:
    """Service for extracting email addresses from websites."""
    
    def __init__(self):
        """Initialize email extractor."""
        self.timeout = 10
        self.max_depth = 2  # Maximum depth for crawling
    
    def extract_from_website(
        self,
        website_url: str,
        max_emails: int = 5
    ) -> List[str]:
        """
        Extract email addresses from a website.
        
        Args:
            website_url: Website URL to extract from
            max_emails: Maximum number of emails to return
            
        Returns:
            List of email addresses found
        """
        if not website_url or website_url == "N/A":
            return []
        
        # Normalize URL
        if not website_url.startswith(("http://", "https://")):
            website_url = f"https://{website_url}"
        
        emails = set()
        
        try:
            # Extract from main page
            page_emails = self._extract_from_page(website_url)
            emails.update(page_emails)
            
            # Try common contact pages
            if len(emails) < max_emails:
                contact_pages = [
                    urljoin(website_url, "/contact"),
                    urljoin(website_url, "/contact-us"),
                    urljoin(website_url, "/about"),
                    urljoin(website_url, "/contact.html"),
                ]
                
                for contact_url in contact_pages:
                    if len(emails) >= max_emails:
                        break
                    try:
                        page_emails = self._extract_from_page(contact_url)
                        emails.update(page_emails)
                    except:
                        continue
            
            # Filter valid emails
            valid_emails = [e for e in emails if self._is_valid_email(e)]
            
            return valid_emails[:max_emails]
            
        except Exception as e:
            print(f"[EMAIL_EXTRACTOR] Error extracting from {website_url}: {e}")
            return []
    
    def _extract_from_page(self, url: str) -> List[str]:
        """Extract emails from a single page."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Extract from HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            emails = set()
            
            # Find mailto links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0].strip()
                    emails.add(email)
            
            # Find emails in text (regex)
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            text_emails = re.findall(email_pattern, response.text)
            emails.update(text_emails)
            
            # Find emails in data attributes
            for element in soup.find_all(attrs={"data-email": True}):
                email = element.get('data-email', '').strip()
                if email:
                    emails.add(email)
            
            return list(emails)
            
        except Exception as e:
            print(f"[EMAIL_EXTRACTOR] Error fetching {url}: {e}")
            return []
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email address."""
        if not email or len(email) < 5:
            return False
        
        # Basic email regex
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        if not re.match(pattern, email):
            return False
        
        # Filter out common false positives
        invalid_patterns = [
            'example.com',
            'test.com',
            'domain.com',
            'your-email',
            'email@email',
            'noreply',
            'no-reply',
        ]
        
        email_lower = email.lower()
        if any(pattern in email_lower for pattern in invalid_patterns):
            return False
        
        return True


# Global instance
email_extractor = EmailExtractor()

