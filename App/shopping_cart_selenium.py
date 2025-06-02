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
    driver = uc.Chrome(version_main=int(os.getenv("CHROME_VERSION", "135")), options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get("https://www.walmart.com")
    return driver


def sign_in(driver):
    logger.info("Navigating to Walmart login page…")
    driver.get("https://www.walmart.com/account/login")

    # 1) Wait for / find the email/phone field
    email_field = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "loginId"))
    )
    logger.info("Entering username/email…")
    email_field.clear()
    email_field.send_keys(WALMART_USERNAME)

    # 2) Try clicking the “Continue” or “Next” button if present
    try:
        next_btn = driver.find_element(
            By.CSS_SELECTOR,
            "button[data-automation-id='login-submit-btn'], button[type='submit']"
        )
        next_btn.click()
        logger.info("Clicked continue; waiting for password field…")

        # 3) Now wait for password input on the second step
        password_field = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "password"))
        )
    except Exception:
        # if no 2-step flow, maybe email & password are on same page
        logger.info("Single-step login form detected; finding password field…")
        password_field = driver.find_element(By.ID, "password")

    # 4) Enter password
    logger.info("Entering password…")
    password_field.clear()
    password_field.send_keys(WALMART_PASSWORD)

    # 5) Click the final “Sign In” button
    try:
        signin_btn = driver.find_element(
            By.CSS_SELECTOR,
            "button[data-automation-id='signin-submit-btn'], button[type='submit']"
        )
        signin_btn.click()
    except NoSuchElementException:
        logger.error("Could not locate the Sign In button.")
        raise

    # 6) Wait for the homepage (search box) to appear
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "global-search-input"))
    )
    logger.success("✅ Logged in successfully.")


def clear_cart(driver):
    logger.info("Clearing cart.")
    try:
        driver.find_element(By.ID, "hf-cart-flyout").click()
        time.sleep(2)
        for remove in driver.find_elements(By.CLASS_NAME, "remove-item"):
            remove.click()
    except NoSuchElementException:
        logger.warning("Cart already empty or cart button not found.")


# def get_grocery_list(ingredients_list):
#     """Simple aggregator for grocery items (could be extended to count quantities)."""
#     grocery_set = set()
#     for item in ingredients_list:
#         grocery_set.add(item.strip())
#     return sorted(grocery_set)

def shop_items(driver, items):
    for name in items:
        logger.info(f"Searching for {name}.")
        search_box = driver.find_element(By.ID, "global-search-input")
        search_box.clear()
        search_box.send_keys(name)
        search_box.submit()

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

        try:
            products[0].find_element(By.TAG_NAME, "a").click()

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to cart') or contains(text(), 'Add to Cart')]"))
            )
            add_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add to cart') or contains(text(), 'Add to Cart')]")
            add_btn.click()
            logger.info(f"{name} added to cart.")
        except Exception as e:
            logger.warning(f"Could not add {name} to cart: {e}")

        driver.get("https://www.walmart.com")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "global-search-input"))
        )


# def compile_weekly_grocery_list(meal_plan):
#     """Extract all ingredients from the weekly meal plan and generate a clean shopping list."""
#     all_ingredients = []

#     # Iterate over each day's entry in the meal plan
#     for day_info in meal_plan.values():
#         ingredients = day_info["Ingredients"]

#         # If ingredients are already a list, add them directly
#         if isinstance(ingredients, list):
#             all_ingredients.extend(ingredients)

#         # If ingredients are a string (possibly HTML or plain text), process line-by-line
#         elif isinstance(ingredients, str):
#             # Split by <br> if HTML, otherwise use newline
#             lines = ingredients.split("<br>") if "<br>" in ingredients else ingredients.split("\n")
            
#             for line in lines:
#                 # Use regex to extract content after &bull; or • symbol
#                 match = re.search(r"(?:&bull;|•)\s*(.+)", line.strip())
                
#                 if match:
#                     # Add the cleaned ingredient text to the list
#                     all_ingredients.append(match.group(1).strip())
#                 elif line.strip():
#                     # Fallback: include the line if not empty even if no bullet match
#                     all_ingredients.append(line.strip())

#     # Remove duplicates and sort the final list
#     return get_grocery_list(all_ingredients)


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