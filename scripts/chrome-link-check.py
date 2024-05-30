import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import gspread
import logging
import string
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from src.checkers import check_row, safe_check_row
from datetime import datetime
from src.format import format_cells, column_number_to_letter
from oauth2client.service_account import ServiceAccountCredentials


# Set up the logger
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('This will get logged to a file')

# Create a lock
lock = Lock()

# Use the credential.json to authenticate the Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds_path = os.path.join(os.path.dirname(__file__), '../config/credentials.json')
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

# Open the Google SpreadSheet and get first sheet
spreadsheet = client.open('test2')
sheet = spreadsheet.sheet1

# Read the data from the sheet into a DataFrame
data = sheet.get_all_values()

# Create a DataFrame from the data, excluding the first row (header row)
df = pd.DataFrame(data[1:], columns=data[0])

# Add new columns to the DataFrame
new_columns = ["Updated Status", "Anchor Text", "Correct Link", "Indexed", "Rel Attributes", "Outgoing Links", "Last Time Refreshed"]
for col in new_columns:
    df[col] = ""

# Create a ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(safe_check_row, df.index, df.to_dict('records')))

# Assign the results to the new columns
for i, result in enumerate(results):
    index, live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed = result

    with lock:
        df.at[i, "Updated Status"] = live_status
        df.at[i, "Anchor Text"] = found_anchor_text
        df.at[i, "Correct Link"] = correct_link
        df.at[i, "Indexed"] = indexed
        df.at[i, "Rel Attributes"] = rel_attributes
        df.at[i, "Outgoing Links"] = outgoing_links
        df.at[i, "Last Time Refreshed"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(live_status, found_anchor_text, correct_link, indexed, rel_attributes, outgoing_links, datetime.now().strftime("%Y-%m-%d %H:%M"))
    
# Convert the DataFrame back to a list of lists and add the headers
new_data = [df.columns.tolist()] + df.values.tolist()

# Calculate last column letter
num_columns = len(df.columns)
last_column_letter = string.ascii_uppercase[num_columns - 1]

# Write the updated data back to the sheet
range_string = f"A1:{last_column_letter}{len(new_data)}"
sheet.update(values=new_data, range_name=range_string)

# Format the cells
format_cells(sheet, df)
