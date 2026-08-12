import re
import os
import sys
import time
from typing import Any

from dotenv import load_dotenv
from loguru import logger
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

import meal_planner_email

"""Automate Walmart cart population from a generated weekly meal plan.

This script:
1) builds a grocery list from the meal plan,
2) signs in to Walmart (with manual MFA support), and
3) adds searched items to cart.
"""

load_dotenv()

logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
    level="INFO",
)

WALMART_USERNAME = os.getenv("WALMART_USERNAME")
WALMART_PASSWORD = os.getenv("WALMART_PASSWORD")
WALMART_BASE_URL = "https://www.walmart.com"
WALMART_LOGIN_URL = f"{WALMART_BASE_URL}/account/login"
SEARCH_INPUT_ID = "global-search-input"

DEFAULT_LOGIN_TIMEOUT_SECONDS = 600
DEFAULT_ELEMENT_WAIT_SECONDS = 15
DEFAULT_SEARCH_WAIT_SECONDS = 10
DEFAULT_HOME_WAIT_SECONDS = 5

if not WALMART_USERNAME or not WALMART_PASSWORD:
    logger.error("WALMART_USERNAME and WALMART_PASSWORD must be set in environment variables.")
    raise ValueError("WALMART_USERNAME and WALMART_PASSWORD must be set in environment variables.")

NO_INGREDIENTS_TEXT = "Order out or ingredients not available"


def _is_mfa_challenge_visible(driver: WebDriver) -> bool:
    """Best-effort detection for Walmart MFA/verification pages."""
    mfa_selectors = [
        (By.ID, "verificationCode"),
        (By.CSS_SELECTOR, "input[autocomplete='one-time-code']"),
        (By.XPATH, "//input[contains(@id, 'code') or contains(@name, 'code') or contains(@aria-label, 'code')]"),
        (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'verification code')]"),
        (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enter code')]"),
    ]

    for by, value in mfa_selectors:
        try:
            if driver.find_elements(by, value):
                return True
        except Exception:
            # Ignore transient stale/DOM errors while page transitions.
            continue

    return False


def _wait_for_logged_in_state(driver: WebDriver, timeout_seconds: int) -> None:
    """Wait until logged in, pausing for manual MFA if prompted."""
    end_time = time.monotonic() + timeout_seconds
    prompted_for_mfa = False

    while time.monotonic() < end_time:
        if driver.find_elements(By.ID, SEARCH_INPUT_ID):
            return

        if _is_mfa_challenge_visible(driver) and not prompted_for_mfa:
            prompted_for_mfa = True
            logger.warning("MFA challenge detected. Complete SMS verification in the browser.")
            input("After you submit the verification code and see Walmart load, press Enter here to continue...")

            # Restart timeout after manual MFA entry so the session does not close mid-verify.
            end_time = time.monotonic() + timeout_seconds
            logger.info("MFA acknowledged. Continuing login wait.")

        time.sleep(1)

    raise TimeoutException(
        f"Timed out waiting for successful login after {timeout_seconds} seconds."
    )


def open_browser() -> WebDriver:
    """Create and return an undetected Chrome WebDriver session."""
    logger.info("Opening undetected Chrome…")
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # If CHROME_VERSION is set, pin to that major version; otherwise auto-detect.
    chrome_version = os.getenv("CHROME_VERSION")
    if chrome_version:
        logger.info(f"Using CHROME_VERSION={chrome_version} for driver startup.")
        driver = uc.Chrome(version_main=int(chrome_version), options=options)
    else:
        logger.info("No CHROME_VERSION set; letting undetected_chromedriver auto-detect browser version.")
        driver = uc.Chrome(options=options)

    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get(WALMART_BASE_URL)
    return driver


def sign_in(driver: WebDriver) -> None:
    """Sign in to Walmart and wait for a logged-in state (supports MFA)."""
    logger.info("Navigating to Walmart login page…")
    driver.get(WALMART_LOGIN_URL)

    email_field = WebDriverWait(driver, DEFAULT_ELEMENT_WAIT_SECONDS).until(
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

        password_field = WebDriverWait(driver, DEFAULT_ELEMENT_WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.ID, "password"))
        )
    except (NoSuchElementException, TimeoutException):
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
    except NoSuchElementException:
        logger.error("Could not locate the Sign In button.")
        raise

    login_timeout = int(os.getenv("LOGIN_TIMEOUT_SECONDS", str(DEFAULT_LOGIN_TIMEOUT_SECONDS)))
    _wait_for_logged_in_state(driver, timeout_seconds=login_timeout)
    logger.success("Logged in successfully.")


