import os
import sys
import time
from dotenv import load_dotenv
from loguru import logger
import undetected_chromedriver as uc
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
    logger.info("Opening undetected Chrome…")
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(version_main=int(os.getenv("CHROME_VERSION", "135")), options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get("https://www.walmart.com")
    return driver


def sign_in(driver):
    logger.info("Navigating directly to login page.")
    driver.get("https://www.walmart.com/account/login")
    try:
        # Wait for the email input by name attribute
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
    except Exception:
        logger.error("Login page did not load or email field not found. Page title: %s", driver.title)
        # optionally dump a snippet of page source for debugging
        snippet = driver.page_source[:200]
        logger.debug("Page source snippet: %s", snippet)
        raise

    email_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "password")
    logger.info("Entering credentials.")
    email_field.clear()
    email_field.send_keys(WALMART_USERNAME)
    password_field.clear()
    password_field.send_keys(WALMART_PASSWORD)

    # Attempt to click sign-in button if present, else submit via form
    try:
        signin_btn = driver.find_element(By.XPATH, "//button[@type='submit' and (contains(., 'Sign in') or contains(., 'Log in'))]")
        signin_btn.click()
    except Exception:
        password_field.submit()

    logger.info("Login submitted, waiting for search input on homepage.")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "global-search-input"))
    )


def clear_cart(driver):
    logger.info("Clearing cart.")
    driver.find_element(By.ID, "hf-cart-flyout").click()
    time.sleep(2)
    for remove in driver.find_elements(By.CLASS_NAME, "remove-item"):
        remove.click()


def get_grocery_list():
    logger.info("Fetching grocery list.")
    return [
        ("bananas", "5"),
        ("orange juice", "1"),
        ("milk", "1"),
    ]


def shop_items(driver, items):
    for name, qty in items:
        logger.info(f"Searching for {name}.")
        search_box = driver.find_element(By.ID, "global-search-input")
        search_box.clear()
        search_box.send_keys(name)
        search_box.submit()

        # Wait for product grid items
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-result-gridview-item"))
            )
        except Exception:
            logger.warning(f"No search results for {name}.")
            driver.get("https://www.walmart.com")
            continue

        products = driver.find_elements(By.CSS_SELECTOR, ".search-result-gridview-item")
        if not products:
            logger.warning(f"No products found for {name}.")
            driver.get("https://www.walmart.com")
            continue

        # Click the first product link
        products[0].find_element(By.TAG_NAME, "a").click()

        # Wait for Add to cart button
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add to cart') or contains(., 'Add to Cart')]))"))
        )
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Add to cart') or contains(., 'Add to Cart')]")
        add_btn.click()
        logger.info(f"{name} added to cart.")

        # Return to homepage for next iteration
        driver.get("https://www.walmart.com")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "global-search-input"))
        )


def main():
    driver = open_browser()
    try:
        sign_in(driver)
        clear_cart(driver)
        shop_items(driver, get_grocery_list())
    except Exception:
        logger.exception("Error during automation.")
    finally:
        logger.info("Closing browser.")
        driver.quit()


if __name__ == "__main__":
    main()
