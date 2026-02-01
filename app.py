
import time
import csv
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager

# === CONFIG ===
HEADLESS = False
QUERIES_FILE = os.path.join(os.path.dirname(__file__), "search_queries.txt")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "gmap_ict_leads.csv") # Changed to local dir for easier access
RETRY_ATTEMPTS = 3

# === SETUP DRIVER ===
def setup_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Hide automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def safe_get(driver, url, retries=RETRY_ATTEMPTS):
    for attempt in range(1, retries + 1):
        try:
            driver.get(url)
            return True
        except Exception as e:
            print(f"[Retry {attempt}] Failed to open URL: {e}")
            time.sleep(5)
    return False

# === SCROLL RESULTS PANEL ===
def scroll_results(driver):
    try:
        # Increase wait time for the results panel
        results_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "m6QErb"))
        )
        print("📄 Found results panel. Scrolling deeply...")
        last_height = driver.execute_script("return arguments[0].scrollHeight", results_box)
        
        # Scroll more aggressively for 5000 leads goal
        for i in range(40): 
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_box)
            time.sleep(2)
            new_height = driver.execute_script("return arguments[0].scrollHeight", results_box)
            if new_height == last_height and i > 10: # Break early if no more results
                break
            last_height = new_height
        return True
    except TimeoutException:
        print("⚠️ No results panel found. Possibly a single place page.")
        return False

# === EXTRACT BUSINESS DETAILS ===
def extract_info(driver, query):
    def safe_find(css_selector, fallback="N/A"):
        try:
            return driver.find_element(By.CSS_SELECTOR, css_selector).text
        except:
            return fallback

    name = safe_find('h1[class*="DUwDvf"]')
    category = safe_find('button[class*="DkEaL"]')

    address, phone, website, plus_code = "N/A", "N/A", "N/A", "N/A"
    try:
        # Find detail elements
        elements = driver.find_elements(By.CLASS_NAME, "Io6YTe")
        for el in elements:
            text = el.text
            if not text: continue
            
            # Simple regex for phone (can be improved for SL)
            if re.search(r'(\+94|0)\s*\d{2}\s*\d{3}\s*\d{4}', text) or re.search(r'\d{3} \d{3} \d{4}', text):
                phone = text
            elif '.' in text and any(ext in text.lower() for ext in ['.com', '.net', '.org', '.edu', '.lk']):
                website = text
            elif '+' in text and len(text) < 20: 
                plus_code = text
            elif address == "N/A" and (',' in text or any(word in text.lower() for word in ['street', 'road', 'rd', 'ave', 'lane'])):
                address = text
    except:
        pass

    return [query, name, category, address, phone, website, plus_code]

# === FILE SAVING ===
def save_to_csv(data, mode='a'):
    file_exists = os.path.isfile(OUTPUT_CSV)
    with open(OUTPUT_CSV, mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists or mode == 'w':
            writer.writerow(["Search Query", "Business Name", "Category", "Address", "Phone", "Website", "Plus Code"])
        if data:
            writer.writerow(data)

# === MAIN ===
def main():
    if not os.path.isfile(QUERIES_FILE):
        print(f"❌ Query file not found: {QUERIES_FILE}")
        return

    with open(QUERIES_FILE, 'r', encoding='utf-8') as f:
        queries = [line.strip() for line in f.readlines() if line.strip()]

    if not queries:
        print("❌ No valid queries found.")
        return

    print(f"🚀 Starting scraper for {len(queries)} queries.")
    print(f"📊 Results will be saved to: {OUTPUT_CSV}")

    driver = setup_driver()
    total_scraped = 0
    visited_names = set()

    # Load existing names to avoid duplicates if resuming
    if os.path.isfile(OUTPUT_CSV):
        try:
            with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    visited_names.add(row["Business Name"])
            print(f"♻️  Loaded {len(visited_names)} existing leads to avoid duplicates.")
        except:
            pass

    try:
        for q_index, query in enumerate(queries):
            print(f"\n🔎 [{q_index+1}/{len(queries)}] Searching: {query}")

            if not safe_get(driver, "https://www.google.com/maps"):
                print("❌ Failed to open Google Maps.")
                continue

            try:
                search_box = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "searchboxinput"))
                )
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.ENTER)
                time.sleep(5)
            except Exception as e:
                # Try fallback search box class
                try:
                    search_box = driver.find_element(By.CLASS_NAME, "searchboxinput")
                    search_box.clear()
                    search_box.send_keys(query)
                    search_box.send_keys(Keys.ENTER)
                    time.sleep(5)
                except:
                    print(f"❌ Failed to input search: {e}")
                    continue

            has_results_list = scroll_results(driver)

            if not has_results_list:
                info = extract_info(driver, query)
                if info[1] != "N/A" and info[1] not in visited_names:
                    save_to_csv(info)
                    visited_names.add(info[1])
                    total_scraped += 1
                    print(f"  ✅ Direct page scraped: {info[1]}")
                continue

            # Scrape results list
            result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
            print(f"🧾 Found {len(result_items)} potential results")

            for index in range(len(result_items)):
                try:
                    # Refresh element list to avoid stale reference
                    result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                    if index >= len(result_items): break
                    
                    result = result_items[index]
                    
                    # Try to extract name before clicking to avoid duplicates early
                    try:
                        name_el = result.find_element(By.CLASS_NAME, "qBF1Pd")
                        name_text = name_el.text
                        if name_text in visited_names:
                            continue
                    except:
                        pass

                    driver.execute_script("arguments[0].scrollIntoView();", result)
                    time.sleep(1)

                    try:
                        result.click()
                    except:
                        driver.execute_script("arguments[0].click();", result)

                    time.sleep(3) # Wait for panel to load
                    info = extract_info(driver, query)
                    
                    if info[1] != "N/A" and info[1] not in visited_names:
                        save_to_csv(info)
                        visited_names.add(info[1])
                        total_scraped += 1
                        print(f"  ✅ {total_scraped}. {info[1]}")
                    
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    print(f"  ⚠️ Error at result {index+1}: {e}")
                    continue

            # Cooldown between queries to avoid bot detection
            print(f"💤 Cooling down...")
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n🛑 Scraper stopped by user.")
    except Exception as e:
        print(f"\n☢️  Critical error: {e}")
    finally:
        driver.quit()
        print(f"\n✅ Done! Total leads collected in this session: {total_scraped}")
        print(f"📊 Total leads in CSV: {len(visited_names)}")
        print(f"📁 Saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
