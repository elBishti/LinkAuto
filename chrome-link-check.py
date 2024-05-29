import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import requests
import re
import csv
import logging

# Set up the driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Set up the logger
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('This will get logged to a file')


# Create a lock
lock = Lock()


# Kolumn 1: Ligger länken live? Dvs. statuskod 200
# Kolumn 2: Innehåller länken RÄTT ankartext?
# Kolumn 3: Innehåller länken RÄTT URL (kundens URL)?
# Kolumn 4: Är länken indexerad på Google?
# Kolumn 5: Vilka rel attribut har länken (nofollow, sponsored)?
# Kolumn 6: Hur många utgående länkar (ej interna) finns på sidan?


# Function that checks if website is running and contains the anchor text
def check_website(driver, url, to_url, anchor):
    # Validate URLs
    if not urlparse(url).scheme or not urlparse(to_url).scheme:
        print("Invalid URL")
        return "Not Live", "Not Checked", "Not Checked", "Not Checked", "Not Checked", 0

    try:
        # Check if the link is live
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return response.status_code, "Not Checked", "Not Checked", "Not Checked", "Not Checked", 0
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while checking if the link is live: {e}")
        return "Not Live", "Not Checked", "Not Checked", "Not Checked", "Not Checked", 0

    with lock:
        driver = None
        try:
            # 2. Check if the anchor text is present
            driver = webdriver.Chrome(service=service)
            driver.get(url)

            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            anchor = re.sub(r'[^\w\såäöÅÄÖ.-]', '', anchor)
            anchor_words = re.split(r'\s|-', anchor.lower())
            found_anchor = False
            outgoing_links = 0

            for link in soup.find_all('a'):
                href = link.get('href')
                if href is None:
                    continue

                absolute_url = urljoin(url, href)
                if not absolute_url.startswith(("http://", "https://")):
                    absolute_url = 'http://' + absolute_url


                link_text = link.get_text().strip().lower()
                link_words = link_text.split()
                if all(word in link_words for word in anchor_words):
                    found_anchor = True
                    found_anchor_text = link_text


                    # 3. Check if the correct To URL is present
                    if absolute_url == to_url:
                        correct_link = "Correct Link"
                    else:
                        correct_link = absolute_url


                    # 5. Check the rel attributes of the link
                    rel_attributes = link.get('rel')
                    if rel_attributes is None:
                        rel_attributes = "None"
                    else:
                        rel_attributes = ", ".join(rel_attributes)
                if href and not href.startswith("/") and root_url not in href:
                    outgoing_links += 1
            if not found_anchor:
                found_anchor_text = "Not Found"
                correct_link = "Not Checked"
                rel_attributes = "Not Checked"
        except Exception as e:
            print(f"An error occurred while checking the anchor text: {e}")
            found_anchor_text = "Not Checked"
            correct_link = "Not Checked"
            rel_attributes = "Not Checked"
            outgoing_links = 0
        
        finally:
            if driver is not None:
                driver.quit()

    try:
        # 4. Check if the link is indexed on Google
        google_search_url = f"https://www.google.com/search?q=site:{url}"
        response = requests.get(google_search_url)
        if url in response.text:
            indexed = "Indexed"
        else:
            indexed = "Not Indexed"
    except Exception as e:
        print(f"An error occurred while checking if the link is indexed on Google: {e}")
        indexed = "Not Checked"

    return "Live", found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed

# Function to check a single row of the DataFrame
def check_row(index, row):
    if pd.isnull(row['URL']) or pd.isnull(row['Ankartext']):
        print("Missing Information")
        return index, "Missing Information", "Not Checked", "Not Checked", "Not Checked", "Not Checked", 0

    # Check the website
    live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed = check_website(driver, row['URL'], row['To URL'], row['Ankartext'])

    return index, live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed

# Path
df = pd.read_csv('data/test.csv', encoding='ISO-8859-1', on_bad_lines='warn')

# Create new columns in the DataFrame
df["Live Status"] = ""
df["Found Anchor Text"] = ""
df["Correct Link"] = ""
df["Indexed"] = ""
df["Rel Attributes"] = ""
df["Outgoing Links"] = ""

# Create a ThreadPoolExecutor
with ThreadPoolExecutor() as executor:
    # Use the executor to run check_row in parallel for each row in the DataFrame
    results = list(executor.map(check_row, df.index, df.to_dict('records')))

# Assign the results to the new columns
for result in results:
    index, live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed = result
    df.at[index, "Live Status"] = live_status
    df.at[index, "Found Anchor Text"] = found_anchor_text
    df.at[index, "Correct Link"] = correct_link
    df.at[index, "Indexed"] = indexed
    df.at[index, "Rel Attributes"] = rel_attributes
    df.at[index, "Outgoing Links"] = outgoing_links

    print(live_status, found_anchor_text, correct_link, indexed, rel_attributes, outgoing_links)

# Save the DataFrame to a CSV file
df.to_csv('data/test.csv', index=False)

driver.quit()
