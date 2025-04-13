import argparse
import logging
import os
import pandas as pd
from dataclasses import dataclass, asdict, field
from multiprocessing import Pool, cpu_count
from playwright.sync_api import sync_playwright
from tqdm import tqdm
from datetime import datetime
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

@dataclass
class Business:
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None

@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list)
    save_at: str = "output"

    def dataframe(self):
        return pd.json_normalize((asdict(b) for b in self.business_list), sep="_")

    def save_to_csv(self, filename):
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_csv(f"{self.save_at}/{filename}.csv", index=False)

    def save_to_excel(self, filename):
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_excel(f"{self.save_at}/{filename}.xlsx", index=False)

def load_zipcodes(csv_path="us_zipcodes.csv", filter_zips=None):
    df = pd.read_csv(csv_path)
    if not all(col in df.columns for col in ["zip", "lat", "lng"]):
        raise ValueError("CSV must have 'zip', 'lat', and 'lng' columns")

    if filter_zips:
        filter_zips = [str(z) for z in filter_zips]
        df = df[df["zip"].astype(str).isin(filter_zips)]

    return [(row["zip"], row["lat"], row["lng"]) for _, row in df.iterrows()]

def scroll_and_collect_links(search_for, lat, lng):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        url = f"https://www.google.com/maps/search/{search_for}/@{lat},{lng},14z"
        page.goto(url, wait_until="domcontentloaded", timeout=10000)
        page.locator('//input[@id="searchboxinput"]').fill(search_for)
        page.keyboard.press("Enter")
        try:
            page.wait_for_selector('div[role="feed"]', timeout=8000)
        except:
            logging.warning("No feed found on page. Skipping...")
            browser.close()
            return []

        list_end = page.locator('span.HlvSq', has_text="You've reached the end of the list.")

        start_time = time.time()
        timeout = 60
        while not list_end.is_visible():
            page.evaluate("""
            const feed = document.querySelector('div[role="feed"]');
            if (feed) feed.scrollTop = feed.scrollHeight;
            """)
            if list_end.is_visible():
                break
            if time.time() - start_time > timeout:
                logging.info("Breaking out of scroll loop after 60 seconds.")
                break

        listing_elements = page.locator('a.hfpxzc').all()
        links = [el.get_attribute("href") for el in listing_elements if el.get_attribute("href")]
        logging.info(f"Collected {len(links)} links.")
        browser.close()
        return links

def scrape_single_link(link):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-infobars"
        ])
        context = browser.new_context()
        page = context.new_page()
        url = link if link.startswith("http") else f"https://www.google.com{link}"
        business = Business()

        try:
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            name_xpath = '//h1[contains(@class, "DUwDvf")]'
            address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "Io6YTe")]'
            website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "Io6YTe")]'
            phone_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "Io6YTe")]'

            try: business.name = page.locator(name_xpath).inner_text(timeout=2000)
            except: pass
            try: business.address = page.locator(address_xpath).inner_text(timeout=2000)
            except: pass
            try: business.website = page.locator(website_xpath).inner_text(timeout=2000)
            except: pass
            try: business.phone_number = page.locator(phone_xpath).inner_text(timeout=2000)
            except: pass

        except Exception as e:
            logging.error(f"Error loading {url}: {e}")
        finally:
            context.close()
            browser.close()

        return asdict(business) if business.name else None

def main(search_query, user_zips=None):
    zip_coords = load_zipcodes("us_zipcodes.csv", filter_zips=user_zips)
    all_links = set()

    for i, (zipcode, lat, lng) in enumerate(zip_coords):
        logging.info(f"[{i+1}/{len(zip_coords)}] Searching around ZIP={zipcode} (lat={lat}, lng={lng})")
        links = scroll_and_collect_links(search_query, lat, lng)
        all_links.update(links)

    logging.info(f"Total unique links collected: {len(all_links)}")

    num_workers = min(cpu_count(), 10)
    business_list = BusinessList()

    with Pool(processes=num_workers) as pool:
        for result in tqdm(pool.imap_unordered(scrape_single_link, list(all_links)), total=len(all_links)):
            if result:
                business_list.business_list.append(Business(**result))

    # Deduplicate
    seen = set()
    unique_businesses = []
    for b in business_list.business_list:
        key = (b.name, b.address)
        if key not in seen:
            seen.add(key)
            unique_businesses.append(b)
    business_list.business_list = unique_businesses

    business_list.save_to_csv("google_maps_zipcode_data")
    logging.info("Scraping complete. Data saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str, required=True, help="Search keyword (e.g., 'dentist')")
    parser.add_argument("--zipcodes", type=str, nargs="*", help="Optional list of ZIP codes (e.g., 92101 90210)")
    args = parser.parse_args()

    start = datetime.now()
    main(args.search, args.zipcodes)
    end = datetime.now()
    logging.info(f"Scraping completed in {end - start}")