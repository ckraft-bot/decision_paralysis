import os
import sys
import time
from dotenv import load_dotenv
from loguru import logger
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables from the .env file
load_dotenv()

# Configure loguru: custom format to stdout
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
    level="INFO",
)

# Walmart credentials
WALMART_USERNAME = os.getenv("WALMART_USERNAME")
WALMART_PASSWORD = os.getenv("WALMART_PASSWORD")

if not WALMART_USERNAME or not WALMART_PASSWORD:
    logger.error("WALMART_USERNAME and WALMART_PASSWORD must be set in environment variables.")
    raise ValueError("WALMART_USERNAME and WALMART_PASSWORD must be set in environment variables.")

def open_browser():
    logger.info("Opening Chrome and loading Walmart homepage.")
    driver = Chrome()
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get("https://www.walmart.com")
    return driver

def sign_in(driver):
    logger.info("Signing in.")
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign in')]"))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "sign-in-email"))
    )
    driver.find_element(By.ID, "sign-in-email").send_keys(WALMART_USERNAME)
    driver.find_element(By.ID, "sign-in-password").send_keys(WALMART_PASSWORD)
    driver.find_element(By.ID, "sign-in-button").click()

def clear_cart(driver):
    logger.info("Clearing cart.")
    driver.find_element(By.ID, "hf-cart-flyout").click()
    time.sleep(2)
    for remove in driver.find_elements(By.CLASS_NAME, "remove-item"):
        remove.click()

def get_grocery_list():
    logger.info("Fetching grocery list.")
    return [
        ("bananas",  "5", "2.00"),
        ("orange juice", "1", "4.00"),
        ("milk",     "1", "7.00"),
    ]

def shop_items(driver, items):
    for name, qty, max_price in items:
        logger.info(f"Searching for {name} under ${max_price}.")
        box = driver.find_element(By.ID, "global-search-input")
        box.clear()
        box.send_keys(name)
        box.submit()
        time.sleep(2)
        products = driver.find_elements(By.CLASS_NAME, "product-tile")
        for p in products:
            price = float(p.find_element(By.CLASS_NAME, "price").text.replace('$',''))
            if price <= float(max_price):
                p.click()
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "add-to-cart-button"))
                )
                driver.find_element(By.ID, "quantity").clear()
                driver.find_element(By.ID, "quantity").send_keys(qty)
                driver.find_element(By.ID, "add-to-cart-button").click()
                time.sleep(1)
                break
        else:
            logger.warning(f"No {name} under ${max_price} found.")

def main():
    driver = open_browser()
    try:
        sign_in(driver)
        clear_cart(driver)
        items = get_grocery_list()
        shop_items(driver, items)
    except Exception:
        logger.exception("Error during automation.")
    finally:
        logger.info("Closing browser.")
        driver.quit()

if __name__ == "__main__":
    main()
