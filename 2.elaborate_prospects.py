import time
import random
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import dotenv_values # Import per .env
from colorama import Fore, Style, init # Import per l'output colorato

# Initialize Colorama
init(autoreset=True) 

# Load configuration from .env file
CONFIG = dotenv_values(".env")

# --- CONFIGURATION FROM .ENV ---
USERNAME = CONFIG.get("LINKEDIN_USERNAME")
PASSWORD = CONFIG.get("LINKEDIN_PASSWORD")
INPUT_FILENAME = CONFIG.get("PHASE2_INPUT_FILE")
OUTPUT_FILENAME = CONFIG.get("PHASE2_OUTPUT_FILE")

# Map to search for both Italian and English labels (more robust)
DETAIL_LABELS = {
    "Industry": ["Settore", "Industry"],
    "Size": ["Dimensioni azienda", "Company size"],
    "Headquarters": ["Sede principale", "Headquarters"]
}

# --- BASE FUNCTIONS (Adapted for .env) ---

def display_results(results_count, filename, phase):
    """Displays a colored, formatted screen with extraction summary."""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}✨ PHASE {phase} EXTRACTION COMPLETED! ✨")
    print(f"{Fore.CYAN}{'='*60}")
    
    if results_count > 0:
        print(f"{Fore.GREEN}✅ SUCCESS:")
        print(f"   {Fore.WHITE}Processed {Fore.YELLOW}{Style.BRIGHT}{results_count} company pages.")
        print(f"   {Fore.WHITE}Detailed data saved to: {Fore.CYAN}{Style.BRIGHT}{filename}")
        print(f"   {Fore.WHITE}Ready for LLM Cold Outreach!")
    else:
        print(f"{Fore.RED}❌ FAILURE:")
        print(f"   {Fore.WHITE}No URLs were found in the input file ({INPUT_FILENAME}).")
        
    print(f"{Fore.CYAN}{'='*60}")

def setup_driver():
    """Configures the Chrome driver and masks automation flags."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    return driver

def linkedin_login(driver, user, pwd):
    """Performs login on LinkedIn."""
    print(f"{Fore.BLUE}🔵 Logging in...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(random.uniform(2, 4))
    
    try:
        driver.find_element(By.ID, "username").send_keys(user)
        time.sleep(random.uniform(1, 2))
        driver.find_element(By.ID, "password").send_keys(pwd)
        time.sleep(random.uniform(1, 2))
        driver.find_element(By.ID, "password").send_keys(Keys.RETURN) 
        
        input(f"\n{Fore.YELLOW}⚠️  Solve any CAPTCHAs/Verifications. Press ENTER here to continue when you are on the LinkedIn homepage...")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Login error: {e}")
        input(f"{Fore.YELLOW}Attempting manual pause. Press ENTER after successful login...")


def load_urls_from_csv(filename):
    """Loads the list of URLs from the Phase 1 CSV file."""
    try:
        df = pd.read_csv(filename)
        urls = df['URL'].tolist()
        print(f"{Fore.GREEN}✅ Loaded {len(urls)} URLs from '{filename}' for detailed analysis.")
        return urls
    except FileNotFoundError:
        print(f"{Fore.RED}❌ Error: Input file '{filename}' not found. Run Phase 1 first.")
        return []
    except KeyError:
        print(f"{Fore.RED}❌ Error: 'URL' column not found in '{filename}'. Check column names.")
        return []

# --- DETAIL EXTRACTION FUNCTIONS (PHASE 2) ---

def get_detail_from_list(driver, label_texts):
    """
    Finds a specific detail (e.g., Company Size) by searching among the provided labels.
    Uses a robust XPATH targeting the <h3> text.
    """
    for label in label_texts:
        try:
            # XPATH: Finds the <h3> containing the label text, goes to its parent <dt>, and gets the next sibling <dd>.
            xpath = f'//h3[contains(text(), "{label}")]/parent::dt/following-sibling::dd[1]'
            element = driver.find_element(By.XPATH, xpath)
            return element.text.strip()
        except Exception:
            # Continues searching with the other labels (e.g., English fallback)
            continue
            
    return "N/A"

def scrape_company_about(driver, company_url):
    """Navigates to the company's /about/ page and extracts required details."""
    print(f"\n{Fore.MAGENTA}🔍 Analyzing page: {company_url}")
    
    # URL clean-up logic
    clean_url = company_url.split("/?")[0].rstrip('/')
    final_url = clean_url + "/about/" if not clean_url.endswith("/about") else clean_url
        
    driver.get(final_url)
    time.sleep(random.uniform(7, 12)) 

    data = {"URL": final_url} # Start with URL for joining/tracking
    
    try:
        # 1. Name and Tagline
        name_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1")))
        data["Name"] = name_element.text.strip()
        
        try:
            tagline_element = driver.find_element(By.XPATH, "//div[contains(@class, 'top-card')]//p[contains(@class, 'org-top-card-summary__tagline')]")
            data["Tagline"] = tagline_element.text.strip()
        except:
            data["Tagline"] = "N/A"

        # 2. Overview / Long Description (UPDATED SELECTOR)
        try:
            # Targets the <p> with the 'break-words' class inside the main about section
            overview_xpath = '//section[contains(@class, "org-about-module")]//p[contains(@class, "break-words")]'
            overview_element = driver.find_element(By.XPATH, overview_xpath)
            
            # Click on "Show more" if present
            try:
                show_more_button = overview_element.find_element(By.XPATH, './/button[contains(text(), "Mostra altro") or contains(text(), "Show more")]')
                show_more_button.click()
                time.sleep(random.uniform(1, 2))
            except:
                pass 
            
            data["Overview"] = overview_element.text.strip()
            
        except Exception:
            data["Overview"] = "N/A"

        # 3. Detail Extraction (Using robust map)
        data["Industry"] = get_detail_from_list(driver, DETAIL_LABELS["Industry"])
        data["Size"] = get_detail_from_list(driver, DETAIL_LABELS["Size"])
        data["Headquarters"] = get_detail_from_list(driver, DETAIL_LABELS["Headquarters"])
        
        print(f"   {Fore.GREEN}Extracted {data['Name']} | Size: {data['Size']}")
        
    except Exception as e:
        print(f"{Fore.RED}   ❌ Critical error during scrape of {final_url}: {e}")
        data = {"URL": final_url, "Name": "ERROR", "Tagline": "ERROR", "Overview": "ERROR", 
                "Industry": "ERROR", "Size": "ERROR", "Headquarters": "ERROR"}
        
    return data

def save_detailed_csv(data, filename):
    """Saves the detailed data to a CSV file."""
    if not data:
        return
    all_keys = list(data[0].keys())
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        writer.writerows(data)

# --- PHASE 2 EXECUTION ---
if __name__ == "__main__":
    
    urls_to_scrape = load_urls_from_csv(INPUT_FILENAME)
    
    if not urls_to_scrape:
        exit()
    
    driver = setup_driver()
    linkedin_login(driver, USERNAME, PASSWORD)
    
    detailed_results = []
    
    print(f"\n{Fore.CYAN}--- STARTING DETAILED SCRAPING (PHASE 2) ---")
    
    for url in urls_to_scrape:
        company_data = scrape_company_about(driver, url)
        detailed_results.append(company_data)
        
    save_detailed_csv(detailed_results, OUTPUT_FILENAME)
    
    # Display results and finalize
    display_results(len(urls_to_scrape), OUTPUT_FILENAME, 2)
    
    driver.quit()
