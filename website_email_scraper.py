import requests
from bs4 import BeautifulSoup
import re

def scrape_website_emails(url):
    """
    Extract email addresses from a webpage.
    Args:
        url: The URL of the webpage to scrape
    Returns:
        list: List of email addresses found on the page
    """
    try:
        # Get the webpage content
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all text content
        text_content = soup.get_text()
        
        # Find all email addresses in the text
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text_content)
        
        # Also look for mailto: links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('mailto:'):
                email = href[7:]  # Remove 'mailto:' prefix
                if '@' in email:
                    emails.append(email)
        
        # Clean and deduplicate emails
        emails = list(set(email.lower() for email in emails))
        
        return emails
        
    except Exception as e:
        print(f"Error scraping emails from {url}: {str(e)}")
        return []