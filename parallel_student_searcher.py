
import time
import csv
import os
import re
import urllib.parse
import json
import random
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event
from datetime import datetime

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
DB_PATH = os.path.join(BASE_DIR, "leadtap.db")
OUTPUT_CSV = os.path.join(BASE_DIR, "sri_lanka_ict_students_final.csv")
STATE_FILE = os.path.join(BASE_DIR, "scraper_state.pkl")
LOG_FILE = os.path.join(BASE_DIR, "scraper.log")

# Import models
import sys
sys.path.append(BACKEND_DIR)
try:
    from database import Base, engine, SessionLocal
    from models import SocialMediaLeads, LeadSources, LeadCollections
except ImportError:
    print("⚠️ Backend models not found. Will only save to CSV.")
    SessionLocal = None

# === CONFIG ===
HEADLESS = True  
MAX_WORKERS = 4  
QUERY_DELAY = (20, 40)   # Slower to avoid platform bans
CAPTCHA_WAIT = 600       # 10 minutes wait on CAPTCHA
PAGE_LOAD_WAIT = 5

# TARGET PLATFORMS
PLATFORMS = ["linkedin.com/in/", "facebook.com", "instagram.com"]

# SPECIFIC UNDERGRADUATE PROVIDERS
# sliit.lk, etc. are high signal for current students
EMAIL_PROVIDERS = [
    'sliit.lk', 'mrt.ac.lk', 'cmb.ac.lk', 'nsbm.ac.lk', 'iit.lk', 'kln.ac.lk', 'jfn.ac.lk', 
    'gmail.com', 'yahoo.com'
]

CITIES = [
    "Colombo", "Kandy", "Galle", "Jaffna", "Kurunegala", "Gampaha", "Matara", 
    "Negombo", "Anuradhapura", "Trincomalee"
]

# Focus on Undergraduate keywords and exclude "Graduated", "BSc", "Alumni"
STUDENT_KEYWORDS = [
    '"Undergraduate"', '"Student"', '"University student"', '"Bachelor student"', 
    '"Followers"', '"Currently studying"'
]

# Exclusion to filter out graduates/professionals
EXCLUSIONS = '-"Graduated" -"Alumni" -"BSc" -"Former" -"Engineer" -"Developer" -"Manager"'

SKILLS = [
    "Java", "Python", "React", "Data Science", "Cyber Security", 
    "Networking", "Software Engineering", "AI", "Mobile Development"
]

# --- Globals ---
csv_lock = Lock()
db_lock = Lock()
scraped_links = set()
finished_queries = set()
captcha_event = Event()
captcha_event.set() # Set means "clear to go"
driver_path = None

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def get_driver_path():
    global driver_path
    if not driver_path:
        driver_path = ChromeDriverManager().install()
    return driver_path

def setup_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(ua_list)}")
    
    service = Service(get_driver_path())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(45)
    return driver

def save_state():
    with csv_lock:
        with open(STATE_FILE, "wb") as f:
            pickle.dump({'finished_queries': finished_queries}, f)

def load_state():
    global finished_queries
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "rb") as f:
                data = pickle.load(f)
                finished_queries = data.get('finished_queries', set())
        except: pass

