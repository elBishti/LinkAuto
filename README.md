# Camjo Link & Anchor Automation

This script automates the process of checking the presence of specific links and anchor texts on a list of webpages. It reads a CSV file containing the URLs of the webpages to check, and adds a new column to the CSV file with the results of the check. The results can be "Found ALL", "Found URL", or "Not Found".

## Installation

This script requires the following Python packages:

- Pandas: For data manipulation and analysis.
- Selenium: For automating web browser interaction.
- webdriver-manager: For managing the browser driver needed by Selenium.
- BeautifulSoup (bs4): For parsing HTML and XML documents.
- re: For regular expression operations.

You can install these packages using pip:

```bash
pip install pandas selenium webdriver-manager beautifulsoup4
```

## Usage
Prepare your data: Add your CSV file to the /data directory. The CSV file should contain a column with the URLs of the webpages to check.

Choose your browser type: The script uses Selenium, which supports multiple browsers. You need to specify the type of browser you want to use.

Update the path: Rename the path under the # Path comment in the script to match the path of your CSV file.

Run the script: You can run the script in one of two ways:

```bash
python chrome-link-check.py
```

Click the run button in your Python IDE.
Run the script from the command line:

## Understanding the Results
The script will add a new column to your CSV file with the results of the check:

"Found ALL": The script found both the link and the anchor text on the webpage.
"Found URL": The script found the link on the webpage, but not the anchor text.
"Not Found": The script didn't find the link on the webpage.
```

This README provides a brief description of the script, instructions for installing the required packages, steps for using the script, and an explanation of the results.