def clear_cart(driver: WebDriver) -> None:
    """Remove existing items from the cart if present."""
    logger.info("Clearing cart.")
    try:
        driver.find_element(By.ID, "hf-cart-flyout").click()
        time.sleep(2)
        for remove in driver.find_elements(By.CLASS_NAME, "remove-item"):
            remove.click()
    except NoSuchElementException:
        logger.warning("Cart already empty or cart button not found.")


def dedupe_grocery_list(ingredients_list: list[str]) -> list[str]:
    """Return a sorted, case-insensitive de-duplicated grocery item list."""
    seen = {}
    for item in ingredients_list:
        key = item.strip().lower()
        if key and key not in seen:
            seen[key] = item.strip()
    return sorted(seen.values())


def compile_weekly_grocery_list(meal_plan: dict[str, dict[str, Any]]) -> list[str]:
    """Extract all ingredients from the weekly meal plan and generate a clean shopping list."""
    all_ingredients: list[str] = []

    for day_info in meal_plan.values():
        ingredients = day_info.get("Ingredients", "")

        # Skip "order out" days -- nothing to shop for
        if ingredients == NO_INGREDIENTS_TEXT:
            continue

        if isinstance(ingredients, list):
            all_ingredients.extend(i.strip() for i in ingredients if i.strip())

        elif isinstance(ingredients, str):
            lines = ingredients.split("<br>") if "<br>" in ingredients else ingredients.split("\n")

            for raw_line in lines:
                line = raw_line.strip()
                if not line:
                    continue

                # Skip section headers like "MEAT:" or "VEGETABLES AND EGGS:"
                if line.endswith(":") and line == line.upper():
                    continue

                # Strip bullet markers: "&bull;", "•", or a leading "- "
                cleaned = re.sub(r"^(?:&bull;|•|-)\s*", "", line).strip()
                if cleaned:
                    all_ingredients.append(cleaned)

    return dedupe_grocery_list(all_ingredients)


def shop_items(driver: WebDriver, items: list[str]) -> None:
    """Search Walmart for each item and add the first result to cart when possible."""
    for name in items:
        logger.info(f"Searching for {name}.")
        search_box = driver.find_element(By.ID, SEARCH_INPUT_ID)
        search_box.clear()
        search_box.send_keys(name)
        search_box.submit()

        try:
            WebDriverWait(driver, DEFAULT_SEARCH_WAIT_SECONDS).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-result-gridview-item"))
            )
        except TimeoutException:
            logger.warning(f"No search results for {name}.")
            driver.get(WALMART_BASE_URL)
            continue

        products = driver.find_elements(By.CSS_SELECTOR, ".search-result-gridview-item")
        if not products:
            logger.warning(f"No products found for {name}.")
            driver.get(WALMART_BASE_URL)
            continue

        products[0].find_element(By.TAG_NAME, "a").click()

        try:
            WebDriverWait(driver, DEFAULT_SEARCH_WAIT_SECONDS).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to cart') or contains(text(), 'Add to Cart')]"))
            )
            add_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add to cart') or contains(text(), 'Add to Cart')]")
            add_btn.click()
            logger.info(f"{name} added to cart.")
        except TimeoutException:
            logger.warning(f"Could not add '{name}' to cart (no Add to Cart button found).")

        driver.get(WALMART_BASE_URL)
        WebDriverWait(driver, DEFAULT_HOME_WAIT_SECONDS).until(
            EC.presence_of_element_located((By.ID, SEARCH_INPUT_ID))
        )


def main() -> None:
    """Generate grocery list, sign in, and populate the Walmart cart."""
    logger.info("Generating this week's meal plan…")
    meal_plan = meal_planner_email.generate_meal_plan_dict()

    grocery_list = compile_weekly_grocery_list(meal_plan)
    logger.info(f"Compiled {len(grocery_list)} grocery items: {grocery_list}")

    if not grocery_list:
        logger.warning("Grocery list is empty (all order-out days?). Nothing to shop for.")
        return

    driver = None
    try:
        driver = open_browser()
        sign_in(driver)
        clear_cart(driver)
        shop_items(driver, grocery_list)
        logger.success("Done. Review your cart before checking out.")
    except Exception:
        logger.exception("Error during automation.")
    finally:
        if driver is not None:
            logger.info("Closing browser.")
            driver.quit()


if __name__ == "__main__":
    main()