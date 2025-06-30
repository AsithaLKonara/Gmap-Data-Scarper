# 🏺️ Gmap Lead Scraper

A powerful and customizable web scraping tool built in Python to collect business leads from Google Maps. It extracts essential business information for multiple search queries and saves the data into a CSV file for use in outreach, research, or lead generation.

---

## ✨ Features

* 🔍 Automates Google Maps searches
* 📅 Extracts multiple leads per query
* 📌 Captures:

  * Business Name
  * Category
  * Address
  * Phone Number
  * Website
  * Plus Code
* 📄 Saves data to CSV in `~/Documents`
* 💻 Works on Mac and cross-platform
* 🧠 Handles both multi-result lists and single business pages
* 🔁 Retries failed attempts automatically

---

## 📁 File Structure

```
gmap-data-scraper/
├── app.py                  # Main scraper script
├── search_queries.txt      # List of search terms (one per line)
├── gmap_all_leads.csv      # Output file with results
├── venv/                   # Python virtual environment
├── README.md               # This documentation
```

---

## 🧰 Requirements

* Python 3.8 or higher
* Google Chrome browser (latest)
* ChromeDriver (managed automatically)

Install dependencies with:

```bash
pip install selenium webdriver-manager
```

---

## 🚀 Setup Instructions

### Step 1: Clone the Project

```bash
git clone <your-local-folder>
cd gmap-data-scraper
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing:

```bash
pip install selenium webdriver-manager
```

---

## ✏️ Create Input File

Create a file named `search_queries.txt` in the **project folder**:

```bash
touch search_queries.txt
```

Add search terms like:

```
restaurant in Nuwara Eliya
auto parts shop in Badulla
furniture shop in Polonnaruwa
salon in Anuradhapura
```

---

## ▶️ Run the Scraper

From the project folder:

```bash
python3 app.py
```

This will:

* Launch Chrome
* Search each term
* Scroll and click on each result
* Collect data and save to `gmap_all_leads.csv` in the same folder

---

## ✅ Output Format

CSV columns:

* Search Query
* Business Name
* Category
* Address
* Phone
* Website
* Plus Code

Example row:

```
restaurant in Nuwara Eliya,Green Hills Restaurant,Restaurant,No.10 Gregory Road,+94 77 123 4567,www.greenhills.lk,PX9W+V3 Nuwara Eliya
```

---

## 👨‍💻 Author

**Asitha L Konara**

---

## ⚠️ Disclaimer

This tool is intended for personal or educational use. Please use responsibly and in accordance with Google Maps' terms of service.
# Gmap-Data-Scarper
