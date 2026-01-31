from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from models import Users, SocialMediaLeads, LeadCollections, LeadSources
from database import get_db
from auth import get_current_user
import logging
import secrets
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
from bs4 import BeautifulSoup
import requests

router = APIRouter(prefix="/api/social-scraper", tags=["social-scraper"])
logger = logging.getLogger("social-scraper")

# Pydantic models
class SocialScrapingRequest(BaseModel):
    platform: str = Field(..., description="Social media platform to scrape (facebook, instagram, twitter, linkedin, tiktok)", example="facebook")
    keywords: List[str] = Field(..., description="List of keywords or hashtags to search.", example=["marketing", "startup"])
    location: Optional[str] = Field(None, description="Location filter for the search.", example="New York")
    max_results: int = Field(100, description="Maximum number of results to fetch.", example=100)
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters for the search.")
    include_engagement: bool = Field(True, description="Whether to include engagement metrics in the results.")
    include_contact_info: bool = Field(True, description="Whether to include contact information in the results.")

class SocialLeadResponse(BaseModel):
    id: int = Field(..., description="Unique identifier for the social lead.")
    platform: str = Field(..., description="Social media platform.", example="facebook")
    platform_id: str = Field(..., description="Platform-specific ID for the lead.")
    username: Optional[str] = Field(None, description="Username or handle.")
    display_name: Optional[str] = Field(None, description="Display name or full name.")
    email: Optional[str] = Field(None, description="Email address.")
    phone: Optional[str] = Field(None, description="Phone number.")
    bio: Optional[str] = Field(None, description="Profile bio or description.")
    followers_count: Optional[int] = Field(None, description="Number of followers.")
    following_count: Optional[int] = Field(None, description="Number of accounts followed.")
    posts_count: Optional[int] = Field(None, description="Number of posts.")
    location: Optional[str] = Field(None, description="Location of the lead.")
    website: Optional[str] = Field(None, description="Website URL.")
    profile_url: Optional[str] = Field(None, description="Profile URL.")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL.")
    verified: bool = Field(..., description="Whether the profile is verified.")
    business_category: Optional[str] = Field(None, description="Business category or industry.")
    engagement_score: Optional[float] = Field(None, description="Calculated engagement score.")
    status: str = Field(..., description="Status of the lead (new, contacted, etc.)")
    tags: List[str] = Field(..., description="Tags associated with the lead.")
    notes: Optional[str] = Field(None, description="Additional notes.")
    created_at: datetime = Field(..., description="Timestamp when the lead was created.")
    updated_at: datetime = Field(..., description="Timestamp when the lead was last updated.")

