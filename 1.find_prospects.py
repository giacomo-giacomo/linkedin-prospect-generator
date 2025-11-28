import time
import random
import csv
import json
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import dotenv_values # Import per .env
from colorama import Fore, Style, init # Import per l'output colorato

# Initialize Colorama for cross-platform terminal colors
init(autoreset=True) 

# Load configuration from .env file
CONFIG = dotenv_values(".env")

# --- CONFIGURATION FROM .ENV ---
USERNAME = CONFIG.get("LINKEDIN_USERNAME")
PASSWORD = CONFIG.get("LINKEDIN_PASSWORD")
KEYWORD = CONFIG.get("SEARCH_KEYWORD")
# Evaluate GEO_IDS as a list, as it's saved as a string in .env
try:
    GEO_IDS = json.loads(CONFIG.get("GEO_IDS", "[]"))
except (json.JSONDecodeError, TypeError):
    GEO_IDS = []
    print(f"{Fore.RED}ERROR: Invalid GEO_IDS format in .env file. Using empty list.")
OUTPUT_FILENAME = CONFIG.get("PHASE1_OUTPUT_FILE")

# ----------------------

def display_results(results_count, filename, phase):
    """Displays a colored, formatted screen with extraction summary."""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}✨ PHASE {phase} EXTRACTION COMPLETED! ✨")
    print(f"{Fore.CYAN}{'='*60}")
    
    if results_count > 0:
        print(f"{Fore.GREEN}✅ SUCCESS:")
        print(f"   {Fore.WHITE}Found and saved {Fore.YELLOW}{Style.BRIGHT}{results_count} company URLs.")
        print(f"   {Fore.WHITE}Data saved to: {Fore.CYAN}{Style.BRIGHT}{filename}")
    else:
        print(f"{Fore.RED}❌ FAILURE:")
        print(f"   {Fore.WHITE}No company URLs were found. Check your keywords and login status.")
        
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

def build_search_url(keyword, geo_ids):
    """Constructs the company search URL with geographic filters."""
    base_url = "https://www.linkedin.com/search/results/companies/"
    geo_json = json.dumps(geo_ids)
    geo_encoded = urllib.parse.quote(geo_json)
    final_url = f"{base_url}?keywords={keyword}&companyHqGeo={geo_encoded}&origin=FACETED_SEARCH"
    return final_url

def extract_companies(driver, search_url):
    """Extracts company URLs and names from search results."""
    print(f"{Fore.MAGENTA}🔵 Starting search on: {search_url}")
    driver.get(search_url)
    time.sleep(random.uniform(4, 7)) 
    
    results = []
    seen_urls = set()
    
    try:
        # Scroll to load results (lazy loading)
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.5, 2.5))
            
        # Robust XPATH: searches for all <a> tags containing /company/ and not /search
        xpath_selector = "//a[contains(@href, '/company/') and not(contains(@href, '/search'))]"
        links = driver.find_elements(By.XPATH, xpath_selector)
        
        print(f"{Fore.GREEN}🔎 Found potential company links: {len(links)}")

        for link in links:
            url = link.get_attribute("href")
            name = link.text.split("\n")[0].strip()
            
            if url and name:
                clean_url = url.split("?")[0]
                
                if "/company/" in clean_url and clean_url not in seen_urls:
                    seen_urls.add(clean_url)
                    results.append({"Name": name, "URL": clean_url})
                    
    except Exception as e:
        print(f"{Fore.RED}❌ Phase 1 extraction error: {e}")
        
    return results

def save_csv(data, filename):
    """Saves the extracted data to a CSV file."""
    if not data:
        return
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

# --- PHASE 1 EXECUTION ---
if __name__ == "__main__":
    driver = setup_driver()
    
    linkedin_login(driver, USERNAME, PASSWORD)
    
    target_url = build_search_url(KEYWORD, GEO_IDS)
    
    companies = extract_companies(driver, target_url)
    
    save_csv(companies, OUTPUT_FILENAME)
    
    # Display results and finalize
    display_results(len(companies), OUTPUT_FILENAME, 1)
    
    driver.quit()
