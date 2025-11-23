"""Activity scraper for detecting boosted posts and recent activity."""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from scrapers.base import ScrapeResult
from scrapers.social_common import HttpClient, rate_limit_delay


class ActivityScraper:
    """
    Scrapes recent posts and detects boosted/sponsored content.
    
    Analyzes:
    - Post dates
    - Engagement metrics
    - Boosted/sponsored indicators
    - Hashtags
    """
    
    def __init__(self, per_request_delay_seconds: float = 2.0, max_fetch_bytes: int = 1024 * 1024):
        """
        Initialize activity scraper.
        
        Args:
            per_request_delay_seconds: Delay between requests
            max_fetch_bytes: Maximum bytes to fetch per page
        """
        self.per_request_delay_seconds = per_request_delay_seconds
        self.client = HttpClient()
        self.max_fetch_bytes = max_fetch_bytes
    
    def scrape_activity(self, url: str, platform: str) -> Dict[str, str]:
        """
        Scrape activity data from a profile URL.
        
        Args:
            url: Profile URL
            platform: Platform name (facebook, instagram, x, tiktok)
            
        Returns:
            Dictionary with last_post_date, is_boosted, post_engagement
        """
        result = {
            "last_post_date": "N/A",
            "is_boosted": "N/A",
            "post_engagement": "N/A"
        }
        
        try:
            rate_limit_delay(self.per_request_delay_seconds)
            resp = self.client.get(url)
            text = resp.text[:self.max_fetch_bytes]
            soup = BeautifulSoup(text, "lxml")
            
            # Platform-specific extraction
            if platform == "facebook":
                result.update(self._extract_facebook_activity(soup, text))
            elif platform == "instagram":
                result.update(self._extract_instagram_activity(soup, text))
            elif platform == "x" or platform == "twitter":
                result.update(self._extract_twitter_activity(soup, text))
            elif platform == "tiktok":
                result.update(self._extract_tiktok_activity(soup, text))
            
        except Exception as e:
            print(f"[ACTIVITY] Error scraping activity for {url}: {e}")
        
        return result
    
    def _extract_facebook_activity(self, soup: BeautifulSoup, text: str) -> Dict[str, str]:
        """Extract activity from Facebook page."""
        result = {
            "last_post_date": "N/A",
            "is_boosted": "false",
            "post_engagement": "N/A"
        }
        
        # Look for sponsored/boosted indicators
        if re.search(r"sponsored|promoted|boosted", text, re.IGNORECASE):
            result["is_boosted"] = "true"
        
        # Look for post dates (various formats)
        date_patterns = [
            r"(\d{1,2})\s+(hours?|days?|weeks?|months?)\s+ago",
            r"(\d{1,2})h\s+ago",
            r"(\d{1,2})d\s+ago",
            r"(\d{1,2})w\s+ago",
            r"(\d{1,2})m\s+ago",
            r"(\d{4}-\d{2}-\d{2})",  # ISO format
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["last_post_date"] = match.group(0)
                break
        
        # Look for engagement metrics
        engagement_patterns = [
            r"(\d+[KMB]?)\s+(likes?|reactions?)",
            r"(\d+[KMB]?)\s+(comments?)",
            r"(\d+[KMB]?)\s+(shares?)",
        ]
        
        for pattern in engagement_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["post_engagement"] = match.group(0)
                break
        
        return result
    
    def _extract_instagram_activity(self, soup: BeautifulSoup, text: str) -> Dict[str, str]:
        """Extract activity from Instagram profile."""
        result = {
            "last_post_date": "N/A",
            "is_boosted": "false",
            "post_engagement": "N/A"
        }
        
        # Look for sponsored indicators
        if re.search(r"sponsored|promoted|paid partnership", text, re.IGNORECASE):
            result["is_boosted"] = "true"
        
        # Look for post dates
        date_patterns = [
            r"(\d{1,2})\s+(hours?|days?|weeks?)\s+ago",
            r"(\d{1,2})h\s+ago",
            r"(\d{1,2})d\s+ago",
            r"(\d{1,2})w\s+ago",
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["last_post_date"] = match.group(0)
                break
        
        # Look for engagement (likes, comments)
        engagement_match = re.search(r"(\d+[KMB]?)\s+(likes?|comments?)", text, re.IGNORECASE)
        if engagement_match:
            result["post_engagement"] = engagement_match.group(0)
        
        return result
    
    def _extract_twitter_activity(self, soup: BeautifulSoup, text: str) -> Dict[str, str]:
        """Extract activity from X/Twitter profile."""
        result = {
            "last_post_date": "N/A",
            "is_boosted": "false",
            "post_engagement": "N/A"
        }
        
        # Look for promoted indicators
        if re.search(r"promoted|sponsored", text, re.IGNORECASE):
            result["is_boosted"] = "true"
        
        # Look for tweet dates
        date_patterns = [
            r"(\d{1,2})\s+(hours?|days?)\s+ago",
            r"(\d{1,2})h\s+ago",
            r"(\d{1,2})d\s+ago",
            r"(\d{4}-\d{2}-\d{2})",
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["last_post_date"] = match.group(0)
                break
        
        # Look for engagement (retweets, likes)
        engagement_match = re.search(r"(\d+[KMB]?)\s+(retweets?|likes?|replies?)", text, re.IGNORECASE)
        if engagement_match:
            result["post_engagement"] = engagement_match.group(0)
        
        return result
    
    def _extract_tiktok_activity(self, soup: BeautifulSoup, text: str) -> Dict[str, str]:
        """Extract activity from TikTok profile."""
        result = {
            "last_post_date": "N/A",
            "is_boosted": "false",
            "post_engagement": "N/A"
        }
        
        # Look for sponsored indicators
        if re.search(r"sponsored|promoted|paid", text, re.IGNORECASE):
            result["is_boosted"] = "true"
        
        # Look for post dates
        date_patterns = [
            r"(\d{1,2})\s+(hours?|days?)\s+ago",
            r"(\d{1,2})h\s+ago",
            r"(\d{1,2})d\s+ago",
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["last_post_date"] = match.group(0)
                break
        
        # Look for engagement (views, likes)
        engagement_match = re.search(r"(\d+[KMB]?)\s+(views?|likes?)", text, re.IGNORECASE)
        if engagement_match:
            result["post_engagement"] = engagement_match.group(0)
        
        return result
    
    def is_active_within_days(self, last_post_date: str, days: int) -> bool:
        """
        Check if last post is within specified days.
        
        Args:
            last_post_date: Date string (various formats)
            days: Number of days to check
            
        Returns:
            True if active within days, False otherwise
        """
        if not last_post_date or last_post_date == "N/A":
            return False
        
        try:
            # Parse relative dates (e.g., "2 days ago", "5h ago")
            if "ago" in last_post_date.lower():
                # Extract number and unit
                match = re.search(r"(\d+)\s*([hdwmy])", last_post_date.lower())
                if match:
                    num = int(match.group(1))
                    unit = match.group(2)
                    
                    if unit == "h":
                        hours_ago = num
                    elif unit == "d":
                        hours_ago = num * 24
                    elif unit == "w":
                        hours_ago = num * 24 * 7
                    elif unit == "m":
                        hours_ago = num * 24 * 30
                    else:
                        hours_ago = days * 24
                    
                    return hours_ago <= (days * 24)
            
            # Parse absolute dates
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", last_post_date)
            if date_match:
                post_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                days_ago = (datetime.now() - post_date).days
                return days_ago <= days
            
        except Exception:
            pass
        
        return False

