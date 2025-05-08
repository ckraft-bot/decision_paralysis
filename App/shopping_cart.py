import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import meal_planner_email

# ——— Logging setup ———
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── CONFIG ──
WALMART_USERNAME = os.getenv("WALMART_USERNAME")
WALMART_PASSWORD = os.getenv("WALMART_PASSWORD")
WALMART_ZIPCODE  = os.getenv("WALMART_ZIPCODE", "") 

# Selenium options
chrome_opts = Options()
chrome_opts.add_argument("--headless")
chrome_opts.add_argument("--disable-gpu")
chrome_opts.add_argument("--window-size=1920,1080")

def init_driver():
    logger.info("Initializing headless Chrome driver")
    chrome_driver_version = os.getenv("CHROMEDRIVER_VERSION")
    if chrome_driver_version:
        driver_path = ChromeDriverManager(version=chrome_driver_version).install()
    else:
        driver_path = ChromeDriverManager().install()
    service = ChromeService(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_opts)
    driver.implicitly_wait(5)
    return driver

def login(driver):
    logger.info("Navigating to Walmart login page")
    driver.get("https://www.walmart.com/account/login")
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    wait = WebDriverWait(driver, 10)
    try:
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_input.clear()
        email_input.send_keys(WALMART_USERNAME)
        pw_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        pw_input.clear()
        pw_input.send_keys(WALMART_PASSWORD)
        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-automation-id='signin-submit-btn']")))
        submit_btn.click()
        wait.until(EC.any_of(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Account overview') or contains(text(), 'My Account') ]")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.error-message"))
        ))
        if "error-message" in driver.page_source:
            logger.error("❌ Login failed; check credentials or MFA flow")
            raise RuntimeError("Login failed; error shown on page.")
        logger.info("✅ Logged in successfully")
    except Exception as e:
        logger.exception("Exception during login: %s", e)
        raise

def set_store(driver):
    logger.info("Setting store zip code to %s", WALMART_ZIPCODE)
    driver.get(f"https://www.walmart.com/store/finder?zipcode={WALMART_ZIPCODE}")
    time.sleep(2)
    try:
        select_btn = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='select-store-btn']")
        select_btn.click()
        time.sleep(2)
        logger.info("Store set successfully")
    except Exception:
        logger.warning("Could not set store automatically; please verify manually")

def add_item_to_cart(driver, query):
    logger.info("Searching and adding '%s' to cart", query)
    search_box = driver.find_element(By.NAME, "query")
    search_box.clear()
    search_box.send_keys(query)
    search_box.submit()
    time.sleep(2)
    try:
        add_btn = driver.find_element(By.CSS_SELECTOR, "button.prod-ProductCTA--primary")
        add_btn.click()
        logger.info("➕ Added '%s' to cart", query)
        time.sleep(1)
    except Exception as e:
        logger.error("❌ Failed to add '%s': %s", query, e)

def build_shopping_list_from_plan(plan_dict):
    # Stub: return fake shopping list instead of parsing plan_dict
    fake_items = ["banana", "milk", "orange juice", "takis"]
    return sorted(set(fake_items))

if __name__ == '__main__':
    if not (WALMART_USERNAME and WALMART_PASSWORD):
        logger.error("Missing WALMART_USERNAME or WALMART_PASSWORD environment variables")
        exit(1)

    # Generate a new meal plan dict with raw ingredients (placeholder, not used here)
    meal_plan_dict = meal_planner_email.generate_meal_plan_dict()

    # Extract grocery list
    shopping_queries = build_shopping_list_from_plan(meal_plan_dict)
    logger.info("Final shopping list: %s", shopping_queries)

    driver = init_driver()
    try:
        login(driver)
        set_store(driver)
        for q in shopping_queries:
            add_item_to_cart(driver, q)
    except Exception:
        logger.exception("Script terminated with an error")
    finally:
        driver.quit()
        logger.info("Driver quit; script complete")