# Social Media Scraping Engine
class SocialMediaScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def setup_driver(self, headless: bool = True):
        """Setup Chrome driver for scraping"""
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        driver = webdriver.Chrome(options=options)
        return driver
    
    async def scrape_facebook(self, keywords: List[str], location: Optional[str] = None, max_results: int = 100) -> List[Dict]:
        """Scrape Facebook pages and groups for leads"""
        leads = []
        driver = self.setup_driver()
        
        try:
            for keyword in keywords:
                search_query = f"{keyword}"
                if location:
                    search_query += f" {location}"
                
                # Search Facebook pages
                driver.get(f"https://www.facebook.com/search/pages/?q={search_query}")
                time.sleep(3)
                
                # Extract page information
                pages = driver.find_elements(By.CSS_SELECTOR, '[data-testid="page-item"]')
                
                for i, page in enumerate(pages[:max_results//len(keywords)]):
                    try:
                        page_data = self.extract_facebook_page_data(page, driver)
                        if page_data:
                            leads.append(page_data)
                    except Exception as e:
                        logger.error(f"Error extracting Facebook page data: {e}")
                        continue
                
                # Search Facebook groups
                driver.get(f"https://www.facebook.com/search/groups/?q={search_query}")
                time.sleep(3)
                
                groups = driver.find_elements(By.CSS_SELECTOR, '[data-testid="group-item"]')
                
                for i, group in enumerate(groups[:max_results//len(keywords)]):
                    try:
                        group_data = self.extract_facebook_group_data(group, driver)
                        if group_data:
                            leads.append(group_data)
                    except Exception as e:
                        logger.error(f"Error extracting Facebook group data: {e}")
                        continue
                        
        finally:
            driver.quit()
        
        return leads
    
    def extract_facebook_page_data(self, page_element, driver) -> Optional[Dict]:
        """Extract data from Facebook page element"""
        try:
            # Click on page to get more details
            page_element.click()
            time.sleep(2)
            
            # Extract basic information
            name = page_element.find_element(By.CSS_SELECTOR, 'h2').text
            category = page_element.find_element(By.CSS_SELECTOR, '[data-testid="page-category"]').text
            
            # Try to extract contact information
            contact_info = {}
            try:
                about_section = driver.find_element(By.CSS_SELECTOR, '[data-testid="page-about"]')
                contact_info = self.extract_contact_info(about_section)
            except:
                pass
            
            return {
                "platform": "facebook",
                "platform_id": f"fb_{secrets.token_hex(8)}",
                "display_name": name,
                "business_category": category,
                "location": contact_info.get("location"),
                "website": contact_info.get("website"),
                "phone": contact_info.get("phone"),
                "email": contact_info.get("email"),
                "followers_count": self.extract_follower_count(page_element),
                "verified": self.is_verified(page_element),
                "profile_url": driver.current_url
            }
        except Exception as e:
            logger.error(f"Error extracting Facebook page data: {e}")
            return None
    
    async def scrape_instagram(self, hashtags: List[str], location: Optional[str] = None, max_results: int = 100) -> List[Dict]:
        """Scrape Instagram profiles and posts for leads"""
        leads = []
        driver = self.setup_driver()
        
        try:
            for hashtag in hashtags:
                # Search Instagram hashtags
                driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
                time.sleep(3)
                
                # Extract profile information from posts
                posts = driver.find_elements(By.CSS_SELECTOR, 'article img')
                
                for i, post in enumerate(posts[:max_results//len(hashtags)]):
                    try:
                        # Click on post to get profile info
                        post.click()
                        time.sleep(2)
                        
                        profile_data = self.extract_instagram_profile_data(driver)
                        if profile_data:
                            leads.append(profile_data)
                            
                        # Close post modal
                        close_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Close"]')
                        close_button.click()
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"Error extracting Instagram profile data: {e}")
                        continue
                        
        finally:
            driver.quit()
        
        return leads
    
    def extract_instagram_profile_data(self, driver) -> Optional[Dict]:
        """Extract data from Instagram profile"""
        try:
            # Get profile information from post modal
            profile_link = driver.find_element(By.CSS_SELECTOR, 'header a')
            profile_name = profile_link.text
            profile_url = profile_link.get_attribute('href')
            
            # Navigate to profile page
            driver.get(profile_url)
            time.sleep(3)
            
            # Extract profile information
            bio = driver.find_element(By.CSS_SELECTOR, 'h1 + div').text
            followers = self.extract_follower_count(driver.find_element(By.CSS_SELECTOR, '[data-testid="followers-count"]'))
            posts = self.extract_posts_count(driver.find_element(By.CSS_SELECTOR, '[data-testid="posts-count"]'))
            
            # Extract contact information from bio
            contact_info = self.extract_contact_from_bio(bio)
            
            return {
                "platform": "instagram",
                "platform_id": f"ig_{secrets.token_hex(8)}",
                "username": profile_name,
                "display_name": profile_name,
                "bio": bio,
                "followers_count": followers,
                "posts_count": posts,
                "website": contact_info.get("website"),
                "email": contact_info.get("email"),
                "phone": contact_info.get("phone"),
                "location": contact_info.get("location"),
                "verified": self.is_verified(driver.find_element(By.CSS_SELECTOR, 'header')),
                "profile_url": profile_url
            }
        except Exception as e:
            logger.error(f"Error extracting Instagram profile data: {e}")
            return None
    
    async def scrape_twitter(self, keywords: List[str], location: Optional[str] = None, max_results: int = 100) -> List[Dict]:
        """Scrape Twitter profiles for leads"""
        leads = []
        driver = self.setup_driver()
        
        try:
            for keyword in keywords:
                search_query = f"{keyword}"
                if location:
                    search_query += f" {location}"
                
                # Search Twitter users
                driver.get(f"https://twitter.com/search?q={search_query}&src=typed_query&f=user")
                time.sleep(3)
                
                # Extract user information
                users = driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserCell"]')
                
                for i, user in enumerate(users[:max_results//len(keywords)]):
                    try:
                        user_data = self.extract_twitter_user_data(user, driver)
                        if user_data:
                            leads.append(user_data)
                    except Exception as e:
                        logger.error(f"Error extracting Twitter user data: {e}")
                        continue
                        
        finally:
            driver.quit()
        
        return leads
    
    def extract_twitter_user_data(self, user_element, driver) -> Optional[Dict]:
        """Extract data from Twitter user element"""
        try:
            # Click on user to get profile details
            user_element.click()
            time.sleep(2)
            
            # Extract profile information
            name = user_element.find_element(By.CSS_SELECTOR, '[data-testid="UserName"]').text
            username = user_element.find_element(By.CSS_SELECTOR, '[data-testid="UserName"] + span').text
            bio = user_element.find_element(By.CSS_SELECTOR, '[data-testid="UserDescription"]').text
            location = user_element.find_element(By.CSS_SELECTOR, '[data-testid="UserLocation"]').text
            website = user_element.find_element(By.CSS_SELECTOR, '[data-testid="UserUrl"]').get_attribute('href')
            
            # Extract follower counts
            followers = self.extract_follower_count(user_element.find_element(By.CSS_SELECTOR, '[data-testid="UserFollowersCount"]'))
            
            return {
                "platform": "twitter",
                "platform_id": f"tw_{secrets.token_hex(8)}",
                "username": username,
                "display_name": name,
                "bio": bio,
                "location": location,
                "website": website,
                "followers_count": followers,
                "verified": self.is_verified(user_element),
                "profile_url": f"https://twitter.com/{username}"
            }
        except Exception as e:
            logger.error(f"Error extracting Twitter user data: {e}")
            return None
    
    async def scrape_linkedin(self, keywords: List[str], location: Optional[str] = None, max_results: int = 100) -> List[Dict]:
        """Scrape LinkedIn profiles and companies for leads"""
        leads = []
        driver = self.setup_driver()
        
        try:
            for keyword in keywords:
                search_query = f"{keyword}"
                if location:
                    search_query += f" {location}"
                
                # Search LinkedIn companies
                driver.get(f"https://www.linkedin.com/search/results/companies/?keywords={search_query}")
                time.sleep(3)
                
                # Extract company information
                companies = driver.find_elements(By.CSS_SELECTOR, '.search-result__info')
                
                for i, company in enumerate(companies[:max_results//len(keywords)]):
                    try:
                        company_data = self.extract_linkedin_company_data(company, driver)
                        if company_data:
                            leads.append(company_data)
                    except Exception as e:
                        logger.error(f"Error extracting LinkedIn company data: {e}")
                        continue
                        
        finally:
            driver.quit()
        
        return leads
    
    def extract_linkedin_company_data(self, company_element, driver) -> Optional[Dict]:
        """Extract data from LinkedIn company element"""
        try:
            # Click on company to get details
            company_element.click()
            time.sleep(2)
            
            # Extract company information
            name = company_element.find_element(By.CSS_SELECTOR, '.search-result__title').text
            industry = company_element.find_element(By.CSS_SELECTOR, '.search-result__subtitle').text
            location = company_element.find_element(By.CSS_SELECTOR, '.search-result__location').text
            size = company_element.find_element(By.CSS_SELECTOR, '.search-result__size').text
            
            # Extract contact information
            contact_info = self.extract_linkedin_contact_info(driver)
            
            return {
                "platform": "linkedin",
                "platform_id": f"li_{secrets.token_hex(8)}",
                "display_name": name,
                "business_category": industry,
                "location": location,
                "website": contact_info.get("website"),
                "phone": contact_info.get("phone"),
                "email": contact_info.get("email"),
                "followers_count": self.extract_follower_count(company_element),
                "verified": self.is_verified(company_element),
                "profile_url": driver.current_url
            }
        except Exception as e:
            logger.error(f"Error extracting LinkedIn company data: {e}")
            return None
    
    async def scrape_tiktok(self, hashtags: List[str], location: Optional[str] = None, max_results: int = 100) -> List[Dict]:
        """Scrape TikTok profiles for leads"""
        leads = []
        driver = self.setup_driver()
        
        try:
            for hashtag in hashtags:
                # Search TikTok hashtags
                driver.get(f"https://www.tiktok.com/tag/{hashtag}")
                time.sleep(3)
                
                # Extract profile information from videos
                videos = driver.find_elements(By.CSS_SELECTOR, '[data-e2e="user-card"]')
                
                for i, video in enumerate(videos[:max_results//len(hashtags)]):
                    try:
                        profile_data = self.extract_tiktok_profile_data(video, driver)
                        if profile_data:
                            leads.append(profile_data)
                    except Exception as e:
                        logger.error(f"Error extracting TikTok profile data: {e}")
                        continue
                        
        finally:
            driver.quit()
        
        return leads
    
    def extract_tiktok_profile_data(self, video_element, driver) -> Optional[Dict]:
        """Extract data from TikTok profile"""
        try:
            # Click on video to get profile info
            video_element.click()
            time.sleep(2)
            
            # Extract profile information
            username = video_element.find_element(By.CSS_SELECTOR, '[data-e2e="user-card-user-unique-id"]').text
            display_name = video_element.find_element(By.CSS_SELECTOR, '[data-e2e="user-card-user-nickname"]').text
            bio = video_element.find_element(By.CSS_SELECTOR, '[data-e2e="user-card-user-signature"]').text
            
            # Extract follower counts
            followers = self.extract_follower_count(video_element.find_element(By.CSS_SELECTOR, '[data-e2e="user-card-followers-count"]'))
            
            return {
                "platform": "tiktok",
                "platform_id": f"tt_{secrets.token_hex(8)}",
                "username": username,
                "display_name": display_name,
                "bio": bio,
                "followers_count": followers,
                "verified": self.is_verified(video_element),
                "profile_url": f"https://www.tiktok.com/@{username}"
            }
        except Exception as e:
            logger.error(f"Error extracting TikTok profile data: {e}")
            return None
    
    # Helper methods
    def extract_follower_count(self, element) -> Optional[int]:
        """Extract follower count from element"""
        try:
            text = element.text
            # Extract number from text like "1.2K followers" or "1,234 followers"
            match = re.search(r'([\d,]+\.?\d*[KMB]?)', text)
            if match:
                count_str = match.group(1)
                if 'K' in count_str:
                    return int(float(count_str.replace('K', '')) * 1000)
                elif 'M' in count_str:
                    return int(float(count_str.replace('M', '')) * 1000000)
                elif 'B' in count_str:
                    return int(float(count_str.replace('B', '')) * 1000000000)
                else:
                    return int(count_str.replace(',', ''))
        except:
            pass
        return None
    
    def extract_posts_count(self, element) -> Optional[int]:
        """Extract posts count from element"""
        try:
            text = element.text
            match = re.search(r'([\d,]+)', text)
            if match:
                return int(match.group(1).replace(',', ''))
        except:
            pass
        return None
    
    def is_verified(self, element) -> bool:
        """Check if profile is verified"""
        try:
            verified_icon = element.find_element(By.CSS_SELECTOR, '[data-testid="verified-badge"]')
            return True
        except:
            return False
    
    def extract_contact_info(self, element) -> Dict[str, str]:
        """Extract contact information from element"""
        contact_info = {}
        try:
            # Look for common contact patterns
            text = element.text.lower()
            
            # Extract email
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            if email_match:
                contact_info["email"] = email_match.group(0)
            
            # Extract phone
            phone_match = re.search(r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', text)
            if phone_match:
                contact_info["phone"] = phone_match.group(0)
            
            # Extract website
            website_match = re.search(r'https?://[^\s]+', text)
            if website_match:
                contact_info["website"] = website_match.group(0)
            
            # Extract location
            location_patterns = [
                r'location[:\s]+([^,\n]+)',
                r'address[:\s]+([^,\n]+)',
                r'based in ([^,\n]+)'
            ]
            for pattern in location_patterns:
                location_match = re.search(pattern, text)
                if location_match:
                    contact_info["location"] = location_match.group(1).strip()
                    break
                    
        except Exception as e:
            logger.error(f"Error extracting contact info: {e}")
        
        return contact_info
    
    def extract_contact_from_bio(self, bio: str) -> Dict[str, str]:
        """Extract contact information from bio text"""
        contact_info = {}
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', bio)
        if email_match:
            contact_info["email"] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', bio)
        if phone_match:
            contact_info["phone"] = phone_match.group(0)
        
        # Extract website
        website_match = re.search(r'https?://[^\s]+', bio)
        if website_match:
            contact_info["website"] = website_match.group(0)
        
        # Extract location
        location_patterns = [
            r'📍\s*([^,\n]+)',
            r'location[:\s]+([^,\n]+)',
            r'based in ([^,\n]+)'
        ]
        for pattern in location_patterns:
            location_match = re.search(pattern, bio)
            if location_match:
                contact_info["location"] = location_match.group(1).strip()
                break
        
        return contact_info
    
    def extract_linkedin_contact_info(self, driver) -> Dict[str, str]:
        """Extract contact information from LinkedIn company page"""
        contact_info = {}
        try:
            # Look for contact information in company page
            contact_section = driver.find_element(By.CSS_SELECTOR, '[data-testid="company-contact-info"]')
            contact_text = contact_section.text
            
            # Extract website
            website_match = re.search(r'https?://[^\s]+', contact_text)
            if website_match:
                contact_info["website"] = website_match.group(0)
            
            # Extract phone
            phone_match = re.search(r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', contact_text)
            if phone_match:
                contact_info["phone"] = phone_match.group(0)
            
            # Extract email
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', contact_text)
            if email_match:
                contact_info["email"] = email_match.group(0)
                
        except Exception as e:
            logger.error(f"Error extracting LinkedIn contact info: {e}")
        
        return contact_info
    
    def calculate_engagement_score(self, lead_data: Dict) -> float:
        """Calculate engagement score for social media lead"""
        score = 0.0
        factors = 0
        
        # Follower count scoring
        if lead_data.get("followers_count"):
            followers = lead_data["followers_count"]
            if followers > 1000000:  # 1M+ followers
                score += 10.0
            elif followers > 100000:  # 100K+ followers
                score += 8.0
            elif followers > 10000:  # 10K+ followers
                score += 6.0
            elif followers > 1000:  # 1K+ followers
                score += 4.0
            else:
                score += 2.0
            factors += 1
        
        # Contact information scoring
        if lead_data.get("email"):
            score += 3.0
            factors += 1
        
        if lead_data.get("phone"):
            score += 2.0
            factors += 1
        
        if lead_data.get("website"):
            score += 2.0
            factors += 1
        
        # Verification scoring
        if lead_data.get("verified"):
            score += 5.0
            factors += 1
        
        # Bio/content scoring
        if lead_data.get("bio"):
            bio_length = len(lead_data["bio"])
            if bio_length > 100:
                score += 2.0
            elif bio_length > 50:
                score += 1.0
            factors += 1
        
        return score / factors if factors > 0 else 0.0

# Initialize scraper
scraper = SocialMediaScraper()

# API endpoints
@router.post(
    "/scrape",
    response_model=Dict[str, Any],
    summary="Start social media scraping job",
    description="Start a background job to scrape social media platforms for leads. Requires Pro or Business plan."
)
async def scrape_social_media(
    background_tasks: BackgroundTasks,
    request: SocialScrapingRequest = Body(..., description="Scraping job parameters."),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Scrape social media platforms for leads (background job)."""
    if current_user.plan not in ['pro', 'business']:
        raise HTTPException(status_code=403, detail="Pro or Business plan required")
    
    # Create collection
    collection = LeadCollections(
        name=f"{request.platform.title()} Collection - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        description=f"Keywords: {', '.join(request.keywords)}",
        source_id=1,  # Social media source ID
        user_id=current_user.id,
        config=json.dumps({
            "platform": request.platform,
            "keywords": request.keywords,
            "location": request.location,
            "max_results": request.max_results,
            "filters": request.filters,
            "include_engagement": request.include_engagement,
            "include_contact_info": request.include_contact_info
        })
    )
    
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    # Start background scraping
    background_tasks.add_task(
        scrape_social_media_task,
        collection.id,
        request.platform,
        request.keywords,
        request.location,
        request.max_results,
        request.filters,
        request.include_engagement,
        request.include_contact_info,
        current_user.id
    )
    
    return {
        "collection_id": collection.id,
        "status": "started",
        "message": f"{request.platform.title()} scraping started"
    }

from social_discovery import run_discovery_task

class DiscoveryRequest(BaseModel):
    platforms: List[str] = Field(["linkedin.com/in/", "facebook.com", "instagram.com"])
    skills: List[str] = Field(["Java", "Python", "React", "Mobile Development"])
    cities: List[str] = Field(["Colombo", "Kandy", "Galle", "Gampaha"])
    providers: List[str] = Field(["sliit.lk", "mrt.ac.lk", "nsbm.ac.lk", "iit.lk", "gmail.com"])
    collection_name: Optional[str] = "Undergraduate Discovery"

@router.post("/discovery/undergraduates")
async def start_undergrad_discovery(
    background_tasks: BackgroundTasks,
    request: DiscoveryRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start the fully automated undergraduate discovery engine."""
    
    # Check Lead Source
    source = db.query(LeadSources).filter(LeadSources.name == "Social Discovery Engine").first()
    if not source:
        source = LeadSources(name="Social Discovery Engine", type="x-ray")
        db.add(source)
        db.commit()
        db.refresh(source)
    
    # Create Collection
    collection = LeadCollections(
        name=request.collection_name,
        user_id=current_user.id,
        source_id=source.id,
        status="running",
        config=json.dumps({
            "platforms": request.platforms,
            "skills": request.skills,
            "cities": request.cities
        })
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    background_tasks.add_task(
        run_discovery_task,
        current_user.id,
        request.platforms,
        request.skills,
        request.cities,
        request.providers,
        collection.id
    )
    
    return {
        "status": "started",
        "collection_id": collection.id,
        "message": "High-priority undergraduate discovery engine started."
    }

@router.get("/discovery/status/{collection_id}")
async def get_discovery_status(
    collection_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    collection = db.query(LeadCollections).filter(
        LeadCollections.id == collection_id,
        LeadCollections.user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
        
    lead_count = db.query(SocialMediaLeads).filter(
        SocialMediaLeads.collection_id == collection_id
    ).count()
    
    return {
        "id": collection.id,
        "name": collection.name,
        "status": collection.status,
        "leads_found": lead_count,
        "last_updated": collection.updated_at
    }

async def scrape_social_media_task(
    collection_id: int,
    platform: str,
    keywords: List[str],
    location: Optional[str],
    max_results: int,
    filters: Optional[Dict],
    include_engagement: bool,
    include_contact_info: bool,
    user_id: int
):
    """Background task to scrape social media platforms"""
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        # Scrape based on platform
        if platform == "facebook":
            leads_data = await scraper.scrape_facebook(keywords, location, max_results)
        elif platform == "instagram":
            leads_data = await scraper.scrape_instagram(keywords, location, max_results)
        elif platform == "twitter":
            leads_data = await scraper.scrape_twitter(keywords, location, max_results)
        elif platform == "linkedin":
            leads_data = await scraper.scrape_linkedin(keywords, location, max_results)
        elif platform == "tiktok":
            leads_data = await scraper.scrape_tiktok(keywords, location, max_results)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Process and save leads
        for lead_data in leads_data:
            # Calculate engagement score
            if include_engagement:
                lead_data["engagement_score"] = scraper.calculate_engagement_score(lead_data)
            
            # Create lead record
            lead = SocialMediaLeads(
                platform=lead_data["platform"],
                platform_id=lead_data["platform_id"],
                username=lead_data.get("username"),
                display_name=lead_data.get("display_name"),
                email=lead_data.get("email"),
                phone=lead_data.get("phone"),
                bio=lead_data.get("bio"),
                followers_count=lead_data.get("followers_count"),
                following_count=lead_data.get("following_count"),
                posts_count=lead_data.get("posts_count"),
                location=lead_data.get("location"),
                website=lead_data.get("website"),
                profile_url=lead_data.get("profile_url"),
                avatar_url=lead_data.get("avatar_url"),
                verified=lead_data.get("verified", False),
                business_category=lead_data.get("business_category"),
                engagement_score=lead_data.get("engagement_score"),
                user_id=user_id,
                collection_id=collection_id,
                status="new"
            )
            
            db.add(lead)
        
        # Update collection status
        collection = db.query(LeadCollections).filter(LeadCollections.id == collection_id).first()
        if collection:
            collection.last_run = datetime.utcnow()
            collection.status = "completed"
        
        db.commit()
        
    except Exception as e:
        logger.exception(f"Error in social media scraping task: {e}")
        
        # Update collection status to failed
        collection = db.query(LeadCollections).filter(LeadCollections.id == collection_id).first()
        if collection:
            collection.status = "failed"
            db.commit()
    finally:
        db.close()

@router.get(
    "/leads",
    response_model=List[SocialLeadResponse],
    summary="Get social media leads",
    description="Get a paginated list of social media leads for the authenticated user. Filter by platform and status."
)
async def get_social_leads(
    platform: Optional[str] = Query(None, description="Filter by social media platform (facebook, instagram, etc.)"),
    status: Optional[str] = Query(None, description="Filter by lead status (new, contacted, etc.)"),
    page: int = Query(1, ge=1, description="Page number for pagination."),
    page_size: int = Query(20, ge=1, le=100, description="Number of leads per page."),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get social media leads (paginated, filterable)."""
    query = db.query(SocialMediaLeads).filter(SocialMediaLeads.user_id == current_user.id)
    
    if platform:
        query = query.filter(SocialMediaLeads.platform == platform)
    
    if status:
        query = query.filter(SocialMediaLeads.status == status)
    
    # Pagination
    offset = (page - 1) * page_size
    leads = query.offset(offset).limit(page_size).all()
    
    return [
        SocialLeadResponse(
            id=lead.id,
            platform=lead.platform,
            platform_id=lead.platform_id,
            username=lead.username,
            display_name=lead.display_name,
            email=lead.email,
            phone=lead.phone,
            bio=lead.bio,
            followers_count=lead.followers_count,
            following_count=lead.following_count,
            posts_count=lead.posts_count,
            location=lead.location,
            website=lead.website,
            profile_url=lead.profile_url,
            avatar_url=lead.avatar_url,
            verified=lead.verified,
            business_category=lead.business_category,
            engagement_score=lead.engagement_score,
            status=lead.status,
            tags=json.loads(lead.tags) if lead.tags else [],
            notes=lead.notes,
            created_at=lead.created_at,
            updated_at=lead.updated_at
        )
        for lead in leads
    ]

@router.get(
    "/analytics",
    response_model=Dict[str, Any],
    summary="Get social media analytics",
    description="Get analytics and statistics for social media scraping jobs and leads."
)
async def get_social_analytics(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get social media scraping analytics and statistics."""
    # Get lead counts by platform
    platform_counts = db.query(
        SocialMediaLeads.platform,
        db.func.count(SocialMediaLeads.id).label('count')
    ).filter(
        SocialMediaLeads.user_id == current_user.id
    ).group_by(SocialMediaLeads.platform).all()
    
    # Get engagement statistics
    engagement_stats = db.query(
        db.func.avg(SocialMediaLeads.engagement_score).label('avg_engagement'),
        db.func.max(SocialMediaLeads.engagement_score).label('max_engagement'),
        db.func.min(SocialMediaLeads.engagement_score).label('min_engagement')
    ).filter(
        SocialMediaLeads.user_id == current_user.id,
        SocialMediaLeads.engagement_score.isnot(None)
    ).first()
    
    # Get status distribution
    status_counts = db.query(
        SocialMediaLeads.status,
        db.func.count(SocialMediaLeads.id).label('count')
    ).filter(
        SocialMediaLeads.user_id == current_user.id
    ).group_by(SocialMediaLeads.status).all()
    
    return {
        "platform_counts": {platform: count for platform, count in platform_counts},
        "engagement_stats": {
            "average": float(engagement_stats.avg_engagement) if engagement_stats.avg_engagement else 0,
            "maximum": float(engagement_stats.max_engagement) if engagement_stats.max_engagement else 0,
            "minimum": float(engagement_stats.min_engagement) if engagement_stats.min_engagement else 0
        },
        "status_distribution": {status: count for status, count in status_counts},
        "total_leads": sum(count for _, count in platform_counts)
    } 