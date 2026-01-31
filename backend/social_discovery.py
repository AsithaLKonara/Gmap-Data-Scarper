
import os
import re
import json
import time
import random
import urllib.parse
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event

import sqlalchemy
from sqlalchemy.orm import Session
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from database import SessionLocal
from models import SocialMediaLeads, LeadSources, LeadCollections

logger = logging.getLogger("social-discovery")

class SocialDiscoveryEngine:
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
        self.scraped_links = set()
        self.max_workers = 3
        self.captcha_event = Event()
        self.captcha_event.set()
        self._load_existing_leads()

    def _load_existing_leads(self):
        existing = self.db.query(SocialMediaLeads.profile_url).filter(SocialMediaLeads.user_id == self.user_id).all()
        for lead in existing:
            self.scraped_links.add(lead.profile_url)

    def setup_driver(self, headless: bool = True):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"user-agent={random.choice(ua_list)}")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(45)
        return driver

    def extract_contacts(self, text: str):
        phones = re.findall(r'(?:\+94|0)7[01245678]\s?[0-9]{3}\s?[0-9]{4}', text)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}', text)
        return (emails[0] if emails else None, phones[0] if phones else None)

    def scrape_query(self, platform: str, skill: str, city: str, provider: str, collection_id: int):
        self.captcha_event.wait()
        
        exclusions = '-"Graduated" -"Alumni" -"BSc" -"Former" -"Engineer"'
        search_query = f'site:{platform} "Sri Lanka" "Undergraduate" "{skill}" "{city}" "@{provider}" {exclusions}'
        
        driver = self.setup_driver()
        leads_found = []
        
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
            driver.get(url)
            time.sleep(random.uniform(3, 7))

            if "sorry/index" in driver.current_url:
                if self.captcha_event.is_set():
                    self.captcha_event.clear()
                    logger.warning("CAPTCHA hit. Pausing engine.")
                    time.sleep(300)
                    self.captcha_event.set()
                return []

            results = driver.find_elements(By.CSS_SELECTOR, "div.g, div.MjjYud")
            for res in results:
                try:
                    link_el = res.find_element(By.CSS_SELECTOR, "a")
                    link = link_el.get_attribute("href")
                    if not link or link in self.scraped_links or "google.com" in link:
                        continue
                    
                    try: title = res.find_element(By.TAG_NAME, "h3").text
                    except: title = "N/A"

                    snippet = "N/A"
                    for sel in ["div.VwiC3b", "span.st"]:
                        try:
                            snippet_el = res.find_element(By.CSS_SELECTOR, sel)
                            snippet = snippet_el.text
                            if snippet: break
                        except: pass

                    email, phone = self.extract_contacts(snippet + " " + title)
                    
                    self.scraped_links.add(link)
                    leads_found.append({
                        "name": title,
                        "email": email,
                        "phone": phone,
                        "link": link,
                        "bio": snippet,
                        "platform": "linkedin" if "linkedin" in platform else ("facebook" if "facebook" in platform else "instagram"),
                        "query": f"{skill}@{city}"
                    })
                except: continue
        finally:
            driver.quit()
        return leads_found

def run_discovery_task(user_id: int, platforms: List[str], skills: List[str], cities: List[str], providers: List[str], collection_id: int):
    """Background task to run discovery"""
    db = SessionLocal()
    engine = SocialDiscoveryEngine(user_id, db)
    
    all_tasks = []
    for platform in platforms:
        for skill in skills:
            for city in cities:
                for provider in providers:
                    all_tasks.append((platform, skill, city, provider))
    
    random.shuffle(all_tasks)
    
    with ThreadPoolExecutor(max_workers=engine.max_workers) as executor:
        futures = {executor.submit(engine.scrape_query, t[0], t[1], t[2], t[3], collection_id): t for t in all_tasks}
        
        for future in as_completed(futures):
            try:
                new_leads = future.result()
                if new_leads:
                    for lead_data in new_leads:
                        # Save to DB
                        lead = SocialMediaLeads(
                            user_id=user_id,
                            platform=lead_data["platform"],
                            display_name=lead_data["name"],
                            email=lead_data["email"],
                            phone=lead_data["phone"],
                            bio=lead_data["bio"],
                            profile_url=lead_data["link"],
                            collection_id=collection_id,
                            status="new",
                            tags=json.dumps([lead_data["query"]])
                        )
                        db.add(lead)
                    db.commit()
            except Exception as e:
                logger.error(f"Discovery Task Error: {e}")
                db.rollback()
    
    # Finalize collection
    collection = db.query(LeadCollections).filter(LeadCollections.id == collection_id).first()
    if collection:
        collection.status = "completed"
        db.commit()
    db.close()
