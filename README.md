# Amazon Category Scraper

This Python script automates the process of logging into Amazon, scraping product details from specific category pages, and saving the data to CSV files.

## Features
- Logs into Amazon using credentials stored in a `credentials.json` file.
- Scrapes product details such as product names from multiple category pages.
- Saves the scraped data into CSV files.

## Prerequisites
1. **Python 3.8+**
2. **Google Chrome** (with a matching ChromeDriver version)
3. **Selenium WebDriver**

## Installation

1. Clone this repository or download the script.

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

3. Set Up credentials.json

    {
        "username": "your-email@example.com/mobile-number",
        "password": "your-password"
    }

4. Set Up ChromeDriver

    Download the appropriate version of ChromeDriver for your version of Chrome: ChromeDriver Downloads.
    Add the ChromeDriver executable to your system's PATH or place it in the same folder as the script.