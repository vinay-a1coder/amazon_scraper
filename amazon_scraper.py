import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import json
import csv

with open("config/credentials.json") as f:
    credentials = json.load(f)

def amazon_login():
    """
    Logs into Amazon using credentials from the 'credentials.json' file.

    Returns:
        webdriver.Chrome: A Selenium Chrome WebDriver instance with an active session.
    """
   
    driver = webdriver.Chrome()
    driver.get("https://www.amazon.in/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.in%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=inflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
    
    try:
        # Explicit wait setup
        wait = WebDriverWait(driver, 15)  # Wait for up to 15 seconds
        
        # Enter email/phone
        email_input = wait.until(EC.presence_of_element_located((By.ID, "ap_email")))
        email_input.send_keys(credentials["username"])
        
        # Click 'Continue' button
        continue_button = wait.until(EC.element_to_be_clickable((By.ID, "continue")))
        continue_button.click()

        # Enter password
        password_input = wait.until(EC.presence_of_element_located((By.ID, "ap_password")))
        password_input.send_keys(credentials["password"])
        
        # Check if CAPTCHA appears
        print("If CAPTCHA appears, solve it manually.")
        time.sleep(20)  # Give enough time for the user to solve CAPTCHA manually

        # Click 'Sign-In' button
        sign_in_button = wait.until(EC.element_to_be_clickable((By.ID, "signInSubmit")))
        sign_in_button.click()
        
        print("Login successful!")
        time.sleep(5)  # Pause for visual confirmation
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        return driver

def extract_product_details(driver, category_name, images_folder):
    """
    Extracts product details from a product page.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        category_name (str): The name of the category.
        images_folder (str): Path to save images.

    Returns:
        dict: A dictionary containing product details.
    """
    def safe_find_element(by, value, default="N/A"):
        try:
            return driver.find_element(by, value).text
        except:
            return default

    def safe_find_elements(by, value):
        try:
            return driver.find_elements(by, value)
        except:
            return []

    try:
        # Extract details
        name = safe_find_element(By.ID, "productTitle")
        price = safe_find_element(By.CSS_SELECTOR, ".a-price .a-offscreen")
        discount = safe_find_element(By.CSS_SELECTOR, ".savingsPercentage")
        rating = safe_find_element(By.CSS_SELECTOR, ".a-icon-star-small span.a-icon-alt")
        description = safe_find_element(By.ID, "feature-bullets")
        num_bought = safe_find_element(By.XPATH, "//div[contains(text(), 'bought in past month')]")
        ship_from = safe_find_element(By.XPATH, "//span[contains(text(), 'Ships from')]/following-sibling::span")
        sold_by = safe_find_element(By.XPATH, "//span[contains(text(), 'Sold by')]/following-sibling::span")

        # Extract images
        images = safe_find_elements(By.CSS_SELECTOR, "#altImages img")
        image_urls = [img.get_attribute("src") for img in images]

        # Save images to folder
        image_filenames = []
        for idx, img_url in enumerate(image_urls):
            if img_url:
                response = requests.get(img_url)
                if response.status_code == 200:
                    image_filename = os.path.join(images_folder, f"{name[:30]}_{idx}.jpg")
                    with open(image_filename, "wb") as img_file:
                        img_file.write(response.content)
                    image_filenames.append(image_filename)

        return {
            "Product Name": name,
            "Product Price": price,
            "Sale Discount": discount,
            "Best Seller Rating": rating,
            "Ship From": ship_from,
            "Sold By": sold_by,
            "Rating": rating,
            "Product Description": description,
            "Number Bought in the Past Month": num_bought,
            "Category Name": category_name,
            "Images": ", ".join(image_filenames),
        }

    except Exception as e:
        print(f"Error extracting product details: {e}")
        return None


def scrape_category(driver, category_url, category_name, limit=1500):
    """
    Scrapes product details from a specific Amazon category.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        category_url (str): The URL of the Amazon category page.
        category_name (str): The category name.
        limit (int): The maximum number of products to scrape.

    Returns:
        list: A list of dictionaries containing product details.
    """
    driver.get(category_url)
    products_data = []
    product_count = 0

    # Create a folder for images for this category
    images_folder = os.path.join("images", category_name)
    os.makedirs(images_folder, exist_ok=True)

    while product_count < limit:
        time.sleep(2)
        product_links = [link.get_attribute("href") for link in driver.find_elements(By.CSS_SELECTOR, ".a-link-normal")]

        for link in product_links:
            if product_count >= limit:
                break
            try:
                driver.get(link)
                details = extract_product_details(driver, category_name, images_folder)
                if details:
                    products_data.append(details)
                    product_count += 1
                    print(f"Scraped {product_count} products...")
            except Exception as e:
                print(f"Skipping product due to error: {e}")

        try:
            driver.find_element(By.CSS_SELECTOR, ".a-last a").click()
        except:
            break

    return products_data

def save_to_csv(data, filename):
    """
    Saves the scraped product data to a CSV file.

    Args:
        data (list): A list of dictionaries containing product details.
        filename (str): The name of the CSV file to save the data.
    """
    if not data:
        print("No data to save.")
        return
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, keys)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    # Initialize Selenium WebDriver
    driver = driver = amazon_login()

    # Define category URLs
    category_urls = [
        "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
        "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
        "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
        "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",
    ]

    # Ensure folders exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    # Scrape each category
    for url in category_urls:
        category_name = url.split("/")[5]
        print(f"Scraping category: {category_name}")
        filename = f"data/{category_name}_best_sellers.csv"

        # Scrape and save data
        data = scrape_category(driver, url, category_name, limit=50)
        save_to_csv(data, filename)
        print(f"Data saved to {filename}")

    driver.quit()