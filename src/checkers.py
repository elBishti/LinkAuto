import pandas as pd
import logging
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from src.helpers import check_link_live, get_page_source, check_anchor_text, check_google_index


# Custom exception class for missing information
class MissingInformationError(Exception):
    pass

# Function that checks if website is running and contains the anchor text
def main(url, to_url, anchor):
    # Add http:// to the to_url if it doesn't have a scheme
    if not urlparse(to_url).scheme:
        to_url = 'http://' + to_url

    # Headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    # Sleep for 1 second to avoid overloading the server
    time.sleep(1)

    # Check if the link is live
    status = check_link_live(url, headers)
    if status != True:
        return status, "Not Found", "Not Found", "Not Found", "Not Found", 0

    # Get the page source
    page_source = get_page_source(url)
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'lxml')

    # Check the anchor text
    found_anchor, found_anchor_text, correct_link, rel_attributes, outgoing_links = check_anchor_text(soup, anchor, to_url, url)

    # If the anchor text was not found, set it to "Not Found"
    if not found_anchor:
        found_anchor_text = "Not Found"

    # Check if the page is indexed by Google
    indexed = check_google_index(url, headers)

    return "Live", found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed

# Function to check a single row of the DataFrame
def check_row(index, row):
    try:
        # Raise an error if the URL or anchor text is missing
        if pd.isnull(row['URL']) or pd.isnull(row['Ankartext']):
            raise MissingInformationError("Missing Information")

        # Check the website
        live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed = main(row['URL'], row['To URL'], row['Ankartext'])
    except MissingInformationError as e:
        # Log the error and set the return values to "Not Checked"
        logging.error(f"An error occurred while checking the DataFrame: {e}")
        live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed = "Not Checked", "Not Checked", "Not Checked", "Not Checked", "Not Checked", 0
    except Exception as e:
        # Log the error and set the return values to "Error"
        logging.error(f"An unexpected error occurred while checking the DataFrame: {e}")
        live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed = "Error", "Error", "Error", "Error", "Error", 0

    return index, live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed

# Function to safely check a single row of the DataFrame
def safe_check_row(index, row):
    # Retry up to 3 times
    for _ in range(3):
        try:
            return check_row(index, row)
        except requests.exceptions.HTTPError as e:
            # Log the error and return the status code
            logging.warning(f"HTTP error checking row {index} with data {row}: {e}. Retrying...")
            return index, e.response.status_code, e.response.status_code, e.response.status_code, e.response.status_code, e.response.status_code
        except requests.exceptions.RequestException as e:
            # Log the error and retry
            logging.warning(f"Network error checking row {index} with data {row}: {e}. Retrying...")
            time.sleep(1)
        except IOError as e:
            # Log the error and return "File Error"
            logging.error(f"File error checking row {index} with data {row}: {e}", exc_info=True)
            return index, "File Error", "File Error", "File Error", "File Error", "File Error"
        except Exception as e:
            # Log the error and return "Error"
            logging.error(f"Unexpected error checking row {index} with data {row}: {e}", exc_info=True)
            return index, "Error", "Error", "Error", "Error", "Error"
    # If we've retried 3 times and still have a network error, log it as an error
    logging.error(f"Persistent network error checking row {index} with data {row}")
    return index, "Network Error", "Network Error", "Network Error", "Network Error", "Network Error"