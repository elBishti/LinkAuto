import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import logging
from checkers import check_row
from datetime import datetime

# Set up the logger
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('This will get logged to a file')

# Create a lock
lock = Lock()

# Path

df = pd.read_csv('data/test.csv')

# Create new columns in the DataFrame
df["Live Status"] = ""
df["Found Anchor Text"] = ""
df["Correct Link"] = ""
df["Indexed"] = ""
df["Rel Attributes"] = ""
df["Outgoing Links"] = ""
df["Time"] = ""

results = []
# Create a ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=5) as executor:
    # Use the executor to run check_row in parallel for each row in the DataFrame
    results = list(executor.map(check_row, df.index, df.to_dict('records')))

# Assign the results to the new columns
for result in results:
    index, live_status, found_anchor_text, correct_link, rel_attributes, outgoing_links, indexed = result

    with lock:
        df.at[index, "Live Status"] = live_status
        df.at[index, "Found Anchor Text"] = found_anchor_text
        df.at[index, "Correct Link"] = correct_link
        df.at[index, "Indexed"] = indexed
        df.at[index, "Rel Attributes"] = rel_attributes
        df.at[index, "Outgoing Links"] = outgoing_links
        df.at[index, "Time"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(live_status, found_anchor_text, correct_link, indexed, rel_attributes, outgoing_links, datetime.now().strftime("%Y-%m-%d %H:%M")

# Save the DataFrame to a CSV file
df.to_csv('data/test.csv', index=False)
