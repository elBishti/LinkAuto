import pandas as pd
import logging
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from helpers import check_link_live, get_page_source, check_anchor_text, check_google_index


class MissingInformationError(Exception):
    pass

# Function that checks if website is running and contains the anchor text
def main(url, to_url, anchor):
    if not urlparse(to_url).scheme:
        to_url = 'http://' + to_url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    time.sleep(1)

    status = check_link_live(url, headers)
    if status != True:
        return status, "Not Found", "Not Found", "Not Found", "Not Found", 0

    page_source = get_page_source(url)
    soup = BeautifulSoup(page_source, 'lxml')

    found_anchor, found_anchor_text, correct_link, rel_attributes, outgoing_links = check_anchor_text(soup, anchor, to_url, url)

    if not found_anchor:
        found_anchor_text = "Not Found"

    indexed = check_google_index(url, headers)

    return "Live", found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed


# Function to check a single row of the DataFrame
def check_row(index, row):
    try:
        if pd.isnull(row['URL']) or pd.isnull(row['Ankartext']):
            raise MissingInformationError("Missing Information")

        # Check the website
        live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed = main(row['URL'], row['To URL'], row['Ankartext'])
    except MissingInformationError as e:
        logging.error(f"An error occurred while checking the DataFrame: {e}")
        live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed = "Not Checked", "Not Checked", "Not Checked", "Not Checked", "Not Checked", 0
    except Exception as e:
        logging.error(f"An unexpected error occurred while checking the DataFrame: {e}")
        live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed = "Error", "Error", "Error", "Error", "Error", 0

    return index, live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed