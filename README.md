# 🤖 AI-Powered B2B Prospect Generation Engine (Demo)

This repository contains a two-phase Python solution for scraping target company data from LinkedIn, forming the foundation for an advanced AI-driven lead generation system.

The core idea is simple: **High-quality data fuels effective personalized outreach.** 

[Image of Selenium web scraping architecture]

## 💡 Beyond the Demo: From Prospects to Leads

This engine is the **Data Backbone** of our advanced lead generation system at **Hirundo**.

We don't just stop at data extraction. We leverage the comprehensive details (`Overview`, `Industry`, `Size`) to **generate hyper-personalized messages using our proprietary AI model**. This personalization ensures that every outreach message is highly relevant to the prospect's business, dramatically increasing conversion rates from prospects to qualified leads.

**Do you want to use this engine too, integrating it with AI to generate leads based on the service you offer?**

**👉 Write to me directly on LinkedIn to find out more:** [Giacomo Maraglino](https://www.linkedin.com/in/giacomo-maraglino-9a811b144/)

---

## 🚀 The Engine: Prospecting in Two Phases

This engine is designed to minimize risk and maximize data quality by dividing the process into two logical stages.

### 📌 Phase 1: URL & Name Collection (`scraper_phase1_urls.py`)

* **Goal:** Quickly search LinkedIn based on **Keywords** (e.g., "Software House") and **Geographic IDs** (e.g., Italy, Milan) and collect the corresponding company URLs and Names.
* **Output:** `prospects_raw.csv` (list of target URLs).
* **Safety:** Minimal network activity per page, focusing only on search results.

### ⚙️ Phase 2: Detailed Data Extraction (`scraper_phase2_details.py`)

* **Goal:** Read the URLs from `prospects_raw.csv`, visit the `/about/` page for each company, and extract critical details like **Overview/Description**, **Company Size**, **Industry**, and **Headquarters**.
* **Output:** `prospects_processed.csv` (rich dataset ready for AI).
* **Safety:** Implements human-like random delays (7-12 seconds) and anti-detection techniques.

---

## 🛠️ Setup and Execution

### Prerequisites

1.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Browser Driver:** Ensure you have the Chrome browser installed. Selenium 4 automatically handles the necessary Chrome Driver installation.

### Configuration (`.env` File)

Create a file named **`.env`** in the root directory and fill in your LinkedIn credentials and search parameters:

```env
# LinkedIn Account Credentials
LINKEDIN_USERNAME="your_email@example.com"
LINKEDIN_PASSWORD="your_password"

# --- PHASE 1 CONFIGURATION ---
SEARCH_KEYWORD="Software House"
GEO_IDS='["103350119", "102890719"]'
PHASE1_OUTPUT_FILE="prospects_raw.csv"

# --- PHASE 2 CONFIGURATION ---
PHASE2_INPUT_FILE="prospects_raw.csv"
PHASE2_OUTPUT_FILE="prospects_processed.csv"
