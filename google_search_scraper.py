import os
import sys
import time
import random
import re
from urllib.parse import quote, unquote

# Add paths to find the Playwright module
sys.path.append(os.path.expanduser("~/.local/lib/python3.13/site-packages"))
sys.path.append(os.path.expanduser("~/AppData/Roaming/Python/Python313/site-packages"))

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright module not found. Installing it now...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.sync_api import sync_playwright

# Check if browser is installed
try:
    import subprocess
    result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"], 
                           capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print("Warning: Unable to install browser automatically. You may need to run:")
        print("python -m playwright install chromium")
except Exception as e:
    print(f"Warning: {str(e)}")
    print("If browser launch fails, manually run: python -m playwright install chromium")

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

#from utils.email_utils import clean_emails
from website_email_scraper import scrape_website_emails
#from storage.database import store_data

def get_google_search_results(query, num_results=10, headless=True):
    """
    Get URLs from Google search results using Playwright.
    Args:
        query: Search query
        num_results: Number of results to fetch
        headless: Whether to run browser in headless mode
    Returns:
        list: List of URLs from search results
    """
    with sync_playwright() as p:
        # Launch browser with various options to avoid detection
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-dev-shm-usage'
            ]
        )
        
        # Create a context with specific viewport and locale
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US'
        )
        
        # Configure context to mimic human behavior
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)
        
        page = context.new_page()
        
        #emulate human like behavior with random timing
        page.set_default_timeout(60000)  # Longer timeout
        
        try:
            # Format the search query
            encoded_query = quote(f"{query} email contact")
            
            # Try different Google domains
            google_domains = [
                'https://www.google.com',
                'https://www.google.co.uk',
                'https://www.google.ca',
                'https://www.google.com.au',
                'https://www.google.de'
            ]
            
            base_url = random.choice(google_domains)
            url = f'{base_url}/search?q={encoded_query}&num={num_results}&hl=en'
            
            print(f"Searching: {url}")
            
            # Navigate to the URL with random timing
            page.goto(url, wait_until="networkidle")
            
            # Add random delay to mimic human behavior
            time.sleep(random.uniform(2, 4))
            
            # Check for captcha
            if page.query_selector('form#captcha-form, img[alt*="captcha"], div#recaptcha'):
                print("Captcha detected! Please solve it manually...")
                if not headless:
                    print("After solving the captcha, press Enter in the terminal...")
                    input()
                else:
                    print("Headless mode is enabled, cannot solve captcha...")
                    return []
            
            # Mimic human scrolling behavior
            for _ in range(3):
                page.mouse.move(
                    random.randint(100, 500),
                    random.randint(100, 500)
                )
                page.mouse.wheel(0, random.randint(300, 700))
                time.sleep(random.uniform(1, 2))
            
            # Wait for search results to load
            page.wait_for_selector('div[data-sokoban-container], div.g, div.tF2Cxc, div.yuRUbf, div[class*="g"]', 
                                  state='visible', timeout=10000)
            
            # Try various XPaths to get result links (more robust than CSS selectors)
            xpath_selectors = [
                "//div[@class='g' or contains(@class, 'g')]//a[not(contains(@href, 'google.com'))]",
                "//div[contains(@class, 'yuRUbf') or contains(@class, 'tF2Cxc')]//a[not(contains(@href, 'google.com'))]",
                "//h3[contains(@class, 'LC20lb')]/parent::*//a[not(contains(@href, 'google.com'))]",
                "//div[contains(@class, 'DKV0Md') or contains(@class, 'MjjYud')]//a[not(contains(@href, 'google.com'))]",
                "//div[@data-sokoban-container]//a[not(contains(@href, 'google.com'))]",
                "//a[contains(@href, '/url?') and not(contains(@href, 'google.com'))]"
            ]
            
            urls = []
            
            for xpath in xpath_selectors:
                elements = page.query_selector_all(xpath)
                for element in elements:
                    href = element.get_attribute('href')
                    if href and 'google.com' not in href:
                        # Parse Google's redirect URLs
                        if '/url?q=' in href:
                            parts = href.split('/url?q=')
                            if len(parts) > 1:
                                actual_url = parts[1].split('&')[0]
                                href = unquote(actual_url)
                        urls.append(href)
            
            # Clean and filter URLs
            cleaned_urls = []
            for url in urls:
                # Remove any URL parameters
                url = url.split('?')[0]
                # Remove trailing slashes
                url = url.rstrip('/')
                # Skip common non-result URLs
                if not any(x in url.lower() for x in ['google.com', 'youtube.com', 'facebook.com', 'twitter.com']):
                    cleaned_urls.append(url)
            
            # Remove duplicates while preserving order
            cleaned_urls = list(dict.fromkeys(cleaned_urls))
            
            if cleaned_urls:
                print(f"Found {len(cleaned_urls)} unique URLs")
                return cleaned_urls[:num_results]
            else:
                print("No URLs found in the search results")
                return []
                
        except Exception as e:
            print(f"Error getting Google search results: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            browser.close()

def scrape_google_search(query, num_results=10, headless=True):
    """
    Scrape emails from websites found in Google search results.
    Args:
        query: Search query
        num_results: Number of results to process
        headless: Whether to run browser in headless mode
    Returns:
        dict: Dictionary containing results for each website
    """
    print(f"\nSearching Google for: {query}")
    
    # Get URLs from search results
    urls = get_google_search_results(query, num_results, headless)
    
    if not urls:
        print("No search results found.")
        return {}
    
    results = {}
    
    # Process each URL
    for i, url in enumerate(urls, 1):
        print(f"\nProcessing website {i}/{len(urls)}: {url}")
        
        try:
            # Scrape emails from the website
            emails = scrape_website_emails(url)
            
            if emails:
                print(f"Found {len(emails)} emails on {url}")
                results[url] = emails
                
                # Store results in database
                store_data({
                    'url': url,
                    'emails': emails,
                    'timestamp': time.time()
                })
            else:
                print(f"No emails found on {url}")
                
            # Add a delay between requests to avoid rate limiting
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            continue
    
    return results

if __name__ == "__main__":
    try:
        # Check if headless mode is specified
        headless = True
        for arg in sys.argv:
            if arg.lower() == 'headless=false':
                headless = False
                sys.argv.remove(arg)
                break
        
        if len(sys.argv) > 1:
            # Get search query from command line arguments
            query = ' '.join(sys.argv[1:])
            
            # Get number of results from environment variable or use default
            num_results = int(os.getenv('NUM_RESULTS', '10'))
            
            # Run the search and scrape
            results = scrape_google_search(query, num_results, headless)
            
            # Print results
            print("\nSearch Results Summary:")
            print("-" * 50)
            for url, emails in results.items():
                print(f"\nWebsite: {url}")
                print(f"Emails found: {len(emails)}")
                for email in emails:
                    print(f"  - {email}")
                    
        else:
            print("Please provide a search query")
            print("Example: python google_playwright_scraper.py 'business emails in new york' headless=false")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 