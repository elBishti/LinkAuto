import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re


# Set up the driver
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)

# Function that checks if website is running and contains the anchor text
def check_website(url, anchor):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        anchor = re.sub(r'[^\w\såäöÅÄÖ]', '', anchor)
        anchor_words = anchor.lower().split()
        found_anchor = False
        for link in soup.find_all('a'):
            link_text = link.get_text().strip().lower()
            if all(word in link_text for word in anchor_words):
                found_anchor = True
                break
        if found_anchor:
            return "Found ALL"
        else:
            return "Found URL"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Not Found"

# Path

# CHANGE THE PATH TO THE LOCATION OF THE CSV FILE
df = pd.read_csv('data/test.csv')

# Add a column to the dataframe to store the result
df['Result'] = False

# Iterate over the rows of the dataframe and print the result
for index, row in df.iterrows():

    if pd.isnull(row['URL']) or pd.isnull(row['Ankartext']):
        print("Missing Information")
        continue

    result = check_website(row['URL'], row['Ankartext'])
    df.at[index, 'Result'] = result
    print(result)

df.to_csv('data/test.csv', index=False)

driver.quit()