def save_lead_to_csv(data):
    with csv_lock:
        file_exists = os.path.isfile(OUTPUT_CSV)
        with open(OUTPUT_CSV, 'a', newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Source", "Query", "Name", "Email", "Phone", "Profile Link", "Snippet", "Timestamp"])
            writer.writerow(data + [datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def save_lead_to_db(data_map):
    if not SessionLocal: return
    with db_lock:
        session = SessionLocal()
        try:
            source = session.query(LeadSources).filter(LeadSources.name == "Social Media Undergraduate Search").first()
            if not source:
                source = LeadSources(name="Social Media Undergraduate Search", type="social")
                session.add(source)
                session.commit()
                session.refresh(source)
            
            collection = session.query(LeadCollections).filter(LeadCollections.name == "Undergraduate Leads").first()
            if not collection:
                collection = LeadCollections(name="Undergraduate Leads", user_id=1, source_id=source.id)
                session.add(collection)
                session.commit()
                session.refresh(collection)
            
            exists = session.query(SocialMediaLeads).filter(SocialMediaLeads.profile_url == data_map['link']).first()
            if not exists:
                lead = SocialMediaLeads(
                    user_id=1, platform="social",
                    display_name=data_map['name'],
                    email=data_map['email'] if data_map['email'] != "N/A" else None,
                    phone=data_map['phone'] if data_map['phone'] != "N/A" else None,
                    bio=data_map['snippet'],
                    profile_url=data_map['link'],
                    collection_id=collection.id,
                    status="new",
                    tags=json.dumps([data_map['query']])
                )
                session.add(lead)
                session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()

def extract_contacts(text):
    # Improved phone regex for Sri Lanka mobile numbers (07x xxxxxxx or +947x xxxxxxx)
    # Target: 071, 072, 075, 076, 077, 078, 070, 074
    phones = re.findall(r'(?:\+94|0)7[01245678]\s?[0-9]{3}\s?[0-9]{4}', text)
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}', text)
    
    email = emails[0] if emails else "N/A"
    phone = phones[0] if phones else "N/A"
    return email, phone

def worker_task(query_tuple):
    skill, city, provider, platform = query_tuple
    query_str = f"{skill}|{city}|{provider}|{platform}"
    
    if query_str in finished_queries: return 0
    captcha_event.wait()

    # X-Ray Search Query construction
    # Targets undergraduates, excludes graduates, looks for Sri Lankan context
    search_query = f'site:{platform} "Sri Lanka" {STUDENT_KEYWORDS[random.randint(0, len(STUDENT_KEYWORDS)-1)]} "{skill}" "{city}" "@{provider}" {EXCLUSIONS}'
    
    driver = None
    leads_found = 0
    try:
        driver = setup_driver()
        url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        driver.get(url)
        time.sleep(PAGE_LOAD_WAIT)

        if "sorry/index" in driver.current_url:
            if captcha_event.is_set():
                captcha_event.clear()
                log(f"🛑 CAPTCHA detected for {query_str}. Pausing for {CAPTCHA_WAIT}s.")
                time.sleep(CAPTCHA_WAIT)
                captcha_event.set()
            return -1

        results = driver.find_elements(By.CSS_SELECTOR, "div.g, div.MjjYud")
        for res in results:
            try:
                link_el = res.find_element(By.CSS_SELECTOR, "a")
                link = link_el.get_attribute("href")
                
                # Filter out google results/cache
                if not link or "google.com" in link or "search?" in link: continue

                try: title = res.find_element(By.TAG_NAME, "h3").text
                except: title = "N/A"

                snippet = "N/A"
                for sel in ["div.VwiC3b", "span.st", "div.s"]:
                    try:
                        snippet_el = res.find_element(By.CSS_SELECTOR, sel)
                        snippet = snippet_el.text
                        if snippet: break
                    except: pass

                email, phone = extract_contacts(snippet + " " + title)
                
                # WE ONLY CARE ABOUT LEADS WITH PHONE NUMBERS IF POSSIBLE
                # But we'll capture all for now and note preference
                
                with csv_lock:
                    if link in scraped_links: continue
                    scraped_links.add(link)
                
                platform_name = "LinkedIn" if "linkedin" in platform else ("Facebook" if "facebook" in platform else "Instagram")
                save_lead_to_csv([platform_name, f"{skill}@{city}", title, email, phone, link, snippet])
                save_lead_to_db({'name': title, 'email': email, 'phone': phone, 'link': link, 'snippet': snippet, 'query': f"{skill}@{city}"})
                
                if phone != "N/A":
                    leads_found += 1
                else: 
                    # If no phone, we still count as a lead but maybe lower priority
                    leads_found += 0.1 
            except: continue
        
        with csv_lock:
            finished_queries.add(query_str)
            save_state()
                
    except Exception as e:
        log(f"Error in task {query_str}: {e}")
    finally:
        if driver: driver.quit()
    
    return int(leads_found) if leads_found >= 1 else (1 if leads_found > 0 else 0)

def main():
    log("Scraper Started - Undergraduate Focus")
    print("🚀 Initializing Undergraduate Lead Engine (LinkedIn, FB, Insta)...")
    
    load_state()
    if os.path.isfile(OUTPUT_CSV):
        try:
            with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    scraped_links.add(row["Profile Link"])
        except: pass

    get_driver_path()

    # Generate multi-platform queries
    all_queries = []
    for platform in PLATFORMS:
        for provider in EMAIL_PROVIDERS:
            for skill in SKILLS:
                for city in CITIES:
                    all_queries.append((skill, city, provider, platform))
    
    random.shuffle(all_queries)
    remaining_queries = [q for q in all_queries if f"{q[0]}|{q[1]}|{q[2]}|{q[3]}" not in finished_queries]
    
    print(f"📦 Total queries: {len(all_queries)} | Remaining: {len(remaining_queries)}")
    print(f"🎯 Target: Undergraduates (Excluding Graduates) with Contact Numbers")
    
    if not remaining_queries:
        print("✅ All queries already finished or no new queries found.")
        return

    total_new = 0
    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(worker_task, q): q for q in remaining_queries}
            
            with tqdm(total=len(remaining_queries), desc="Scraping") as pbar:
                for future in as_completed(futures):
                    try:
                        res = future.result()
                        if res >= 0:
                            total_new += res
                            pbar.update(1)
                            pbar.set_postfix({"new": total_new})
                        else:
                            # CAPTCHA or retryable error handled inside
                            pbar.update(0) 
                    except Exception as e:
                        log(f"Future Error: {e}")
                        pbar.update(1)
                    
                    # Global throttle
                    time.sleep(random.uniform(*QUERY_DELAY) / MAX_WORKERS)
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    except Exception as e:
        log(f"Fatal crash in executor: {e}")

    print(f"\n✅ Session finished. Total new leads: {total_new}")
    log("Scraper Finished")

if __name__ == "__main__":
    while True:
        try:
            main()
            # If main finishes normally, check if there are still remaining queries
            load_state()
            all_q = [(s, c, p) for p in EMAIL_PROVIDERS for s in SKILLS for c in CITIES]
            rem = [q for q in all_q if f"{q[0]}|{q[1]}|{q[2]}" not in finished_queries]
            if not rem:
                print("🏁 All work completed successfully.")
                break
            print("⏳ Re-starting in 60s to finish remaining queries...")
            time.sleep(60)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"☢️  System crash: {e}. Re-starting in 30s...")
            time.sleep(30)
