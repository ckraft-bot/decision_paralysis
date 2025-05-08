import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import meal_planner_email
from meal_planner_email import INGREDIENTS

# ——— Logging setup ———
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── CONFIG ──
# WALMART_EMAIL = os.getenv("WALMART_EMAIL")
# WALMART_PASSWORD = os.getenv("WALMART_PASSWORD")
WALMART_STORE_ID = os.getenv("WALMART_STORE_ID")  # default zip code

# Selenium setup
chrome_opts = Options()
chrome_opts.add_argument("--headless")
chrome_opts.add_argument("--disable-gpu")
chrome_opts.add_argument("--window-size=1920,1080")

def init_driver():
    logger.info("Initializing headless Chrome driver")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_opts)
    driver.implicitly_wait(5)
    return driver


def login(driver):
    logger.info("Navigating to Walmart login page")
    driver.get("https://www.walmart.com/account/login")
    # email field
    email_input = driver.find_element(By.ID, "email")
    email_input.clear()
    email_input.send_keys(WALMART_EMAIL)
    # password field
    pw_input = driver.find_element(By.ID, "password")
    pw_input.clear()
    pw_input.send_keys(WALMART_PASSWORD)
    # submit
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='signin-submit-btn']")
    submit_btn.click()
    time.sleep(3)
    # verify login
    if "Account overview" in driver.page_source or "My Account" in driver.page_source:
        logger.info("✅ Logged in successfully")
    else:
        logger.error("❌ Login failed; check credentials or MFA flow")
        raise RuntimeError("Login failed")


def set_store(driver):
    logger.info("Setting store zip code to %s", WALMART_STORE_ID)
    driver.get(f"https://www.walmart.com/store/finder?zipcode={WALMART_STORE_ID}")
    time.sleep(2)
    # click first 'Select this store'
    try:
        select_btn = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='select-store-btn']")
        select_btn.click()
        time.sleep(2)
        logger.info("Store set successfully")
    except Exception:
        logger.warning("Could not set store automatically; please verify manually")


def add_item_to_cart(driver, query):
    logger.info("Searching and adding '%s' to cart", query)
    # search
    search_box = driver.find_element(By.NAME, "query")
    search_box.clear()
    search_box.send_keys(query)
    search_box.submit()
    time.sleep(2)
    # add to cart
    try:
        add_btn = driver.find_element(
            By.CSS_SELECTOR,
            "button.prod-ProductCTA--primary"
        )
        add_btn.click()
        logger.info("➕ Added '%s' to cart", query)
        time.sleep(1)
    except Exception as e:
        logger.error("❌ Failed to add '%s': %s", query, e)


def build_shopping_list(plan_dict):
    from itertools import chain
    items = []
    for details in plan_dict.values():
        meal = details['Meal']
        ing = INGREDIENTS.get(meal, {})
        for section_items in ing.values():
            items.extend(section_items)
    # dedupe
    shopping_list = sorted(set(items))
    logger.info("Built shopping list with %d items", len(shopping_list))
    return shopping_list


if __name__ == '__main__':
    if not (WALMART_EMAIL and WALMART_PASSWORD):
        logger.error("Missing WALMART_EMAIL or WALMART_PASSWORD environment variables")
        exit(1)

    driver = init_driver()
    try:
        login(driver)
        set_store(driver)
        shopping_queries = build_shopping_list(meal_plan_dict)
        for q in shopping_queries:
            add_item_to_cart(driver, q)
    except Exception:
        logger.exception("Script terminated with an error")
    finally:
        driver.quit()
        logger.info("Driver quit; script complete")
