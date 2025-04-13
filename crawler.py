import httplib2
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
import re
import time
from timeit import default_timer as timer
import sys
from tqdm import tqdm
import csv
from urllib.parse import urlparse
from datetime import datetime


def scrape_website_emails(url):
    """
    Crawl a homepage and its links (esp. contact pages) to extract emails.
    Uses Selenium to render dynamic content.
    Includes a tqdm progress bar for feedback.
    """
    # Make HTTP request to get initial HTML
    http = httplib2.Http()
    status, response = http.request(url)
    status_code = int(status.get("status", 0))
    
    if status_code not in [200, 201, 203]:
        raise Exception(f"Failed to fetch {url}: {status_code}")

    emails = set()
    all_links = set()
    contact_links = set()

    # Extract links from homepage
    for link in BeautifulSoup(response, 'html.parser', parse_only=SoupStrainer('a')):
        if link.has_attr('href'):
            href = link['href']
            all_links.add(href)
            if 'contact' in href.lower():
                contact_links.add(href)

    # Always crawl homepage first
    crawl_links = {url}
    # Prioritize contact links
    crawl_links.update(urljoin(url, link) for link in contact_links)
    # Then add other internal links
    crawl_links.update(urljoin(url, link) for link in all_links if link.startswith('/') or link.startswith(url))
    
    crawl_links = list(crawl_links)  # Convert to list for tqdm

    print(f"[INFO] Starting crawl of {len(crawl_links)} pages for {url}", flush=True)

    # Set up headless Selenium
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')

    driver = webdriver.Chrome(options=options)

    # Email regex
    email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    
    for i, link in enumerate(crawl_links, 1):
        print(f"[{i}/{len(crawl_links)}] Scraping: {link}", flush=True)
        try:
            driver.get(link)
            time.sleep(0.2)
            html = driver.page_source
            found_emails = email_pattern.findall(html)
            found_emails = [email for email in found_emails if not email.lower().endswith('.png')]
            emails.update(found_emails)
        except Exception as e:
            print(f"[!] Error loading {link}: {e}", flush=True)

    driver.quit()
    return list(emails)

# Run script
if __name__ == "__main__":    
    if len(sys.argv) < 2:
        print("Usage: python3 crawler.py <site_url>", flush=True)
        sys.exit(1)

    site_url = sys.argv[1]
    if not site_url.startswith("http"):
        site_url = "https://" + site_url

    email_list = scrape_website_emails(site_url)
    print("Emails found:", email_list, flush=True)

    parsed_url = urlparse(site_url)
    domain = parsed_url.netloc.replace("www.", "").replace(".", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/emails_{domain}_{timestamp}.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Email"])
        for email in email_list:
            writer.writerow([email])

    print(f"[INFO] Emails saved to: {filename}", flush=True)

