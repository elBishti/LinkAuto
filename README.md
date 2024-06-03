# Google Sheet Link Automation

This script automates the process of checking the presence of specific links and anchor texts on a list of webpages. It reads and ammends straight into a google sheet with rellevant information about the URL's

## Installation

This script requires the following Python packages:

- Pandas: For data manipulation and analysis.
- Selenium: For automating web browser interaction.
- webdriver-manager: For managing the browser driver needed by Selenium.
- BeautifulSoup (bs4): For parsing HTML and XML documents.
- re: For regular expression operations.
- oauth2client: For getting access to google sheets

You can install these packages using pip:

```bash
pip install pandas selenium webdriver-manager beautifulsoup4 re oauth2client
```

## Usage
First you need to get a Google Sheets API and add it to the code, thereafter you will need to get credentials.json and add to a new folder called config,
You will also have to share the sheets with the email you get from your Google Sheets API,

Prepare your data: Add you google sheets name to the code in app.py. The sheet should contain a URL Column, An Ankartext Column & a To URL column.

The script uses Selenium, and this script specifically uses google chrome so make sure you have it downloaded.

Run the script: You can run the script in one of two ways:

```bash
python app.py
```

Click the run button in your Python IDE.

## Understanding the Results
The script will add a new column to your Sheet with the results of the check:

There are multiple colors that will be added and color depending on the result.

This README provides a brief description of the script, instructions for installing the required packages, steps for using the script, and an explanation of the results.



