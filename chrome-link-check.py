import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import re

# Set up the driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)


# Kolumn 1: Ligger länken live? Dvs. statuskod 200
# Kolumn 2: Innehåller länken RÄTT ankartext?
# Kolumn 3: Innehåller länken RÄTT URL (kundens URL)?
# Kolumn 4: Är länken indexerad på Google?
# Kolumn 5: Vilka rel attribut har länken (nofollow, sponsored)?
# Kolumn 6: Hur många utgående länkar (ej interna) finns på sidan?

# Function that checks if website is running and contains the anchor text
def check_website(url, anchor):
    driver = None
    try:
        # Check if the link is live
        response = requests.get(url)
        if response.status_code != 200:
            return "Not Live", "Not Checked", "Not Checked", "Not Checked", "Not Checked", "Not Checked"

        driver = webdriver.Chrome(service=service)
        driver.get(url)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        anchor = re.sub(r'[^\w\såäöÅÄÖ-.]', '', anchor)
        anchor_words = anchor.lower().split()
        found_anchor = False
        status_message = "Not Found"
        for link in soup.find_all('a'):
            link_text = link.get_text().strip().lower()
            if all(word in link_text for word in anchor_words):
                found_anchor = True
                break
        
        if found_anchor:
            status_message = "Found ALL"
        else:
            status_message = "Found URL"

        # Placeholder for other checks
        right_url = "Not Checked"
        indexed = "Not Checked"
        rel_attributes = "Not Checked"
        outgoing_links = "Not Checked"

        return "Live", status_message, right_url, indexed, rel_attributes, outgoing_links
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Not Live", "Not Checked", "Not Checked", "Not Checked", "Not Checked", "Not Checked"
    finally:
        if driver:
            driver.quit()


# Path
df = pd.read_csv('data/test.csv')

# Add columns to the dataframe to store the results
df['Link Status'] = ""
df['Anchor Text'] = ""
df['Right URL'] = ""
df['Indexed'] = ""
df['Rel Attributes'] = ""
df['Outgoing Links'] = ""

# Iterate over the rows of the dataframe and print the result
for index, row in df.iterrows():

    if pd.isnull(row['URL']) or pd.isnull(row['Ankartext']):
        print("Missing Information")
        continue

    link_status, anchor_text, right_url, indexed, rel_attributes, outgoing_links = check_website(row['URL'], row['Ankartext'])
    df.at[index, 'Link Status'] = link_status
    df.at[index, 'Anchor Text'] = anchor_text
    df.at[index, 'Right URL'] = right_url
    df.at[index, 'Indexed'] = indexed
    df.at[index, 'Rel Attributes'] = rel_attributes
    df.at[index, 'Outgoing Links'] = outgoing_links
    print(link_status, anchor_text, right_url, indexed, rel_attributes, outgoing_links)

df.to_csv('data/test.csv', index=False)

driver.quit()