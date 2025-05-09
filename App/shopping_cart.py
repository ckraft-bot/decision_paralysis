from playwright.sync_api import sync_playwright
from loguru import logger

# Configure loguru to write logs to a file (optional)
logger.add("walmart_cart.log", rotation="500 KB")

def add_item_to_cart(item_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set headless=True for no browser window
        page = browser.new_page()
        
        logger.info(f"🌐 Navigating to Walmart to search for: {item_name}")
        page.goto("https://www.walmart.com/")
        
        # Search for the item
        page.fill("input[aria-label='Search Walmart.com']", item_name)
        page.press("input[aria-label='Search Walmart.com']", "Enter")
        page.wait_for_timeout(3000)
        
        try:
            # Click the first result (CSS selector may require fine-tuning)
            page.click("a[data-item-id]:nth-of-type(1)")
            page.wait_for_timeout(2000)

            # Click "Add to cart" button
            page.click("button:has-text('Add to cart')")
            logger.success(f"✅ Added '{item_name}' to cart!")
        except Exception as e:
            logger.error(f"⚠️ Could not add '{item_name}': {e}")
        
        # Optional: take screenshot
        screenshot_path = f"{item_name.replace(' ', '_')}.png"
        page.screenshot(path=screenshot_path)
        logger.debug(f"📸 Screenshot saved: {screenshot_path}")
        
        browser.close()

# Your grocery list
grocery_list = ["avocado", "extra firm tofu", "grape tomatoes"]

# Add each item to cart
for item in grocery_list:
    add_item_to_cart(item)
