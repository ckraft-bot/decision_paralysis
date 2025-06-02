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
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")
    # Disable images and enable stealth to reduce CAPTCHA risk
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(version_main=int(os.getenv("CHROME_VERSION", "135")), options=options, headless=False, use_subprocess=True)
    driver.implicitly_wait(10)
    driver.get("https://www.walmart.com")
    logger.success("✅ Browser opened and navigated to Walmart homepage.")
    return driver

def sign_in(driver):
    logger.info("Navigating to Walmart login page…")
    driver.get("https://www.walmart.com/account/login")

    email_field = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "loginId"))
    )
    logger.info("Entering username/email…")
    email_field.clear()
    email_field.send_keys(WALMART_USERNAME)

    try:
        next_btn = driver.find_element(
            By.CSS_SELECTOR,
            "button[data-automation-id='login-submit-btn'], button[type='submit']"
        )
        next_btn.click()
        logger.info("Clicked continue; waiting for password field…")
        password_field = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "password"))
        )
    except Exception:
        logger.info("Single-step login form detected; finding password field…")
        password_field = driver.find_element(By.ID, "password")

    logger.info("Entering password…")
    password_field.clear()
    password_field.send_keys(WALMART_PASSWORD)

    try:
        signin_btn = driver.find_element(
            By.CSS_SELECTOR,
            "button[data-automation-id='signin-submit-btn'], button[type='submit']"
        )
        signin_btn.click()
        logger.info("Sign in button clicked.")
    except NoSuchElementException:
        logger.error("Could not locate the Sign In button.")
        raise

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "global-search-input"))
    )
    logger.success("✅ Logged in successfully.")

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
    for i, name in enumerate(items, 1):
        logger.info(f"({i}/{len(items)}) Searching for '{name}'...")
        search_box = driver.find_element(By.ID, "global-search-input")
        search_box.clear()
        search_box.send_keys(name)
        search_box.submit()

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-testid='list-view'] div[class*='search-result-product']"))
            )
            logger.info(f"Search results loaded for '{name}'.")
        except Exception:
            logger.warning(f"No search results for '{name}'. Skipping.")
            driver.get("https://www.walmart.com")
            continue

        products = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='list-view'] div[class*='search-result-product']")
        if not products:
            logger.warning(f"No products found for '{name}'. Dumping HTML for debugging...")
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            driver.get("https://www.walmart.com")
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

        logger.info("Returning to homepage...")
        driver.get("https://www.walmart.com")
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