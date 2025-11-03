import time
import csv
import os
import re
import sys
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
HEADLESS = False  # Set to False to see Chrome browser window
QUERIES_FILE = os.path.join(os.path.dirname(__file__), "search_queries.txt")
OUTPUT_CSV = os.path.expanduser("~/Documents/gmap_all_leads.csv")
RETRY_ATTEMPTS = 3
DELAY_BETWEEN_QUERIES = 10  # Add delay between queries
MAX_RESULTS_PER_QUERY = 20  # Increased limit for more results per query
RESUME_MODE = False  # Process all queries (including already done ones)

# Use simple text instead of emojis for better compatibility

# === SETUP DRIVER ===
def setup_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless")
    
    # Performance optimizations
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")
    options.add_argument("--disable-css")
    options.add_argument("--memory-pressure-off")
    options.add_argument("--max_old_space_size=4096")
    
    # Reduce memory usage
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def safe_get(driver, url, retries=RETRY_ATTEMPTS):
    for attempt in range(1, retries + 1):
        try:
            driver.get(url)
            return True
        except Exception as e:
            print(f"[RETRY {attempt}] Failed to open URL: {e}")
            time.sleep(5)
    return False

# === SCROLL RESULTS PANEL ===
def scroll_results(driver):
    try:
        # Wait for results panel
        results_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "m6QErb"))
        )
        print("[INFO] Found results panel. Scrolling to load all results...")
        
        # Get initial count
        initial_count = len(driver.find_elements(By.CLASS_NAME, "Nv2PK"))
        print(f"[INFO] Initial results found: {initial_count}")
        
        # Scroll multiple times to load more results
        last_count = initial_count
        stable_count = 0
        
        for scroll_attempt in range(100):  # Increased to 100 scroll attempts
            # Scroll to bottom with multiple scroll steps
            for i in range(3):  # Multiple scroll steps per attempt
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_box)
                time.sleep(0.5)  # Short wait between scrolls
            
            time.sleep(3)  # Longer wait time for loading
            
            # Also try scrolling by a large amount to trigger more loading
            driver.execute_script("arguments[0].scrollTop += 2000", results_box)
            time.sleep(2)
            
            # Check if new results loaded
            current_count = len(driver.find_elements(By.CLASS_NAME, "Nv2PK"))
            
            if current_count > last_count:
                print(f"[INFO] Loaded more results: {current_count} (was {last_count})")
                last_count = current_count
                stable_count = 0
            else:
                stable_count += 1
                
            # If no new results for 5 consecutive scrolls, we're done (increased from 3)
            if stable_count >= 5:
                print(f"[INFO] No more results loading. Final count: {current_count}")
                break
                
            # Additional check: if we have more than 20 results, scroll even more aggressively
            if current_count > 20:
                for extra_scroll in range(5):
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_box)
                    time.sleep(1)
                    driver.execute_script("arguments[0].scrollTop += 1000", results_box)
                    time.sleep(1)
                    
            # Try alternative scrolling methods
            if scroll_attempt % 10 == 0:  # Every 10th attempt
                # Try scrolling with page down
                results_box.send_keys(Keys.PAGE_DOWN)
                time.sleep(2)
                results_box.send_keys(Keys.PAGE_DOWN)
                time.sleep(2)
                
                # Try scrolling with end key
                results_box.send_keys(Keys.END)
                time.sleep(2)
                
        # Final aggressive scroll to ensure all are loaded
        print("[INFO] Performing final aggressive scroll...")
        for final_scroll in range(10):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_box)
            time.sleep(1)
            driver.execute_script("arguments[0].scrollTop += 3000", results_box)
            time.sleep(1)
            results_box.send_keys(Keys.END)
            time.sleep(1)
        
        # Scroll back to top
        driver.execute_script("arguments[0].scrollTop = 0", results_box)
        time.sleep(1)
        
        final_count = len(driver.find_elements(By.CLASS_NAME, "Nv2PK"))
        print(f"[INFO] Scrolling complete. Total results: {final_count}")
        return True
        
    except TimeoutException:
        print("[WARNING] No results panel found. Possibly a single place page.")
        return False
    except Exception as e:
        print(f"[ERROR] Error during scrolling: {e}")
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

