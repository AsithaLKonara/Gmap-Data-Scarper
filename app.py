
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
    TimeoutException, NoSuchElementException, ElementClickInterceptedException
)
from webdriver_manager.chrome import ChromeDriverManager

# === CONFIG ===
HEADLESS = False
QUERIES_FILE = os.path.join(os.path.dirname(__file__), "search_queries.txt")
OUTPUT_CSV = os.path.expanduser("~/Documents/gmap_all_leads.csv")
RETRY_ATTEMPTS = 3

# === SETUP DRIVER ===
def setup_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
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
        results_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "m6QErb"))
        )
        print("📄 Found results panel. Scrolling...")
        for _ in range(25):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_box)
            time.sleep(1)
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
        elements = driver.find_elements(By.CLASS_NAME, "Io6YTe")
        for el in elements:
            text = el.text
            if re.search(r'\d{3} \d{3} \d{4}', text):
                phone = text
            elif '.' in text and any(ext in text for ext in ['.com', '.net', '.org']):
                website = text
            elif '+' in text:
                plus_code = text
            elif address == "N/A":
                address = text
    except:
        pass

    return [query, name, category, address, phone, website, plus_code]

# === MAIN ===
def main():
    if not os.path.isfile(QUERIES_FILE):
        print(f"❌ Query file not found: {QUERIES_FILE}")
        return

    with open(QUERIES_FILE, 'r', encoding='utf-8') as f:
        queries = list(set([line.strip() for line in f.readlines() if line.strip()]))

    if not queries:
        print("❌ No valid queries found.")
        return

    driver = setup_driver()
    all_data = []

    for q_index, query in enumerate(queries):
        print(f"\n🔎 [{q_index+1}/{len(queries)}] Searching: {query}")

        if not safe_get(driver, "https://maps.google.com"):
            print("❌ Failed to open Google Maps.")
            continue

        try:
            search_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "searchboxinput"))
            )
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.ENTER)
            time.sleep(5)
        except Exception as e:
            print(f"❌ Failed to input search: {e}")
            continue

        has_results_list = scroll_results(driver)

        if not has_results_list:
            info = extract_info(driver, query)
            all_data.append(info)
            print(f"✅ Direct page scraped: {info[1]}")
            continue

        result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        print(f"🧾 Found {len(result_items)} businesses")

        visited = set()

        for index in range(len(result_items)):
            try:
                result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                if index >= len(result_items):
                    break

                result = result_items[index]
                if result in visited:
                    continue
                visited.add(result)

                driver.execute_script("arguments[0].scrollIntoView();", result)
                time.sleep(1)

                try:
                    result.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", result)

                time.sleep(5)
                info = extract_info(driver, query)
                all_data.append(info)
                print(f"  ✅ {index+1}. {info[1]}")
            except Exception as e:
                print(f"  ⚠️ Error at result {index+1}: {e}")
                continue

    driver.quit()

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Search Query", "Business Name", "Category", "Address", "Phone", "Website", "Plus Code"])
        writer.writerows(all_data)

    print(f"\n✅ Done! Scraped {len(all_data)} records.")
    print(f"📁 Saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
