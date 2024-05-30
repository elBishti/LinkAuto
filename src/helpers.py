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
    # Remove all characters that are not alphanumeric, underscore, or whitespace
    # Convert the text to lowercase
    return re.sub(r'[^a-zA-Z0-9_åäöÅÄÖ\s]', '', text).strip().lower()

# Function to check if the URL is live  
def check_link_live(url, headers):
    try:
        # Send a GET request to the URL
        response = requests.get(url, timeout=10, headers=headers)
        # If the HTTP status code is not in the 200-299 range, the URL is not live
        if not 200 <= response.status_code < 300:
            print(f"HTTP status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        # If a request exception occurs, print the error and return it
        print(f"Error: {e}")
        return str(e)
    # If no exceptions occurred and the status code is in the 200-299 range, the URL is live
    return True

# Function to get the page source using Selenium
def get_page_source(url):
    # Set up the Chrome WebDriver service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    # Navigate to the URL
    driver.get(url)
    # Wait until the page has fully loaded
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
    # Get the page source
    page_source = driver.page_source
    # Close the browser
    driver.quit()
    # Return the page source
    return page_source

# Function to check the anchor text & correct link & rel attributes & outgoing links
def check_anchor_text(soup, anchor, to_url, url):
    try:
        # Convert the anchor text to UTF-8 to handle special characters
        anchor = anchor.encode('utf-8').decode('utf-8')
        # Clean the anchor text and split it into words
        anchor_words = set(clean_text(anchor).split())
        # Initialize variables to keep track of whether the anchor text and URL have been found
        found_anchor = False
        found_anchor_text = None
        found_to_url = False
        # Initialize variables to keep track of the last URL checked and the number of outgoing links
        last_url_checked = None
        outgoing_links = 0
        # Initialize variables to keep track of the correct link and its rel attributes
        correct_link = "None"
        rel_attributes = "Not Found"

        # Parse the root URL and the target URL
        root_url = urlparse(url).netloc
        to_url_parsed = urlparse(to_url)
        # Normalize the target URL by removing 'www.' and trailing slashes
        to_url_normalized = to_url_parsed.netloc.replace('www.', '') + to_url_parsed.path.rstrip('/')

        # Loop over all 'a' elements in the soup object
        for link in soup.find_all('a'):
            # Get the href attribute of the link
            href = link.get('href')
            # If the href attribute is None, skip this link
            if href is None:
                continue

            # Convert the href attribute to an absolute URL
            absolute_url = urljoin(url, href)
            # If the absolute URL doesn't start with 'http://' or 'https://', add 'http://' to the start
            if not absolute_url.startswith(("http://", "https://")):
                absolute_url = 'http://' + absolute_url

            # If the absolute URL is a mailto link, skip this link
            if "mailto:" in absolute_url:
                continue

            # If the absolute URL is on the same domain as the root URL, skip this link
            if urlparse(absolute_url).netloc == root_url:
                continue

            # Clean the link text and split it into words
            link_text = clean_text(link.get_text())
            link_words = set(link_text.split())

            # If the anchor words are a subset of the link words, the anchor text has been found
            if anchor_words.issubset(link_words):
                found_anchor = True
                found_anchor_text = link_text

            # Normalize the absolute URL by removing 'www.' and trailing slashes
            absolute_url_parsed = urlparse(absolute_url)
            absolute_url_normalized = absolute_url_parsed.netloc.replace('www.', '') + absolute_url_parsed.path.rstrip('/')
            # Update the last URL checked
            last_url_checked = absolute_url

            # If the normalized absolute URL matches the normalized target URL, the correct link has been found
            if absolute_url_normalized == to_url_normalized:
                correct_link = "Correct"
                found_to_url = True
            # If the correct link hasn't been found yet and the absolute URL is on a different domain than the root URL, update the correct link
            elif correct_link == "None" and urlparse(absolute_url).netloc != root_url:
                correct_link = absolute_url

            # Get the rel attributes of the link
            rel_attributes = link.get('rel')
            # If the rel attributes are None, set them to "None"
            if rel_attributes is None:
                rel_attributes = "None"
            else:
                # Otherwise, join the rel attributes into a string separated by commas
                rel_attributes = ", ".join(rel_attributes)

            # If the href attribute is not a relative URL and doesn't contain the root URL, increment the number of outgoing links
            if href and not href.startswith("/") and root_url not in href:
                outgoing_links += 1

        # If the target URL wasn't found, set the correct link to the last URL checked
        if not found_to_url:
            correct_link = last_url_checked

        # Return the results
        return found_anchor, found_anchor_text, correct_link, rel_attributes, outgoing_links

    except Exception as e:
        # If an exception occurs, print the error and raise the exception
        print(f"An error occurred while checking the anchor text: {e}")
        raise

# Function to check if a given URL is indexed by Google
def check_google_index(url, headers):
    # Construct the Google search URL by appending the URL to the standard Google search string
    google_search_url = f"https://www.google.com/search?q=site:{url}"
    try:
        # Send a GET request to the Google search URL with the provided headers
        response = requests.get(google_search_url, headers=headers)
        # If the URL is found in the response text, it means that the URL is indexed by Google
        if url in response.text:
            return "Indexed"
    except Exception as e:
        # If an exception occurs (e.g., a network error), log the error and return "Not Checked"
        logging.error(f"An error occurred while checking if the link is indexed on Google: {e}")
        return "Not Checked"
    # If the URL is not found in the response text, it means that the URL is not indexed by Google
    return "Not Indexed"