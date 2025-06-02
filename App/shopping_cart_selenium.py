import os
import sys
import time
import re
from dotenv import load_dotenv
from loguru import logger
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import meal_planner_email

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
    logger.info("Opening undetected Chrome…")
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-data-dir=/tmp/chrome_user_data")
    options.add_argument("--profile-directory=Default")
    driver = uc.Chrome(version_main=int(os.getenv("CHROME_VERSION", "135")), options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get("https://www.walmart.com")
    logger.success("✅ Browser opened and navigated to Walmart homepage.")
    return driver

def sign_in(driver):
    logger.info("Assuming session is authenticated via cookies or manual login.")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "global-search-input"))
    )
    logger.success("✅ Browser session appears logged in.")

def clear_cart(driver):
    logger.info("Clearing cart.")
    try:
        driver.find_element(By.ID, "hf-cart-flyout").click()
        time.sleep(2)
        removed = 0
        for remove in driver.find_elements(By.CLASS_NAME, "remove-item"):
            remove.click()
            removed += 1
        logger.info(f"Removed {removed} item(s) from cart.")
    except NoSuchElementException:
        logger.warning("Cart already empty or cart button not found.")

def shop_items(driver, items):
    driver.get("https://www.walmart.com/cp/food/976759")
    for i, name in enumerate(items, 1):
        logger.info(f"({i}/{len(items)}) Searching for '{name}' on food page...")

        search_box = driver.find_element(By.ID, "global-search-input")
        search_box.clear()
        search_box.send_keys(name)
        search_box.send_keys(Keys.RETURN)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-testid='list-view'] div[class*='search-result-product']"))
            )
            logger.info(f"Search results loaded for '{name}'.")
        except Exception:
            logger.warning(f"No search results for '{name}'. Skipping.")
            driver.get("https://www.walmart.com/cp/food/976759")
            continue

        products = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='list-view'] div[class*='search-result-product']")
        if not products:
            logger.warning(f"No products found for '{name}'. Skipping.")
            driver.get("https://www.walmart.com/cp/food/976759")
            continue

        try:
            logger.info(f"Clicking first result for '{name}'...")
            products[0].find_element(By.CSS_SELECTOR, "a[href]").click()

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to cart') or contains(text(), 'Add to Cart')]"))
            )
            add_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add to cart') or contains(text(), 'Add to Cart')]")
            add_btn.click()
            logger.success(f"✅ '{name}' added to cart.")
        except Exception as e:
            logger.warning(f"Could not add '{name}' to cart: {e}")

        logger.info("Returning to food page...")
        driver.get("https://www.walmart.com/cp/food/976759")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "global-search-input"))
        )

def main():
    logger.info("Using test grocery list for Walmart automation...")

    fake_ingredients = [
        "eggs",
        "milk",
        "spinach",
        "olive oil",
        "garlic",
        "bananas",
        "orange juice"
    ]

    driver = open_browser()
    try:
        sign_in(driver)
        clear_cart(driver)
        shop_items(driver, fake_ingredients)
    except Exception:
        logger.exception("Error during automation.")
    finally:
        logger.info("Closing browser.")
        driver.quit()

if __name__ == "__main__":
    main()