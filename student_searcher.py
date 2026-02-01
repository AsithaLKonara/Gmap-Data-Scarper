
import time
import csv
import os
import re
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === CONFIG ===
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "sri_lanka_ict_students_final.csv")
HEADLESS = False  

# Domains to target university students
EMAIL_PROVIDERS = [
    'gmail.com', 'sliit.lk', 'mrt.ac.lk', 'cmb.ac.lk', 'nsbm.ac.lk', 'iit.lk'
]

# Cities and keywords for breadth
CITIES = ["Colombo", "Kandy", "Galle", "Jaffna", "Kurunegala", "Gampaha", "Matara"]
SKILLS = ["Java", "Python", "React", "Data Science", "Cyber Security", "Networking"]

def setup_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def extract_contacts(text):
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}', text)
    phones = re.findall(r'(?:\+94|0)7[0-9]\s?[0-9]{3}\s?[0-9]{4}', text) 
    
    email = emails[0] if emails else "N/A"
    phone = phones[0] if phones else "N/A"
    return email, phone

def save_lead(data):
    file_exists = os.path.isfile(OUTPUT_CSV)
    with open(OUTPUT_CSV, 'a', newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Source", "Query", "Name", "Email", "Phone", "Profile Link", "Snippet"])
        writer.writerow(data)

def scrape_leads(driver):
    print("🚀 Student Lead Engine Initialized...")
    
    scraped_links = set()
    if os.path.isfile(OUTPUT_CSV):
        try:
            with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    scraped_links.add(row["Profile Link"])
            print(f"♻️  Resuming: {len(scraped_links)} leads already in file.")
        except Exception as e:
            print(f"Could not read existing file: {e}")

    for provider in EMAIL_PROVIDERS:
        for skill in SKILLS:
            for city in CITIES:
                search_query = f'site:linkedin.com/in/ "student" "{skill}" "{city}" "@{provider}" "Sri Lanka"'
                print(f"🔎 Query: {skill} in {city} (@{provider})")
                
                driver.get(f"https://www.google.com/search?q={urllib.parse.quote(search_query)}")
                time.sleep(5)
                
                if "sorry/index" in driver.current_url:
                    print("⚠️ Google CAPTCHA! Please solve it to continue.")
                    while "sorry/index" in driver.current_url:
                        time.sleep(2)

                # Modern Google results selector (can be div.g, div.MjjYud, etc.)
                results = driver.find_elements(By.CSS_SELECTOR, "div.g, div.MjjYud")
                if not results:
                    print("  ⚠️ No search result containers found on page.")
                    continue

                new_leads_count = 0
                for res in results:
                    try:
                        # Try multiple common link selectors
                        try:
                            link_el = res.find_element(By.CSS_SELECTOR, "a")
                            link = link_el.get_attribute("href")
                        except:
                            continue

                        if not link or "linkedin.com/in/" not in link:
                            continue

                        if link in scraped_links:
                            continue
                        
                        try:
                            title = res.find_element(By.TAG_NAME, "h3").text
                        except:
                            title = "N/A"

                        try:
                            # Try common snippet selectors
                            snippet_selectors = ["div.VwiC3b", "span.st", "div.s"]
                            snippet = "N/A"
                            for sel in snippet_selectors:
                                try:
                                    snippet_el = res.find_element(By.CSS_SELECTOR, sel)
                                    snippet = snippet_el.text
                                    if snippet: break
                                except: continue
                        except:
                            snippet = "N/A"
                        
                        email, phone = extract_contacts(snippet + " " + title)
                        
                        save_lead(["LinkedIn", f"{skill}@{city}", title, email, phone, link, snippet])
                        scraped_links.add(link)
                        new_leads_count += 1
                        print(f"  ✅ Added: {title[:30]}...")
                    except Exception as e:
                        # print(f"    Error processing a result: {e}")
                        continue
                
                if new_leads_count == 0:
                    print("  ⚠️ No NEW leads found for this query.")
                else:
                    print(f"  ✨ Total new leads for this query: {new_leads_count}")

                time.sleep(15) 

def main():
    driver = setup_driver()
    try:
        scrape_leads(driver)
    except KeyboardInterrupt:
        print("\n🛑 Session paused.")
    except Exception as e:
        print(f"\n☢️  Fatal Error: {e}")
    finally:
        driver.quit()
        if os.path.isfile(OUTPUT_CSV):
            print(f"📊 Process finished. Check {OUTPUT_CSV}")
        else:
            print("📊 Process finished, but no file was created.")

if __name__ == "__main__":
    main()
