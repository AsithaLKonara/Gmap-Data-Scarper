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
git clone https://github.com/AsithaLKonara/Gmap-Data-Scarper.git
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
# Auto-commit system added

## SSO/SAML Support

- SSO/SAML login is only available in Docker or supported Linux environments.
- On macOS 12, the SSO endpoints are placeholders and will not function.
- For SSO development, use Docker or deploy to a Linux server.

## Multi-Tenancy Architecture

LeadTap supports full multi-tenancy for SaaS and enterprise use cases. All user, job, lead, CRM, analytics, notification, support, and API key data is isolated by tenant (organization).

### How it works
- Each user, job, lead, etc. is associated with a `tenant_id`.
- All API requests must include the `X-Tenant` header (tenant slug), set automatically by the frontend after login/registration.
- Backend endpoints strictly filter and validate by tenant, preventing cross-tenant data access.
- Super-admins can manage tenants, onboard new organizations, and switch context for support.

### Migration for Existing Data
- Run `python scripts/assign_default_tenant.py` to assign all orphaned records to a Default Tenant.

### Tenant Onboarding
- Use the admin endpoints to create a new tenant (organization).
- Invite users to the tenant via the onboarding API or UI.
- Users must enter their organization/tenant slug on login/registration.

### Security
- All endpoints enforce tenant isolation.
- Automated tests and utilities ensure no cross-tenant data leaks.

## Per-Tenant SSO/SAML Setup

Tenant admins can enable and configure SSO/SAML for their organization:

1. Go to **Settings > SSO/SAML Configuration** in the admin dashboard.
2. Enter your SSO provider’s details:
   - **Entity ID**: Your SAML entity ID (from your IdP, e.g., Okta, Google, Azure).
   - **SSO URL**: The SAML SSO endpoint (from your IdP).
   - **Certificate**: The X.509 certificate (PEM format) from your IdP.
3. Save the configuration.
4. Users will now see a “Sign in with SSO” button on the login page after entering your organization/tenant slug.
5. Clicking the button will redirect to your SSO provider for authentication.

**Troubleshooting:**
- Ensure all SSO fields are correct and match your IdP’s metadata.
- If SSO is not working, check the SSO config and try again.
- Contact support if you need help with SAML metadata or certificates.
