# Google Sheet Link Automation

#### Video Demo: https://youtu.be/GE6Mei7loxI

This script automates the process of checking the presence of specific links and anchor texts on a list of webpages. It reads and ammends straight into a google sheet with rellevant information about the URL's

## Installation

This script requires the following Python packages:

- pandas: A data manipulation and analysis library.
- logging: A standard Python library for generating logging messages.
- time: A standard Python library for time-related functions.
- requests: A library for making HTTP requests in Python.
- bs4 (BeautifulSoup4): A library for pulling data out of HTML and XML files.
- urllib: A standard Python library for working with URLs.
- selenium: A web testing library used to automate browser activities.
- webdriver_manager: A helper tool to easily get an instance of a WebDriver.
- gspread: A Python client for Google Sheets.
- gspread_dataframe: A library to get a pandas DataFrame from a Google Sheets using gspread.
- gspread_formatting: A library to get and set cell formatting in Google Sheets with gspread.
- oauth2client: A library for OAuth 2.0 client-side functionality.

You can install these packages using pip:

```bash
pip install pandas logging time requests bs4 urllib selenium webdriver_manager gspread gspread_dataframe gspread_formatting oauth2client
```

## Usage

Google Sheets API: You need to enable the Google Sheets API for your Google account. This API allows your script to interact with Google Sheets. Once you've enabled the API, you'll receive a key that you need to add to your code.

credentials.json: This is a file that contains the credentials required to authenticate your script with the Google Sheets API. You need to download this file from the Google Cloud Console and add it to a new folder in your project directory named config.

Sharing the sheet: The Google Sheets document that your script will interact with needs to be shared with the email address associated with your Google Sheets API. This is to ensure that your script has the necessary permissions to read from and write to the sheet.

Preparing your data: You need to specify the name of your Google Sheets document in the app.py file. The sheet should contain three columns: a URL column, an Anchor Text column, and a To URL column.

Selenium and Google Chrome: The script uses Selenium, a tool for automating web browsers, to scrape data from web pages. This particular script is set up to use the Google Chrome browser, so you need to have it installed on your machine.

Running the script: Once you've set everything up, you can run the script. The README doesn't specify the two ways to run the script, but typically, you can run a Python script directly from the command line or from within an integrated development environment (IDE) like Visual Studio Code.

```bash
python app.py
```

Click the run button in your Python IDE.

## Understanding the Results
The script will add a new column to your Sheet with the results of the check:

There are multiple colors that will be added and color depending on the result.

This README provides a brief description of the script, instructions for installing the required packages, steps for using the script, and an explanation of the results.

## Understanding the files
### app.py
The script itself and is used to start the script. It's used to open the google sheet aswell as ammend the new data into the google sheet.
### helpers.py 
Contains several helper functions for web scraping and link checking. Using selenium it opens up a browser and then using my
functions like check_link_live, get_page_source & check_anchor_text it's checking for different criterias and are returning them to print them into the google sheets.
### checkers.py
Contains functions for web scraping and link checking. It uses libraries such as pandas, requests, and BeautifulSoup to fetch and parse web pages.
### format.py
is the file used to "paint" the different cells depending on their values. It reads the value from a cell and then depending on the value it "paints" the cell red, green or yellow.
Red meaning the result is wrong or the site is down, green meaning everything is correct and yellow indicating that something might be incorrect.
### .gitignore
is used to not push certain files to my git and not reveal my secret key. I had big problems with this as it didnt allow me to push new commit's or synch my git's. But after long investigation i finally got it to work.

## Difficulties
I would say that the greates setbacks i had was the .gitignore, and also understand how to code outside the CS50 environment. Using different structures and trying to implement the google sheets api. The main idea was to run it using only a CSV file but i quickly figured out it will be easier for me to use if it's connected to the google sheets. The only fallback is that it's harder for other people to set up the file for themself.

## Tools
For this project i've used ChatGPT & Github Co-Pilot. It's been essential for making my debugging go faster and also commenting in the projects to make it easy to understand.