# === INCREMENTAL CSV WRITER ===
def write_result_to_csv(result_data, csv_file):
    """Write a single result to CSV file immediately"""
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow(["Search Query", "Business Name", "Category", "Address", "Phone", "Website", "Plus Code"])
        
        # Write the result
        writer.writerow(result_data)
    
    print(f"[SAVE] Saved to CSV: {result_data[1]}")

def get_processed_queries(csv_file):
    """Get list of queries that have already been processed"""
    if not os.path.exists(csv_file):
        return set()
    
    processed = set()
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row and len(row) > 0:
                    processed.add(row[0])  # First column is search query
    except Exception as e:
        print(f"[WARNING] Error reading existing CSV: {e}")
    
    return processed

# === MAIN ===
def main():
    if not os.path.isfile(QUERIES_FILE):
        print(f"[ERROR] Query file not found: {QUERIES_FILE}")
        return

    with open(QUERIES_FILE, 'r', encoding='utf-8') as f:
        all_queries = list(set([line.strip() for line in f.readlines() if line.strip()]))

    if not all_queries:
        print("[ERROR] No valid queries found.")
        return

    # Filter out already processed queries if resume mode is enabled
    if RESUME_MODE:
        processed_queries = get_processed_queries(OUTPUT_CSV)
        queries = [q for q in all_queries if q not in processed_queries]
        
        if processed_queries:
            print(f"[INFO] Found {len(processed_queries)} already processed queries")
            print(f"[RESUME] Resuming with {len(queries)} remaining queries")
        else:
            print(f"[START] Starting fresh with {len(queries)} queries")
    else:
        queries = all_queries
        print(f"[START] Processing all {len(queries)} queries")

    if not queries:
        print("[DONE] All queries have already been processed!")
        return

    driver = setup_driver()
    total_saved = 0

    for q_index, query in enumerate(queries):
        print(f"\n[SEARCH] [{q_index+1}/{len(queries)}] Searching: {query}")
        
        # Add delay between queries to prevent overload
        if q_index > 0:
            print(f"[WAIT] Waiting {DELAY_BETWEEN_QUERIES} seconds before next query...")
            time.sleep(DELAY_BETWEEN_QUERIES)

        if not safe_get(driver, "https://maps.google.com"):
            print("[ERROR] Failed to open Google Maps.")
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
            print(f"[ERROR] Failed to input search: {e}")
            continue

        has_results_list = scroll_results(driver)

        if not has_results_list:
            info = extract_info(driver, query)
            write_result_to_csv(info, OUTPUT_CSV)
            total_saved += 1
            print(f"[SUCCESS] Direct page scraped: {info[1]}")
            continue

        result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        print(f"[INFO] Found {len(result_items)} businesses")

        visited = set()

        # Limit results to prevent overload
        max_results = min(len(result_items), MAX_RESULTS_PER_QUERY)
        
        for index in range(max_results):
            try:
                result_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                if index >= len(result_items):
                    break

                result = result_items[index]
                if result in visited:
                    continue
                visited.add(result)

                driver.execute_script("arguments[0].scrollIntoView();", result)
                time.sleep(2)  # Increased delay

                try:
                    result.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", result)

                time.sleep(3)  # Reduced wait time
                info = extract_info(driver, query)
                write_result_to_csv(info, OUTPUT_CSV)
                total_saved += 1
                print(f"  [SUCCESS] {index+1}. {info[1]}")
                
                # Add delay between results
                time.sleep(2)
            except Exception as e:
                print(f"  [WARNING] Error at result {index+1}: {e}")
                continue

    driver.quit()

    print(f"\n[DONE] Scraped {total_saved} records.")
    print(f"[SAVE] All data saved incrementally to: {OUTPUT_CSV}")
    print(f"[SAFE] Data is safe even if program stops unexpectedly!")

if __name__ == "__main__":
    main()
