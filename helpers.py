from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urlparse, urljoin
import requests
import re
import logging


# Function to clean the text
def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9_åäöÅÄÖ\s]', '', text).strip().lower()

# Function to check if the URL is live  
def check_link_live(url, headers):
    try:
        response = requests.get(url, timeout=10, headers=headers)
        if not 200 <= response.status_code < 300:
            print(f"HTTP status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return str(e)
    return True

# Function to get the page source using Selenium
def get_page_source(url):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
    page_source = driver.page_source
    driver.quit()
    return page_source

def check_anchor_text(soup, anchor, to_url, url):
    try:
        anchor = anchor.encode('utf-8').decode('utf-8')
        anchor_words = set(clean_text(anchor).split())
        found_anchor = False
        found_anchor_text = None
        found_to_url = False
        last_url_checked = None
        outgoing_links = 0
        correct_link = "None"
        rel_attributes = "Not Found"

        root_url = urlparse(url).netloc
        to_url_parsed = urlparse(to_url)
        to_url_normalized = to_url_parsed.netloc.replace('www.', '') + to_url_parsed.path.rstrip('/')


        for link in soup.find_all('a'):
            href = link.get('href')
            if href is None:
                continue

            absolute_url = urljoin(url, href)
            if not absolute_url.startswith(("http://", "https://")):
                absolute_url = 'http://' + absolute_url

            if "mailto:" in absolute_url:
                continue

            if urlparse(absolute_url).netloc == root_url:
                continue

            link_text = clean_text(link.get_text())
            link_words = set(link_text.split())

            if anchor_words.issubset(link_words):
                found_anchor = True
                found_anchor_text = link_text


            absolute_url_parsed = urlparse(absolute_url)
            absolute_url_normalized = absolute_url_parsed.netloc.replace('www.', '') + absolute_url_parsed.path.rstrip('/')
            last_url_checked = absolute_url

            if absolute_url_normalized == to_url_normalized:
                correct_link = "Correct"
                found_to_url = True
            elif correct_link == "None" and urlparse(absolute_url).netloc != root_url:
                correct_link = absolute_url

            rel_attributes = link.get('rel')
            if rel_attributes is None:
                rel_attributes = "None"
            else:
                rel_attributes = ", ".join(rel_attributes)

            if href and not href.startswith("/") and root_url not in href:
                outgoing_links += 1
            
        if not found_to_url:
            correct_link = last_url_checked

        return found_anchor, found_anchor_text, correct_link, rel_attributes, outgoing_links
    
    except Exception as e:
        print(f"An error occurred while checking the anchor text: {e}")
        raise

# Function to check if the link is indexed on Google
def check_google_index(url, headers):
    google_search_url = f"https://www.google.com/search?q=site:{url}"
    try:
        response = requests.get(google_search_url, headers=headers)
        if url in response.text:
            return "Indexed"
    except Exception as e:
        logging.error(f"An error occurred while checking if the link is indexed on Google: {e}")
        return "Not Checked"
    return "Not Indexed"