from playwright.sync_api import sync_playwright
from loguru import logger
from dotenv import load_dotenv
import os
import sys

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

def sign_in(page):
    logger.info("🔐 Signing in to Walmart.com...")
    page.goto("https://www.walmart.com/account/login")

    # Fill in login form
    page.wait_for_selector("input#loginId")
    page.fill("input#loginId", WALMART_USERNAME)
    page.fill("input#password", WALMART_PASSWORD)

    # Click the sign-in button
    page.click("button:has-text('Sign in')")

    # Wait until we're logged in (e.g., user profile button appears)
    page.wait_for_timeout(5000)  # You can improve this with a more robust check
    logger.success("✅ Successfully signed in!")


def add_item_to_cart(item_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        sign_in(page)  # Perform login before doing anything

        logger.info(f"🌐 Searching Walmart for: {item_name}")
        page.goto("https://www.walmart.com/")
        page.fill("input[aria-label='Search Walmart.com']", item_name)
        page.press("input[aria-label='Search Walmart.com']", "Enter")
        page.wait_for_timeout(3000)

        try:
            page.click("a[data-item-id]:nth-of-type(1)")
            page.wait_for_timeout(2000)
            page.click("button:has-text('Add to cart')")  # Case-sensitive match
            logger.success(f"✅ Added '{item_name}' to cart!")
        except Exception as e:
            logger.error(f"⚠️ Could not add '{item_name}': {e}")
        browser.close()

# Your grocery list
grocery_list = ["avocado", "extra firm tofu", "grape tomatoes"]

for item in grocery_list:
    add_item_to_cart(item)
